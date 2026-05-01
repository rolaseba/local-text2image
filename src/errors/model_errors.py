"""Model-related exception classes."""

from src.errors.base import ModelError


class ModelNotFoundError(ModelError):
    def __init__(self, model_name: str):
        message = f"Model '{model_name}' not found in /models."
        guidance = (
            f"Run 'text2image download {model_name}' first to download the model."
        )
        super().__init__(message, guidance)


class ModelDownloadError(ModelError):
    def __init__(self, model_name: str):
        message = f"Failed to download model '{model_name}'."
        guidance = "Check your internet connection and try again."
        super().__init__(message, guidance)


class ModelLoadError(ModelError):
    def __init__(self, reason: str = "unknown"):
        message = f"Failed to load model. {reason}"
        guidance = "Your GPU may not have enough memory. Try closing other GPU applications or use a smaller model."
        super().__init__(message, guidance)


class ModelValidationError(ModelError):
    def __init__(
        self, model_name: str, missing_files: list = None, corrupted_files: list = None
    ):
        parts = []
        if missing_files:
            parts.append(f"Missing files: {', '.join(missing_files)}")
        if corrupted_files:
            parts.append(f"Corrupted files: {', '.join(corrupted_files)}")

        message = f"Model '{model_name}' validation failed. {'; '.join(parts)}"
        guidance = (
            "Try re-downloading the model using 'text2image download <model-name>'"
        )
        super().__init__(message, guidance)
