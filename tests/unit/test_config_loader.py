"""Unit tests for config loader."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import yaml

from src.config.loader import (
    load_config,
    load_model_config,
    get_config_path,
    get_default_config,
    DEFAULT_CONFIG,
)
from src.errors import ConfigError


class TestGetConfigPath:
    """Tests for get_config_path function."""

    def test_get_config_path_default(self):
        path = get_config_path()
        assert isinstance(path, Path)

    def test_get_config_path_custom(self):
        path = get_config_path("custom.yaml")
        assert "custom.yaml" in str(path)


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_config_missing_file(self):
        with patch("src.config.loader.get_config_path") as mock_path:
            mock_path.return_value = Path("/nonexistent/config.yaml")

            with pytest.raises(ConfigError) as exc_info:
                load_config()

            assert "not found" in str(exc_info.value)

    def test_load_config_invalid_yaml(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content:")
            temp_path = Path(f.name)

        try:
            with pytest.raises(ConfigError) as exc_info:
                load_config(temp_path)

            assert "Invalid YAML" in str(exc_info.value)
        finally:
            temp_path.unlink()

    def test_load_config_missing_model(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({"prompt": "test"}, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ConfigError) as exc_info:
                load_config(temp_path)

            assert "model" in str(exc_info.value).lower()
        finally:
            temp_path.unlink()

    def test_load_config_missing_prompt(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({"model": "flux-schnell"}, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ConfigError) as exc_info:
                load_config(temp_path)

            assert "prompt" in str(exc_info.value).lower()
        finally:
            temp_path.unlink()

    def test_load_config_unsupported_model(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({"model": "unknown-model", "prompt": "test"}, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ConfigError) as exc_info:
                load_config(temp_path)

            assert "not supported" in str(exc_info.value)
        finally:
            temp_path.unlink()

    def test_load_config_invalid_width(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(
                {
                    "model": "flux-schnell",
                    "prompt": "test",
                    "width": 500,  # Not divisible by 8
                },
                f,
            )
            temp_path = Path(f.name)

        try:
            with pytest.raises(ConfigError) as exc_info:
                load_config(temp_path)

            assert "Width" in str(exc_info.value)
        finally:
            temp_path.unlink()

    def test_load_config_invalid_steps(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            config_dir = tmpdir / "config" / "models"
            config_dir.mkdir(parents=True)

            yaml.dump(
                {"model": "flux-schnell", "prompt": "test", "num_inference_steps": 200},
                open(tmpdir / "config.yaml", "w"),
            )

            with patch("src.config.loader.Path.cwd", return_value=tmpdir):
                with pytest.raises(ConfigError) as exc_info:
                    load_config(tmpdir / "config.yaml")

                assert "num_inference_steps" in str(exc_info.value)

    def test_load_config_success(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({"model": "flux-schnell", "prompt": "A beautiful sunset"}, f)
            temp_path = Path(f.name)

        try:
            config = load_config(temp_path)
            assert config["model"] == "flux-schnell"
            assert config["prompt"] == "A beautiful sunset"
            assert config["width"] == 1024  # Default
            assert config["height"] == 1024  # Default
        finally:
            temp_path.unlink()

    def test_load_config_applies_defaults(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({"model": "flux-schnell", "prompt": "test"}, f)
            temp_path = Path(f.name)

        try:
            config = load_config(temp_path)
            assert config["guidance_scale"] == 3.5
            assert config["num_inference_steps"] == 28
            assert config["device"] == "auto"
            assert config["enable_progress"] is True
        finally:
            temp_path.unlink()

    def test_load_config_invalid_device(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({"model": "flux-schnell", "prompt": "test", "device": "gpu"}, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ConfigError) as exc_info:
                load_config(temp_path)

            assert "Unsupported device" in str(exc_info.value)
        finally:
            temp_path.unlink()


class TestLoadModelConfig:
    """Tests for load_model_config function."""

    def test_load_model_config_not_found(self):
        config = load_model_config("unknown-model")
        assert config == {}

    def test_load_model_config_success(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({"min_vram_gb": 4, "recommended_vram_gb": 8}, f)
            temp_path = Path(f.name)

        try:
            with patch("src.config.loader.Path.cwd") as mock_cwd:
                mock_cwd.return_value = temp_path.parent.parent
                config = load_model_config("test-model")
        finally:
            temp_path.unlink()


class TestGetDefaultConfig:
    """Tests for get_default_config function."""

    def test_get_default_config_returns_dict(self):
        defaults = get_default_config()
        assert isinstance(defaults, dict)
        assert defaults["model"] is None
        assert defaults["guidance_scale"] == 3.5

    def test_default_config_is_copy(self):
        defaults = get_default_config()
        defaults["model"] = "modified"
        original = DEFAULT_CONFIG.copy()
        assert original["model"] is None


class TestModelConfigMerging:
    """Tests for model-specific config merging."""

    def test_load_config_merges_model_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            config_dir = tmpdir / "config" / "models"
            config_dir.mkdir(parents=True)

            model_config = {
                "num_inference_steps": 20,
                "guidance_scale": 4.0,
                "min_vram_gb": 4,
            }
            with open(config_dir / "flux-schnell.yaml", "w") as f:
                yaml.dump(model_config, f)

            user_config = {
                "model": "flux-schnell",
                "prompt": "test",
                "num_inference_steps": 50,
            }
            with open(tmpdir / "config.yaml", "w") as f:
                yaml.dump(user_config, f)

            with patch("src.config.loader.Path.cwd", return_value=tmpdir):
                config = load_config(tmpdir / "config.yaml")

            assert config["num_inference_steps"] == 20

    def test_load_config_no_model_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            user_config = {
                "model": "flux-schnell",
                "prompt": "test",
            }
            with open(tmpdir / "config.yaml", "w") as f:
                yaml.dump(user_config, f)

            with patch("src.config.loader.Path.cwd", return_value=tmpdir):
                config = load_config(tmpdir / "config.yaml")

            assert config["num_inference_steps"] == 28

    def test_model_config_priority(self):
        """User config should take precedence over defaults when no model config exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            user_config = {
                "model": "flux-schnell",
                "prompt": "test",
                "num_inference_steps": 10,
            }
            with open(tmpdir / "config.yaml", "w") as f:
                yaml.dump(user_config, f)

            with patch("src.config.loader.Path.cwd", return_value=tmpdir):
                config = load_config(tmpdir / "config.yaml")

            assert config["num_inference_steps"] == 10


class TestValidation:
    """Tests for enhanced configuration validation."""

    def test_validate_output_dir_not_a_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            output_file = tmpdir / "output.txt"
            output_file.write_text("test")

            user_config = {
                "model": "flux-schnell",
                "prompt": "test",
                "output_dir": str(output_file),
            }
            with open(tmpdir / "config.yaml", "w") as f:
                yaml.dump(user_config, f)

            with patch("src.config.loader.Path.cwd", return_value=tmpdir):
                with pytest.raises(ConfigError) as exc_info:
                    load_config(tmpdir / "config.yaml")

                assert "not a directory" in str(exc_info.value)

    def test_validate_filename_format_missing_timestamp(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            user_config = {
                "model": "flux-schnell",
                "prompt": "test",
                "filename_format": "image.png",
            }
            with open(tmpdir / "config.yaml", "w") as f:
                yaml.dump(user_config, f)

            with patch("src.config.loader.Path.cwd", return_value=tmpdir):
                with pytest.raises(ConfigError) as exc_info:
                    load_config(tmpdir / "config.yaml")

                assert "timestamp" in str(exc_info.value)

    def test_validate_seed_invalid_type(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            user_config = {
                "model": "flux-schnell",
                "prompt": "test",
                "seed": "random",
            }
            with open(tmpdir / "config.yaml", "w") as f:
                yaml.dump(user_config, f)

            with patch("src.config.loader.Path.cwd", return_value=tmpdir):
                with pytest.raises(ConfigError) as exc_info:
                    load_config(tmpdir / "config.yaml")

                assert "seed" in str(exc_info.value).lower()

    def test_validate_seed_out_of_range(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            user_config = {
                "model": "flux-schnell",
                "prompt": "test",
                "seed": -1,
            }
            with open(tmpdir / "config.yaml", "w") as f:
                yaml.dump(user_config, f)

            with patch("src.config.loader.Path.cwd", return_value=tmpdir):
                with pytest.raises(ConfigError) as exc_info:
                    load_config(tmpdir / "config.yaml")

                assert "seed" in str(exc_info.value).lower()

    def test_validate_seed_valid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            user_config = {
                "model": "flux-schnell",
                "prompt": "test",
                "seed": 42,
            }
            with open(tmpdir / "config.yaml", "w") as f:
                yaml.dump(user_config, f)

            with patch("src.config.loader.Path.cwd", return_value=tmpdir):
                config = load_config(tmpdir / "config.yaml")

            assert config["seed"] == 42


class TestErrorMessages:
    """Tests for config error messages."""

    def test_error_message_includes_guidance(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            user_config = {
                "model": "flux-schnell",
                "prompt": "test",
                "width": 500,
            }
            with open(tmpdir / "config.yaml", "w") as f:
                yaml.dump(user_config, f)

            with patch("src.config.loader.Path.cwd", return_value=tmpdir):
                with pytest.raises(ConfigError) as exc_info:
                    load_config(tmpdir / "config.yaml")

                error_str = str(exc_info.value)
                assert "Width" in error_str
                assert "guidance" in error_str.lower() or "Use" in error_str

    def test_error_message_for_missing_model(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            user_config = {"prompt": "test"}
            with open(tmpdir / "config.yaml", "w") as f:
                yaml.dump(user_config, f)

            with patch("src.config.loader.Path.cwd", return_value=tmpdir):
                with pytest.raises(ConfigError) as exc_info:
                    load_config(tmpdir / "config.yaml")

                error_str = str(exc_info.value)
                assert "model" in error_str.lower()
                assert "flux-schnell" in error_str

    def test_error_message_for_missing_prompt(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            user_config = {"model": "flux-schnell"}
            with open(tmpdir / "config.yaml", "w") as f:
                yaml.dump(user_config, f)

            with patch("src.config.loader.Path.cwd", return_value=tmpdir):
                with pytest.raises(ConfigError) as exc_info:
                    load_config(tmpdir / "config.yaml")

                error_str = str(exc_info.value)
                assert "prompt" in error_str.lower()
                assert "Add" in error_str
