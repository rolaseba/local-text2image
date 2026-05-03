"""CLI entry point for text-2-image."""

import random
import click
from pathlib import Path
from typing import Optional, Dict, Any, Callable, Tuple

from src.utils.console import (
    console,
    print_info,
    print_success,
    print_error,
    print_header,
)
from src.utils.progress import progress
from src.models import downloader
from src.models.factory import create_model_loader, list_supported_models
from src.models.validator import is_model_valid, validate_model_or_raise
from src.config import load_config
from src.output import save_image
from src.validation import validate_all_components, get_validation_summary, validate_gpu
from src.utils.device import select_device
from src.utils.env import load_dotenv
from src.errors import (
    ModelDownloadError,
    ConfigError,
    ModelLoadError,
    ModelNotFoundError,
    ImageSaveError,
    InsufficientMemoryError,
    CudaNotAvailableError,
)


__version__ = "0.1.0"


def create_progress_manager():
    """Create a progress manager for multi-tiered generation progress."""
    state = {
        "overall_task": None,
        "step_task": None,
        "batch_size": 1,
        "current_batch": 0,
    }

    def callback(message: str, value: float = 0.0, total: Optional[int] = None):
        if state["overall_task"] is None:
            progress.start()
            state["overall_task"] = progress.add_task(
                "[cyan]Overall Progress", total=100
            )

        # If 'total' is provided, it's a step-based update (Generation phase)
        if total is not None:
            # Update overall bar to 'Generating' state
            # Progress is (batch_idx / batch_size) * 100 + (current_step / total_steps) * 20
            batch_progress = (state["current_batch"] / state["batch_size"]) * 100
            step_progress = (value / total) * 20 if total > 0 else 0

            progress.update(
                state["overall_task"],
                completed=int(batch_progress + step_progress),
                description=f"[cyan]Generating image {state['current_batch'] + 1}/{state['batch_size']}...",
            )

            # Manage the detailed step bar
            if state["step_task"] is None:
                state["step_task"] = progress.add_task(
                    "[magenta]Denoising", total=total
                )

            progress.update(state["step_task"], completed=value, description=message)
        else:
            # Update the overall bar (Loading phase)
            progress.update(
                state["overall_task"], completed=int(value * 100), description=message
            )

    return callback, state


@click.group()
@click.version_option(version=__version__)
def cli():
    """text2image - Local text-to-image generation CLI."""
    pass


@cli.command()
@click.option(
    "--batch", "-b", type=int, help="Number of images to generate in this batch"
)
def generate(batch):
    """Generate an image from configuration."""
    try:
        print_info("Loading configuration...")
        config = load_config()

        print_info("Checking compute device availability...")
        validate_gpu(config.get("device", "auto"), min_free_percent=20.0)
        device_selection = select_device(config.get("device", "auto"))
        print_info(f"Using compute device: {device_selection.name}")
        if device_selection.warning:
            print_info(device_selection.warning)

        # Use CLI batch option if provided, otherwise use config.yaml
        batch_size = batch if batch is not None else config.get("batch_size", 1)

        if batch_size < 1:
            print_error("Batch size must be at least 1.")
            raise click.Abort()

        model_name = config.get("model")
        prompt = config.get("prompt")

        print_info(f"Using model: {model_name}")
        print_info(
            f"Prompt: {prompt[:50]}..." if len(prompt) > 50 else f"Prompt: {prompt}"
        )

        print_info("Validating model...")
        models_dir = downloader.get_models_dir()
        model_path = models_dir / model_name

        if not model_path.exists():
            print_error(
                f"Model '{model_name}' not found. Run 'text2image download {model_name}' first."
            )
            raise click.Abort()

        if not is_model_valid(model_name):
            print_error(
                f"Model '{model_name}' is incomplete or corrupted. Run 'text2image download {model_name}' to re-download."
            )
            raise click.Abort()

        print_success("Model validated successfully")

        progress_callback, prog_state = create_progress_manager()
        prog_state["batch_size"] = batch_size

        loader = create_model_loader(
            model_name, model_path, validate=False, progress_callback=progress_callback
        )

        print_info("Loading model...")
        loader.load(device=config.get("device", "auto"))

        print_info("Generating image...")

        # Generate requested number of images
        generated_files = []
        for i in range(batch_size):
            prog_state["current_batch"] = i

            # Use a random seed for each image in the batch for diversity
            # unless a specific seed is provided in config
            seed = config.get("seed")
            if seed is None:
                seed = random.randint(0, 2**32 - 1)

            image = loader.generate(
                prompt=config.get("prompt"),
                negative_prompt=config.get("negative_prompt", ""),
                width=config.get("width", 1024),
                height=config.get("height", 1024),
                num_inference_steps=config.get("num_inference_steps", 28),
                guidance_scale=config.get("guidance_scale", 3.5),
                seed=seed,
            )

            output_dir = config.get("output_dir", "output")
            output_path = save_image(
                image=image,
                output_dir=output_dir,
                prompt=config.get("prompt"),
            )
            generated_files.append(output_path)

        # Stop progress before returning
        progress.stop()

        print_success(f"Successfully generated {len(generated_files)} image(s).")
        for path in generated_files:
            print_info(f" -> {path}")

        return generated_files

    except ConfigError as e:
        print_error(str(e))
        raise click.Abort()
    except CudaNotAvailableError as e:
        print_error(str(e))
        raise click.Abort()
    except InsufficientMemoryError as e:
        print_error(str(e))
        raise click.Abort()
    except ImageSaveError as e:
        print_error(str(e))
        raise click.Abort()
    except ModelNotFoundError as e:
        print_error(str(e))
        print_info("Run 'text2image download <model-name>' to download a model first.")
        raise click.Abort()
    except ModelLoadError as e:
        print_error(str(e))
        raise click.Abort()
    except Exception as e:
        print_error(f"Generation failed: {e}")
        raise click.Abort()


@cli.command()
@click.argument("model_name")
def download(model_name):
    """Download a model by name."""
    try:
        load_dotenv()
        model_path = downloader.download_model(model_name)
        print_success(f"Model '{model_name}' downloaded to: {model_path}")
    except ModelDownloadError as e:
        print_error(str(e))
        raise click.Abort()


@cli.command()
def list_models():
    """List available models and their integrity status."""
    print_header("Model Integrity Report")

    models_dir = downloader.get_models_dir()
    supported_models = list_supported_models()

    # Define the path to model constraint configs
    constraints_dir = Path.cwd() / "config" / "models"

    found_any = False
    for model in supported_models:
        found_any = True
        model_path = models_dir / model
        config_path = constraints_dir / f"{model}.yaml"

        weights_ok = model_path.exists() and any(
            f.suffix in [".safetensors", ".bin", ".pt"]
            for f in model_path.iterdir()
            if f.is_file()
        )
        config_ok = config_path.exists()

        status = (
            "[green]OK[/green]"
            if weights_ok and config_ok
            else "[yellow]PARTIAL[/yellow]"
        )
        if not weights_ok and not config_ok:
            status = "[red]MISSING[/red]"
        elif not weights_ok:
            status = "[yellow]NOT DOWNLOADED[/yellow]"
        elif not config_ok:
            status = "[red]CONFIG MISSING[/red]"

        weights_icon = "✅" if weights_ok else "❌"
        config_icon = "✅" if config_ok else "❌"

        console.print(
            f" - {model} {status} (Weights: {weights_icon} Config: {config_icon})"
        )

    if not found_any:
        print_info("No supported models identified.")


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
