"""Model validation utilities for text2image."""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from src.errors.model_errors import ModelValidationError
from src.errors import ModelNotFoundError
from src.models.downloader import get_models_dir, get_model_id


FLUX_REQUIRED_FILES = [
    "model.safetensors",
    "config.json",
]

FLUX_OPTIONAL_FILES = [
    "tokenizer.json",
    "tokenizer_config.json",
    "diffusion_pytorch_model.safetensors",
]

MIN_VALID_FILE_SIZE = 1
MIN_VALID_JSON_SIZE = 1000


@dataclass(frozen=True)
class ValidationResult:
    """Result of model validation."""

    is_valid: bool
    model_name: str
    missing_files: list = None
    corrupted_files: list = None
    extra_files: list = None

    def __post_init__(self):
        if self.missing_files is None:
            object.__setattr__(self, "missing_files", [])
        if self.corrupted_files is None:
            object.__setattr__(self, "corrupted_files", [])
        if self.extra_files is None:
            object.__setattr__(self, "extra_files", [])


def get_model_config(model_name: str) -> dict:
    """Get the required files for a specific model.

    Args:
        model_name: Name of the model

    Returns:
        Dictionary with 'required' and 'optional' file lists
    """
    config = {
        "flux-schnell": {
            "required": FLUX_REQUIRED_FILES,
            "optional": FLUX_OPTIONAL_FILES,
        },
        "flux-dev": {
            "required": FLUX_REQUIRED_FILES,
            "optional": FLUX_OPTIONAL_FILES,
        },
    }

    resolved_id = get_model_id(model_name)
    short_name = model_name

    for key in config:
        if key in model_name or key in resolved_id:
            short_name = key
            break

    return config.get(
        short_name,
        {
            "required": FLUX_REQUIRED_FILES,
            "optional": FLUX_OPTIONAL_FILES,
        },
    )


def _find_file_in_model(model_path: Path, filename: str) -> Optional[Path]:
    """Find a file in model directory or subdirectories.

    Args:
        model_path: Root path of the model
        filename: File name to search for

    Returns:
        Path to file if found, None otherwise
    """
    if (model_path / filename).exists():
        return model_path / filename

    for subdir in model_path.iterdir():
        if subdir.is_dir():
            if (subdir / filename).exists():
                return subdir / filename
    return None


def validate_model(model_name: str) -> ValidationResult:
    """Validate that a model has all required files.

    Args:
        model_name: Name of the model to validate

    Returns:
        ValidationResult with validation status

    Raises:
        ModelNotFoundError: If model directory doesn't exist
    """
    model_path = get_models_dir() / model_name

    if not model_path.exists():
        raise ModelNotFoundError(model_name)

    try:
        if not any(model_path.iterdir()):
            raise ModelNotFoundError(model_name)
    except OSError:
        raise ModelNotFoundError(model_name)

    config = get_model_config(model_name)
    required_files = config["required"]
    optional_files = config["optional"]

    model_files = set()
    for f in model_path.rglob("*"):
        if f.is_file():
            model_files.add(f.name)

    missing = []
    for req_file in required_files:
        file_path = _find_file_in_model(model_path, req_file)
        if file_path is None:
            missing.append(req_file)
        elif file_path.stat().st_size < MIN_VALID_FILE_SIZE:
            missing.append(f"{req_file} (empty)")

    corrupted = []
    for req_file in required_files:
        file_path = _find_file_in_model(model_path, req_file)
        if file_path and file_path.stat().st_size < MIN_VALID_JSON_SIZE:
            if req_file.endswith(".json"):
                try:
                    import json

                    with open(file_path) as f:
                        json.load(f)
                except json.JSONDecodeError:
                    corrupted.append(req_file)

    extra = [
        f for f in model_files if f not in required_files and f not in optional_files
    ]

    is_valid = len(missing) == 0 and len(corrupted) == 0

    return ValidationResult(
        is_valid=is_valid,
        model_name=model_name,
        missing_files=missing,
        corrupted_files=corrupted,
        extra_files=extra,
    )


def validate_model_or_raise(model_name: str) -> ValidationResult:
    """Validate model and raise exception if invalid.

    Args:
        model_name: Name of the model to validate

    Returns:
        ValidationResult if valid

    Raises:
        ModelNotFoundError: If model directory doesn't exist
        ModelValidationError: If validation fails
    """
    result = validate_model(model_name)

    if not result.is_valid:
        raise ModelValidationError(
            model_name=model_name,
            missing_files=result.missing_files,
            corrupted_files=result.corrupted_files,
        )

    return result


def is_model_valid(model_name: str) -> bool:
    """Quick check if model is valid without raising exceptions.

    Args:
        model_name: Name of the model to check

    Returns:
        True if model is valid, False otherwise
    """
    try:
        result = validate_model(model_name)
        return result.is_valid
    except (ModelNotFoundError, ModelValidationError):
        return False
