"""Unit tests for FLUX model loader."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile

from src.generation.flux import FluxModelLoader
from src.errors import ModelLoadError


class TestFluxModelLoader:
    """Tests for FluxModelLoader class."""

    def test_init(self):
        loader = FluxModelLoader("flux-schnell", Path("/models/flux-schnell"))
        assert loader.model_name == "flux-schnell"
        assert loader.model_path == Path("/models/flux-schnell")
        assert loader.progress_callback is None

    def test_init_with_callback(self):
        callback = Mock()
        loader = FluxModelLoader(
            "flux-schnell", Path("/models/flux-schnell"), progress_callback=callback
        )
        assert loader.progress_callback == callback

    def test_is_loaded_false_initially(self):
        loader = FluxModelLoader("flux-schnell", Path("/models/flux-schnell"))
        assert loader.is_loaded() is False

    def test_get_memory_requirement_flux_schnell(self):
        loader = FluxModelLoader("flux-schnell", Path("/models/flux-schnell"))
        assert loader.get_memory_requirement() == 4

    def test_get_memory_requirement_flux_dev(self):
        loader = FluxModelLoader("flux-dev", Path("/models/flux-dev"))
        assert loader.get_memory_requirement() == 8

    def test_get_memory_requirement_unknown(self):
        loader = FluxModelLoader("unknown", Path("/models/unknown"))
        assert loader.get_memory_requirement() == 4

    def test_report_progress_with_callback(self):
        callback = Mock()
        loader = FluxModelLoader(
            "flux-schnell", Path("/models/flux-schnell"), progress_callback=callback
        )
        loader._report_progress("Test message", 0.5)
        callback.assert_called_once_with("Test message", 0.5)

    def test_report_progress_without_callback(self):
        loader = FluxModelLoader("flux-schnell", Path("/models/flux-schnell"))
        loader._report_progress("Test message", 0.5)

    def test_generate_without_load_raises(self):
        loader = FluxModelLoader("flux-schnell", Path("/models/flux-schnell"))

        with pytest.raises(ModelLoadError) as exc_info:
            loader.generate("test prompt")

        assert "not loaded" in str(exc_info.value).lower()

    def test_get_memory_usage(self):
        loader = FluxModelLoader("flux-schnell", Path("/models/flux-schnell"))
        usage = loader.get_memory_usage()

        assert "allocated" in usage
        assert "reserved" in usage

    def test_unload_clears_pipeline(self):
        loader = FluxModelLoader("flux-schnell", Path("/models/flux-schnell"))
        loader._pipeline = MagicMock()
        loader._model = MagicMock()

        loader.unload()

        assert loader._pipeline is None
        assert loader._model is None
