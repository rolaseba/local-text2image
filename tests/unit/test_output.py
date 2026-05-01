"""Unit tests for output module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
from datetime import datetime
from PIL import Image

from src.output import (
    ensure_output_dir,
    generate_filename,
    save_image,
    get_output_path,
    ImageSaveError,
)


class TestEnsureOutputDir:
    """Tests for ensure_output_dir function."""

    def test_ensure_output_dir_creates_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = ensure_output_dir(tmpdir)
            assert output_path.exists()
            assert output_path.is_dir()

    def test_ensure_output_dir_creates_nested_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            nested = str(Path(tmpdir) / "nested" / "path")
            output_path = ensure_output_dir(nested)
            assert output_path.exists()
            assert output_path.is_dir()


class TestGenerateFilename:
    """Tests for generate_filename function."""

    def test_generate_filename_default(self):
        filename = generate_filename("test prompt")
        assert filename.endswith(".png")
        assert "test prompt" not in filename

    def test_generate_filename_with_format(self):
        filename = generate_filename("test", output_format="jpg")
        assert filename.endswith(".jpg")

    def test_generate_filename_with_timestamp(self):
        ts = datetime(2026, 4, 6, 12, 0, 0)
        filename = generate_filename("test", timestamp=ts)
        assert "20260406_120000" in filename


class TestSaveImage:
    """Tests for save_image function."""

    def test_save_image_success(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            image = Image.new("RGB", (100, 100), color="red")
            output_path = save_image(
                image=image,
                output_dir=tmpdir,
                prompt="test prompt",
            )

            assert output_path.exists()
            assert output_path.parent == Path(tmpdir)

    def test_save_image_custom_filename(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            image = Image.new("RGB", (100, 100), color="red")
            output_path = save_image(
                image=image,
                output_dir=tmpdir,
                prompt="test",
                filename="custom_name.png",
            )

            assert output_path.name == "custom_name.png"

    def test_save_image_jpeg_format(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            image = Image.new("RGB", (100, 100), color="red")
            output_path = save_image(
                image=image,
                output_dir=tmpdir,
                prompt="test",
                output_format="jpeg",
            )

            assert output_path.name.endswith(".jpeg")


class TestGetOutputPath:
    """Tests for get_output_path function."""

    def test_get_output_path(self):
        path = get_output_path("output", "image.png")
        assert path == Path("output") / "image.png"
