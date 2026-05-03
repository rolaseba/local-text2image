"""Model factory for creating model loaders."""

from pathlib import Path
from typing import Dict, Type

from src.errors import ModelNotFoundError, ModelValidationError


SUPPORTED_MODEL_NAMES = ["flux-schnell", "flux-dev"]


class ModelFactory:
    """Factory for creating model loaders with encapsulated registry."""

    _registry: Dict[str, Type] = {}
    _initialized = False

    @classmethod
    def register(cls, model_type: str, loader_class: Type) -> None:
        """Register a model loader class.

        Args:
            model_type: Model type identifier (e.g., 'flux', 'sdxl')
            loader_class: Model loader class
        """
        cls._registry[model_type] = loader_class

    @classmethod
    def _ensure_initialized(cls) -> None:
        """Ensure model loaders are registered (called once)."""
        if cls._initialized:
            return

        from src.generation.flux import FluxModelLoader

        cls.register("flux", FluxModelLoader)
        cls._initialized = True

    @classmethod
    def create(
        cls,
        model_name: str,
        model_path: Path,
        validate: bool = True,
        progress_callback=None,
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
        cls._ensure_initialized()

        from src.models.validator import validate_model_or_raise

        if validate:
            validate_model_or_raise(model_name)

        model_type = cls._get_model_type(model_name)

        if model_type not in cls._registry:
            available = ", ".join(cls._registry.keys()) or "none"
            raise ModelNotFoundError(
                f"Model type '{model_type}' not supported. Available models: {available}"
            )

        return cls._registry[model_type](model_name, model_path, progress_callback)

    @classmethod
    def _get_model_type(cls, model_name: str) -> str:
        """Extract model type from model name.

        Uses prefix matching to avoid false positives (e.g., "my-flux-model"
        incorrectly matching as "flux").

        Args:
            model_name: Full model name

        Returns:
            Model type identifier
        """
        name_lower = model_name.lower()
        if name_lower.startswith("flux"):
            return "flux"
        if name_lower.startswith("sdxl"):
            return "sdxl"
        if name_lower.startswith("sd") and not name_lower.startswith("sdxl"):
            return "sd"
        return model_name

    @classmethod
    def list_supported(cls) -> list:
        """Get list of supported model names."""
        cls._ensure_initialized()
        return SUPPORTED_MODEL_NAMES

    @classmethod
    def is_supported(cls, model_name: str) -> bool:
        """Check if a model name is supported."""
        return model_name in SUPPORTED_MODEL_NAMES


def register_model(model_type: str, loader_class: Type) -> None:
    """Register a model loader class.

    Args:
        model_type: Model type identifier (e.g., 'flux', 'sdxl')
        loader_class: Model loader class
    """
    ModelFactory.register(model_type, loader_class)


def _ensure_registered() -> None:
    """Ensure model loaders are registered."""
    ModelFactory._ensure_initialized()


def create_model_loader(
    model_name: str,
    model_path: Path,
    validate: bool = True,
    progress_callback=None,
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
    return ModelFactory.create(model_name, model_path, validate, progress_callback)


def _get_model_type(model_name: str) -> str:
    """Extract model type from model name.

    Args:
        model_name: Full model name

    Returns:
        Model type identifier
    """
    return ModelFactory._get_model_type(model_name)


def list_supported_models() -> list:
    """Get list of supported model names."""
    return ModelFactory.list_supported()


def is_model_supported(model_name: str) -> bool:
    """Check if a model name is supported."""
    return ModelFactory.is_supported(model_name)