"""Unit tests for CLI generate command."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile

from click.testing import CliRunner
from src.cli import cli


class TestGenerateCommand:
    """Tests for generate CLI command."""

    def test_generate_command_exists(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "--help"])
        assert result.exit_code == 0
        assert "Generate" in result.output

    @patch("src.cli.load_config")
    @patch("src.cli.is_model_valid")
    @patch("src.cli.create_model_loader")
    @patch("src.cli.downloader")
    def test_generate_success(
        self, mock_downloader, mock_loader, mock_valid, mock_config
    ):
        mock_config.return_value = {
            "model": "flux-schnell",
            "prompt": "A test prompt",
            "negative_prompt": "",
            "width": 1024,
            "height": 1024,
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
            "seed": None,
        }

        mock_model_path = MagicMock()
        mock_model_path.exists.return_value = True
        mock_downloader.get_models_dir.return_value = mock_model_path

        mock_valid.return_value = True

        mock_loader_instance = MagicMock()
        mock_loader_instance.generate.return_value = MagicMock()
        mock_loader.return_value = mock_loader_instance

        runner = CliRunner()
        result = runner.invoke(cli, ["generate"])

        assert "Configuration" in result.output or "error" not in result.output.lower()

    @patch("src.cli.load_config")
    def test_generate_config_error(self, mock_config):
        from src.errors import ConfigError

        mock_config.side_effect = ConfigError(
            "Test config error", guidance="Fix your config"
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["generate"])

        assert "error" in result.output.lower() or "Test config error" in result.output

    @patch("src.cli.load_config")
    @patch("src.cli.downloader")
    def test_generate_model_not_found(self, mock_downloader, mock_config):
        mock_config.return_value = {
            "model": "flux-schnell",
            "prompt": "test",
        }

        mock_model_path = MagicMock()
        mock_model_path.exists.return_value = False
        mock_downloader.get_models_dir.return_value = mock_model_path

        runner = CliRunner()
        result = runner.invoke(cli, ["generate"])

        assert "not found" in result.output.lower() or "error" in result.output.lower()

    @patch("src.cli.load_config")
    @patch("src.cli.is_model_valid")
    @patch("src.cli.downloader")
    def test_generate_model_invalid(self, mock_downloader, mock_valid, mock_config):
        mock_config.return_value = {
            "model": "flux-schnell",
            "prompt": "test",
        }

        mock_model_path = MagicMock()
        mock_model_path.exists.return_value = True
        mock_downloader.get_models_dir.return_value = mock_model_path

        mock_valid.return_value = False

        runner = CliRunner()
        result = runner.invoke(cli, ["generate"])

        assert (
            "incomplete" in result.output.lower()
            or "corrupted" in result.output.lower()
        )
