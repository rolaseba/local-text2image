"""Output-related exception classes."""

from src.errors.base import Text2ImageError


class ImageSaveError(Text2ImageError):
    def __init__(self, reason: str):
        message = f"Failed to save image. {reason}"
        guidance = "Check that the output directory is writable."
        super().__init__(message, guidance)
