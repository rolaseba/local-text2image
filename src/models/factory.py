"""Model factory for creating model loaders."""

from pathlib import Path
from typing import Dict, Type, Optional

from src.errors import ModelNotFoundError, ModelValidationError


MODEL_REGISTRY: Dict[str, Type] = {}
_registered = False


def register_model(model_type: str, loader_class: Type) -> None:
    """Register a model loader class.

    Args:
        model_type: Model type identifier (e.g., 'flux', 'sdxl')
        loader_class: Model loader class
    """
    MODEL_REGISTRY[model_type] = loader_class


def _ensure_registered():
    """Ensure model loaders are registered."""
    global _registered
    if _registered:
        return

    from src.generation.flux import FluxModelLoader

    register_model("flux", FluxModelLoader)
    _registered = True


def create_model_loader(
    model_name: str,
    model_path: Path,
    validate: bool = True,
    progress_callback: callable = None,
):
    """Create a model loader for the specified model.

    Args:
        model_name: Name of the model
        model_path: Path to the model files
        validate: Whether to validate model files before loading
        progress_callback: Optional callback for progress updates

    Returns:
        ModelLoader instance

    Raises:
        ModelNotFoundError: If model type is not supported
        ModelValidationError: If model validation fails
    """
    _ensure_registered()

    from src.models.validator import validate_model_or_raise

    if validate:
        validate_model_or_raise(model_name)

    model_type = _get_model_type(model_name)

    if model_type not in MODEL_REGISTRY:
        available = ", ".join(MODEL_REGISTRY.keys()) or "none"
        raise ModelNotFoundError(
            f"Model type '{model_type}' not supported. Available models: {available}"
        )

    return MODEL_REGISTRY[model_type](model_name, model_path, progress_callback)


def _get_model_type(model_name: str) -> str:
    """Extract model type from model name.

    Args:
        model_name: Full model name

    Returns:
        Model type identifier
    """
    name_lower = model_name.lower()
    if "flux" in name_lower:
        return "flux"
    elif "sdxl" in name_lower:
        return "sdxl"
    elif "sd" in name_lower and "sdxl" not in name_lower:
        return "sd"
    return model_name


def list_supported_models() -> list:
    """Get list of supported model types."""
    _ensure_registered()
    return list(MODEL_REGISTRY.keys())
