"""Model downloader for text2image."""

import os
from pathlib import Path
from typing import Optional
from huggingface_hub import snapshot_download
from src.errors import ModelDownloadError
from src.utils.console import print_info, print_success, print_error
from src.utils.progress import progress


MODEL_SHORTCUTS = {
    "flux-schnell": "black-forest-labs/FLUX.1-schnell",
    "flux-dev": "black-forest-labs/FLUX.1-dev",
}


def get_model_id(model_name: str) -> str:
    """Resolve short model name to HuggingFace model ID."""
    if model_name in MODEL_SHORTCUTS:
        return MODEL_SHORTCUTS[model_name]
    return model_name


def get_models_dir() -> Path:
    """Get or create the models directory."""
    models_dir = Path("models")
    if not models_dir.exists():
        models_dir.mkdir(parents=True, exist_ok=True)
    return models_dir


def download_model(
    model_name: str,
    local_dir: Optional[str] = None,
) -> str:
    """Download a model from HuggingFace.

    Args:
        model_name: Model name or HuggingFace model ID
        local_dir: Optional local directory to save model

    Returns:
        Path to downloaded model

    Raises:
        ModelDownloadError: If download fails
    """
    model_id = get_model_id(model_name)

    if local_dir is None:
        local_dir = str(get_models_dir() / model_name)

    print_info(f"Downloading model: {model_name} ({model_id})...")

    try:
        local_path = snapshot_download(
            repo_id=model_id,
            local_dir=local_dir,
        )

        print_success(f"Model downloaded successfully to: {local_path}")
        return local_path

    except Exception as e:
        raise ModelDownloadError(f"{model_name}: {str(e)}")


def is_model_downloaded(model_name: str) -> bool:
    """Check if a model is already downloaded."""
    model_id = get_model_id(model_name)
    local_path = get_models_dir() / model_name
    return local_path.exists() and any(local_path.iterdir())


def get_model_path(model_name: str) -> Optional[Path]:
    """Get the path to a downloaded model."""
    local_path = get_models_dir() / model_name
    if local_path.exists() and any(local_path.iterdir()):
        return local_path
    return None
