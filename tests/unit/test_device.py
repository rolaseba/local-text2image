"""Unit tests for device selection helpers."""

from unittest.mock import Mock, patch

import pytest

from src.utils.device import normalize_device_option, select_device


class TestNormalizeDeviceOption:
    def test_defaults_to_auto(self):
        assert normalize_device_option(None) == "auto"

    def test_normalizes_case_and_whitespace(self):
        assert normalize_device_option(" CUDA ") == "cuda"

    def test_rejects_unknown_device(self):
        with pytest.raises(ValueError):
            normalize_device_option("vulkan")


class TestSelectDevice:
    @patch("torch.cuda.is_available", return_value=True)
    def test_auto_prefers_cuda(self, mock_cuda):
        selection = select_device("auto")

        assert selection.name == "cuda"
        assert selection.is_accelerated is True

    @patch("torch.cuda.is_available", return_value=False)
    def test_auto_falls_back_to_cpu(self, mock_cuda):
        selection = select_device("auto")

        assert selection.name == "cpu"
        assert selection.is_accelerated is False
        assert "slow" in selection.warning

    @patch("torch.cuda.is_available", return_value=False)
    def test_unavailable_requested_device_raises(self, mock_cuda):
        with pytest.raises(RuntimeError):
            select_device("cuda")
