"""FLUX model loader implementation."""

import os

os.environ["DIFFUSERS_DISABLE_PROGRESS_BARS"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import logging
import sys
import io

logging.getLogger("diffusers").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("tqdm").setLevel(logging.ERROR)

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Callable
import torch

from src.errors import ModelLoadError
from src.utils.console import print_info, print_success
from src.utils.console import console
from src.utils.device import select_device


class SuppressProgress:
    """Context manager to suppress progress bar output."""

    def __enter__(self):
        self._old_stderr = sys.stderr
        sys.stderr = io.StringIO()
        return self

    def __exit__(self, *args):
        sys.stderr = self._old_stderr


class BaseModelLoader(ABC):
    """Abstract base class for model loaders."""

    def __init__(self, model_name: str, model_path: Path):
        self.model_name = model_name
        self.model_path = model_path
        self._model = None

    @abstractmethod
    def load(self, device: str = "auto") -> None:
        pass

    @abstractmethod
    def generate(self, prompt: str, **kwargs):
        pass

    @abstractmethod
    def get_memory_requirement(self) -> int:
        pass

    def unload(self) -> None:
        self._model = None

    def is_loaded(self) -> bool:
        return self._pipeline is not None


class FluxModelLoader(BaseModelLoader):
    """Model loader for FLUX text-to-image models."""

    def __init__(
        self,
        model_name: str,
        model_path: Path,
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ):
        """Initialize FLUX model loader.

        Args:
            model_name: Name of the model
            model_path: Path to the model files
            progress_callback: Optional callback for progress updates
        """
        super().__init__(model_name, model_path)
        self.progress_callback = progress_callback
        self._pipeline = None
        self._device = None
        self._device_selection = None

    def load(self, device: str = "auto") -> None:
        """Load the FLUX model into memory.

        Raises:
            ModelLoadError: If model loading fails
        """
        try:
            self._report_progress("Loading model...", 0.0)

            self._device = self._get_device(device)
            self._report_progress(f"Using device: {self._device}", 0.1)

            from diffusers import FluxPipeline

            self._report_progress("Loading model files...", 0.2)

            with SuppressProgress():
                self._pipeline = FluxPipeline.from_pretrained(
                    str(self.model_path),
                    torch_dtype=torch.float16
                    if self._device.type == "cuda"
                    else torch.float32,
                    low_cpu_mem_usage=True,
                )

            self._pipeline.set_progress_bar_config(disable=True)

            self._report_progress("Applying memory optimization...", 0.5)

            if self._device.type == "cuda" and hasattr(
                self._pipeline, "enable_sequential_cpu_offload"
            ):
                self._pipeline.enable_sequential_cpu_offload()
            elif self._device.type == "cuda" and hasattr(
                self._pipeline, "enable_model_cpu_offload"
            ):
                self._pipeline.enable_model_cpu_offload()
            else:
                self._pipeline.to(self._device)

            self._report_progress("Model loaded successfully!", 1.0)

            # Force a newline before the success message to avoid merging with the progress bar
            from src.utils.console import console

            console.print("\n")

            print_success(f"Model '{self.model_name}' loaded successfully")

        except Exception as e:
            raise ModelLoadError(str(e))

    def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        num_inference_steps: int = 28,
        guidance_scale: float = 3.5,
        seed: Optional[int] = None,
        **kwargs,
    ) -> str:
        """Generate an image from a text prompt.

        Args:
            prompt: Text prompt for generation
            negative_prompt: Negative prompt to avoid
            width: Image width
            height: Image height
            num_inference_steps: Number of denoising steps
            guidance_scale: Guidance scale for generation
            seed: Random seed for reproducibility
            **kwargs: Additional generation parameters

        Returns:
            Path to generated image

        Raises:
            ModelLoadError: If model is not loaded
        """
        if not self.is_loaded():
            raise ModelLoadError("Model not loaded. Call load() first.")

        generator = None
        if seed is not None:
            generator_device = self._device if self._device.type == "cuda" else "cpu"
            generator = torch.Generator(device=generator_device).manual_seed(seed)

        self._report_progress("Generating image...", 0.0)

        step_counter = {"current": 0}

        def progress_callback(pipeline, step, timestep, kwargs):
            step_counter["current"] = step + 1

            if self.progress_callback:
                # Pass current step and total steps to the callback
                self.progress_callback(
                    f"Denoising step {step_counter['current']}/{num_inference_steps}",
                    step_counter["current"],
                    num_inference_steps,
                )

            return {}

        with torch.inference_mode():
            result = self._pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator,
                callback_on_step_end=progress_callback,
                callback_on_step_end_tensor_inputs=["latents"],
                **kwargs,
            )

        self._report_progress("Generation complete!", 1.0)

        return result.images[0]

    def get_memory_requirement(self) -> int:
        """Get estimated VRAM requirement in GB.

        Returns:
            Required VRAM in gigabytes
        """
        model_configs = {
            "flux-schnell": 4,
            "flux-dev": 8,
        }
        return model_configs.get(self.model_name, 4)

    def unload(self) -> None:
        """Unload model from memory."""
        if self._pipeline is not None:
            del self._pipeline
            self._pipeline = None

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        self._model = None
        print_info("Model unloaded from memory")

    def get_memory_usage(self) -> dict:
        """Get current memory usage.

        Returns:
            Dictionary with memory usage information
        """
        usage = {"allocated": 0, "reserved": 0}

        if torch.cuda.is_available():
            usage["allocated"] = torch.cuda.memory_allocated() / (1024**3)
            usage["reserved"] = torch.cuda.memory_reserved() / (1024**3)

        return usage

    def _get_device(self, requested_device: str = "auto") -> torch.device:
        """Get the device to use for inference.

        Returns:
            torch.device object
        """
        self._device_selection = select_device(requested_device)
        return torch.device(self._device_selection.name)

    def _report_progress(self, message: str, progress: float) -> None:
        """Report progress through callback.

        Args:
            message: Progress message
            progress: Progress value (0.0 to 1.0)
        """
        if self.progress_callback:
            # For loading phase, use the 0.0-1.0 float as the progress value
            self.progress_callback(message, progress)
