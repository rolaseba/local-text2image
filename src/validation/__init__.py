"""Pre-flight validation for text2image generation."""

from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

from src.config import load_config
from src.models.validator import is_model_valid
from src.models import downloader
from src.errors.hardware_errors import CudaNotAvailableError, InsufficientMemoryError
from src.utils.device import select_device


@dataclass
class ValidationResult:
    """Result of pre-flight validation."""

    is_valid: bool
    errors: List[str]
    warnings: List[str]

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


def check_gpu_availability(
    device: str = "auto", min_free_percent: float = 20.0
) -> tuple[bool, str]:
    """Check if the requested compute device is available.

    Args:
        device: Requested device option
        min_free_percent: Minimum percentage of free VRAM required (default 20%)

    Returns:
        Tuple of (is_available, message)
    """
    try:
        import torch
        import subprocess

        selection = select_device(device)

        if selection.name == "cpu":
            return True, "CPU available. Generation will be very slow."

        if selection.name != "cuda":
            return True, f"{selection.name.upper()} available (experimental backend)"

        gpu_count = torch.cuda.device_count()
        if gpu_count == 0:
            return False, "No CUDA devices found."

        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=memory.used,memory.total",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                return (
                    True,
                    "GPU available (nvidia-smi not accessible for memory check)",
                )

            lines = result.stdout.strip().split("\n")
            if not lines:
                return True, "GPU available"

            used_mb, total_mb = map(int, lines[0].split(","))
            used_percent = (used_mb / total_mb) * 100
            free_percent = 100 - used_percent

            if free_percent < min_free_percent:
                return (
                    False,
                    f"GPU memory low: {free_percent:.1f}% free ({used_mb}/{total_mb} MB used). Close other GPU applications.",
                )

            return (
                True,
                f"GPU available: {free_percent:.1f}% free ({total_mb} MB total)",
            )

        except FileNotFoundError:
            return True, "GPU available (nvidia-smi not found)"

    except (ImportError, RuntimeError) as e:
        return False, str(e)


def validate_gpu(device: str = "auto", min_free_percent: float = 20.0) -> None:
    """Validate compute device availability and raise exception if not sufficient.

    Args:
        device: Requested device option
        min_free_percent: Minimum percentage of free VRAM required

    Raises:
        CudaNotAvailableError: If CUDA is not available
        InsufficientMemoryError: If not enough free VRAM
    """
    is_available, message = check_gpu_availability(device, min_free_percent)

    if not is_available:
        if "cuda" in message.lower():
            raise CudaNotAvailableError()
        elif "memory low" in message:
            raise InsufficientMemoryError("VRAM")
        else:
            raise CudaNotAvailableError()


def validate_all_components() -> ValidationResult:
    """Validate all components needed for generation.

    Returns:
        ValidationResult with validation status and any errors/warnings
    """
    errors = []
    warnings = []

    try:
        config = load_config()
    except Exception as e:
        errors.append(f"Config error: {str(e)}")
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    model_name = config.get("model")
    output_dir = config.get("output_dir", "output")

    if not model_name:
        errors.append("No model specified in config")
    else:
        models_dir = downloader.get_models_dir()
        model_path = models_dir / model_name

        if not model_path.exists():
            errors.append(
                f"Model '{model_name}' not found. Run 'text2image download {model_name}' first."
            )
        elif not is_model_valid(model_name):
            errors.append(
                f"Model '{model_name}' is incomplete or corrupted. Re-download required."
            )

    output_path = Path(output_dir)
    if output_path.exists() and not output_path.is_dir():
        errors.append(f"Output directory '{output_dir}' is not a valid directory")

    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        errors.append(f"Cannot create output directory: {str(e)}")

    is_valid = len(errors) == 0

    return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)


def get_validation_summary(result: ValidationResult) -> str:
    """Get human-readable validation summary.

    Args:
        result: ValidationResult from validate_all_components()

    Returns:
        Formatted string with validation results
    """
    if result.is_valid:
        return "All components validated successfully"

    lines = ["Pre-flight validation failed:"]
    for error in result.errors:
        lines.append(f"  - {error}")

    return "\n".join(lines)
