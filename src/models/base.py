"""Model loader base abstraction."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class ModelLoader(ABC):
    """Abstract base class for model loaders."""

    def __init__(self, model_name: str, model_path: Path):
        """Initialize model loader.

        Args:
            model_name: Name of the model
            model_path: Path to the model files
        """
        self.model_name = model_name
        self.model_path = model_path
        self._model = None

    @abstractmethod
    def load(self) -> None:
        """Load the model into memory."""
        pass

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate an image from a text prompt.

        Args:
            prompt: Text prompt for generation
            **kwargs: Additional generation parameters

        Returns:
            Path to generated image
        """
        pass

    @abstractmethod
    def get_memory_requirement(self) -> int:
        """Get estimated VRAM requirement in GB.

        Returns:
            Required VRAM in gigabytes
        """
        pass

    def unload(self) -> None:
        """Unload model from memory."""
        self._model = None

    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._model is not None
