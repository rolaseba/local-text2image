"""Image output management for text2image."""

import hashlib
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
from PIL import Image

from src.errors.output_errors import ImageSaveError


def ensure_output_dir(output_dir: str) -> Path:
    """Ensure output directory exists.

    Args:
        output_dir: Path to output directory

    Returns:
        Path object for output directory
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def generate_filename(
    prompt: str,
    output_format: str = "png",
    timestamp: Optional[datetime] = None,
) -> str:
    """Generate filename for output image.

    Args:
        prompt: Generation prompt
        output_format: Image format (png, jpg, etc.)
        timestamp: Optional timestamp (defaults to now)

    Returns:
        Generated filename
    """
    if timestamp is None:
        timestamp = datetime.now()

    ts_str = timestamp.strftime("%Y%m%d_%H%M%S")
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:8]

    return f"{ts_str}_{prompt_hash}.{output_format}"


def save_image(
    image: Image.Image,
    output_dir: str,
    prompt: str,
    filename: Optional[str] = None,
    output_format: str = "png",
) -> Path:
    """Save generated image to output directory.

    Args:
        image: PIL Image object to save
        output_dir: Output directory path
        prompt: Generation prompt (for filename)
        filename: Optional custom filename
        output_format: Image format (png, jpg, etc.)

    Returns:
        Path to saved image

    Raises:
        ImageSaveError: If save fails
    """
    try:
        output_path = ensure_output_dir(output_dir)

        if filename is None:
            filename = generate_filename(prompt, output_format)

        filepath = output_path / filename

        if output_format.lower() in ["jpg", "jpeg"]:
            image.save(filepath, "JPEG", quality=95)
        else:
            image.save(filepath, "PNG")

        return filepath

    except OSError as e:
        raise ImageSaveError(f"OS error: {e}")
    except (ValueError, KeyError) as e:
        raise ImageSaveError(f"Invalid image or format: {e}")


def get_output_path(output_dir: str, filename: str) -> Path:
    """Get full output path.

    Args:
        output_dir: Output directory
        filename: Filename

    Returns:
        Full path to output file
    """
    return Path(output_dir) / filename
