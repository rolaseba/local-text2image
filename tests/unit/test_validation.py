"""Unit tests for validation module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from types import SimpleNamespace
import tempfile

from src.validation import (
    ValidationResult,
    check_gpu_availability,
    validate_all_components,
    get_validation_summary,
)


class TestValidateAllComponents:
    """Tests for validate_all_components function."""

    @patch("src.validation.load_config")
    def test_validate_config_error(self, mock_config):
        from src.errors import ConfigError

        mock_config.side_effect = ConfigError("Invalid config", guidance="Fix it")

        result = validate_all_components()

        assert result.is_valid is False
        assert len(result.errors) > 0

    @patch("src.validation.load_config")
    @patch("src.validation.downloader")
    def test_validate_model_not_found(self, mock_dl, mock_config):
        mock_config.return_value = {
            "model": "flux-schnell",
            "prompt": "test",
            "output_dir": "output",
        }

        mock_dl.get_models_dir.return_value = Path("/nonexistent")

        result = validate_all_components()

        assert result.is_valid is False
        assert any("not found" in e.lower() for e in result.errors)

    @patch("src.validation.load_config")
    @patch("src.validation.downloader")
    @patch("src.validation.is_model_valid")
    def test_validate_success(self, mock_valid, mock_dl, mock_config):
        mock_config.return_value = {
            "model": "flux-schnell",
            "prompt": "test",
            "output_dir": "output",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_models_dir = Path(tmpdir)
            mock_model_path = mock_models_dir / "flux-schnell"
            mock_model_path.mkdir()

            mock_dl.get_models_dir.return_value = mock_models_dir
            mock_valid.return_value = True

            result = validate_all_components()

            assert result.is_valid is True


class TestCheckGpuAvailability:
    @patch("src.validation.select_device")
    def test_cpu_is_available_with_slow_message(self, mock_select):
        mock_select.return_value = SimpleNamespace(name="cpu")

        is_available, message = check_gpu_availability("cpu")

        assert is_available is True
        assert "slow" in message

    @patch("src.validation.select_device")
    def test_unavailable_device_returns_error(self, mock_select):
        mock_select.side_effect = RuntimeError("Requested device 'cuda' is not available")

        is_available, message = check_gpu_availability("cuda")

        assert is_available is False
        assert "not available" in message


class TestGetValidationSummary:
    """Tests for get_validation_summary function."""

    def test_summary_valid(self):
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        summary = get_validation_summary(result)
        assert "successfully" in summary.lower()

    def test_summary_invalid(self):
        result = ValidationResult(
            is_valid=False, errors=["Error 1", "Error 2"], warnings=[]
        )
        summary = get_validation_summary(result)
        assert "failed" in summary.lower()
        assert "Error 1" in summary
