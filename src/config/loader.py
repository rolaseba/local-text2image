"""Configuration loader for text2image."""

from pathlib import Path
from typing import Optional
import yaml

from src.errors import ConfigError
from src.utils.device import SUPPORTED_DEVICE_OPTIONS, normalize_device_option


DEFAULT_CONFIG = {
    "model": None,
    "prompt": None,
    "negative_prompt": "",
    "output_dir": "output",
    "filename_format": "{timestamp}_{prompt_hash}.png",
    "width": 1024,
    "height": 1024,
    "num_inference_steps": 28,
    "guidance_scale": 3.5,
    "seed": None,
    "batch_size": 1,
    "device": "auto",
    "enable_progress": True,
}


def get_config_path(config_file: str = "config.yaml") -> Path:
    """Get path to config file.

    Args:
        config_file: Name of config file (default: config.yaml)

    Returns:
        Path to config file
    """
    project_root = Path.cwd()
    config_path = project_root / "config" / config_file

    if not config_path.exists():
        config_path = project_root / config_file

    return config_path


def load_config(config_path: Optional[Path] = None) -> dict:
    """Load user configuration from YAML file.

    Args:
        config_path: Path to config file. If None, searches for config.yaml

    Returns:
        Configuration dictionary with defaults applied

    Raises:
        ConfigError: If config file is invalid or missing required fields
    """
    if config_path is None:
        config_path = get_config_path()

    if not config_path.exists():
        raise ConfigError(
            f"Config file not found: {config_path}",
            guidance="Create a config.yaml file in the project root or config/ directory.",
        )

    try:
        with open(config_path) as f:
            user_config = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise ConfigError(
            f"Invalid YAML in config file: {e}",
            guidance="Check your config.yaml for syntax errors.",
        )

    config = DEFAULT_CONFIG.copy()
    config.update(user_config)

    _validate_required_fields(config)

    model_name = config.get("model")
    if model_name:
        model_config = load_model_config(model_name)
        _merge_model_config(config, model_config)
        _validate_against_model_constraints(config, model_config, model_name)

    _validate_config(config, config_path)

    return config


def _validate_against_model_constraints(
    config: dict, model_constraints: dict, model_name: str
) -> None:
    """Validate user configuration against model-specific constraints.

    Args:
        config: Main configuration dictionary
        model_constraints: Constraints loaded from model YAML
        model_name: Name of the model being used
    """
    if not model_constraints:
        return

    constraints = model_constraints.get("constraints")
    if constraints is None:
        return

    for field, range_limits in constraints.items():
        # Only validate if the field exists in the final config
        if field in config:
            val = config[field]

            if not isinstance(val, (int, float)):
                raise ConfigError(
                    f"Invalid type for '{field}': expected number, got {type(val).__name__}.",
                    guidance=f"Update {field} in config.yaml to be a number.",
                )

            min_val = range_limits.get("min")
            max_val = range_limits.get("max")

            if min_val is not None and val < min_val:
                raise ConfigError(
                    f"Invalid value for '{field}': {val}. "
                    f"Model '{model_name}' requires a minimum of {min_val}.",
                    guidance=f"Update {field} in config.yaml to be at least {min_val}.",
                )

            if max_val is not None and val > max_val:
                raise ConfigError(
                    f"Invalid value for '{field}': {val}. "
                    f"Model '{model_name}' allows a maximum of {max_val}.",
                    guidance=f"Update {field} in config.yaml to be at most {max_val}.",
                )


def load_model_config(model_name: str) -> dict:
    """Load model-specific configuration.

    Args:
        model_name: Name of the model

    Returns:
        Model configuration dictionary
    """
    project_root = Path.cwd()
    model_config_path = project_root / "config" / "models" / f"{model_name}.yaml"

    if not model_config_path.exists():
        return {}

    try:
        with open(model_config_path) as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise ConfigError(
            f"Invalid YAML in model config: {e}",
            guidance=f"Check {model_config_path} for syntax errors.",
        )


def _merge_model_config(config: dict, model_config: dict) -> None:
    """Merge model-specific config into main config.

    Model config values override user config values.

    Args:
        config: Main configuration dictionary
        model_config: Model-specific configuration dictionary
    """
    if not model_config:
        return

    override_fields = [
        "num_inference_steps",
        "guidance_scale",
        "width",
        "height",
    ]

    for field in override_fields:
        if field in model_config and model_config[field] is not None:
            config[field] = model_config[field]


def _validate_config(config: dict, config_path: Path) -> None:
    """Validate configuration values.

    Args:
        config: Configuration dictionary
        config_path: Path to config file (for error messages)

    Raises:
        ConfigError: If validation fails
    """
    if not config.get("model"):
        raise ConfigError(
            "Config is missing required field 'model'",
            guidance="Add `model: flux-schnell` to your config.yaml",
        )

    if not config.get("prompt"):
        raise ConfigError(
            "Config is missing required field 'prompt'",
            guidance="Add your prompt to config.yaml, e.g., prompt: 'A beautiful sunset'",
        )

    model = config.get("model")
    supported_models = ["flux-schnell", "flux-dev"]
    if model not in supported_models:
        raise ConfigError(
            f"Model '{model}' is not supported. Available: {', '.join(supported_models)}",
            guidance=f"Use one of: {', '.join(supported_models)}",
        )

    width = config.get("width", 1024)
    height = config.get("height", 1024)

    if not isinstance(width, int) or not (256 <= width <= 2048 and width % 8 == 0):
        raise ConfigError(
            f"Width must be 256-2048 and divisible by 8. Got: {width}",
            guidance="Use a width value like 512, 768, 1024, or 1536",
        )

    if not isinstance(height, int) or not (256 <= height <= 2048 and height % 8 == 0):
        raise ConfigError(
            f"Height must be 256-2048 and divisible by 8. Got: {height}",
            guidance="Use a height value like 512, 768, 1024, or 1536",
        )

    steps = config.get("num_inference_steps", 28)
    if not isinstance(steps, int) or not (1 <= steps <= 100):
        raise ConfigError(
            f"num_inference_steps must be 1-100. Got: {steps}",
            guidance="Use a value between 1 and 100",
        )

    batch_size = config.get("batch_size", 1)
    if not isinstance(batch_size, int) or batch_size < 1:
        raise ConfigError(
            f"batch_size must be a positive integer. Got: {batch_size}",
            guidance="Set batch_size to 1 or more in config.yaml",
        )

    try:
        config["device"] = normalize_device_option(config.get("device"))
    except ValueError as e:
        raise ConfigError(
            str(e),
            guidance=f"Use one of: {', '.join(SUPPORTED_DEVICE_OPTIONS)}",
        )

    guidance = config.get("guidance_scale", 3.5)
    if not isinstance(guidance, (int, float)) or not (1.0 <= guidance <= 20.0):
        raise ConfigError(
            f"guidance_scale must be 1.0-20.0. Got: {guidance}",
            guidance="Use a value between 1.0 and 20.0",
        )

    _validate_output_settings(config)
    _validate_seed(config)
    _validate_vram_requirements(config)


def _validate_required_fields(config: dict) -> None:
    """Validate required fields before loading model-specific settings."""
    if not config.get("model"):
        raise ConfigError(
            "Config is missing required field 'model'",
            guidance="Add `model: flux-schnell` to your config.yaml",
        )

    if not config.get("prompt"):
        raise ConfigError(
            "Config is missing required field 'prompt'",
            guidance="Add your prompt to config.yaml, e.g., prompt: 'A beautiful sunset'",
        )

    model = config.get("model")
    supported_models = ["flux-schnell", "flux-dev"]
    if model not in supported_models:
        raise ConfigError(
            f"Model '{model}' is not supported. Available: {', '.join(supported_models)}",
            guidance=f"Use one of: {', '.join(supported_models)}",
        )


def _validate_output_settings(config: dict) -> None:
    """Validate output directory and filename format.

    Args:
        config: Configuration dictionary

    Raises:
        ConfigError: If output settings are invalid
    """
    output_dir = config.get("output_dir", "output")

    output_path = Path(output_dir)
    if output_path.exists() and not output_path.is_dir():
        raise ConfigError(
            f"Output directory '{output_dir}' is not a directory",
            guidance="Use a valid directory path for output_dir",
        )

    filename_format = config.get("filename_format", "{timestamp}.png")
    required_tokens = ["{timestamp}"]
    has_required = any(token in filename_format for token in required_tokens)
    if not has_required:
        raise ConfigError(
            f"filename_format must include '{{timestamp}}'. Got: {filename_format}",
            guidance="Use format like '{timestamp}_{prompt_hash}.png'",
        )


def _validate_seed(config: dict) -> None:
    """Validate seed value if specified.

    Args:
        config: Configuration dictionary

    Raises:
        ConfigError: If seed is invalid
    """
    seed = config.get("seed")
    if seed is None:
        return

    if not isinstance(seed, int):
        raise ConfigError(
            f"seed must be an integer, got {type(seed).__name__}",
            guidance="Use an integer seed or remove seed for random generation",
        )

    if seed < 0 or seed > 2**32 - 1:
        raise ConfigError(
            f"seed must be between 0 and 2^32-1. Got: {seed}",
            guidance="Use a seed value in range 0-4294967295",
        )


def _validate_vram_requirements(config: dict) -> None:
    """Validate VRAM requirements against available hardware.

    Args:
        config: Configuration dictionary

    Raises:
        ConfigError: If VRAM requirements not met
    """
    model = config.get("model")
    if not model:
        return

    model_config = load_model_config(model)
    min_vram = model_config.get("min_vram_gb", 4)

    try:
        import torch

        if config.get("device") in {"auto", "cuda"} and torch.cuda.is_available():
            device_count = torch.cuda.device_count()
            if device_count == 0:
                return

            available_vram = None
            for device_idx in range(device_count):
                try:
                    props = torch.cuda.get_device_properties(device_idx)
                    vram = props.total_memory / (1024**3)
                    if available_vram is None or vram > available_vram:
                        available_vram = vram
                except (IndexError, RuntimeError):
                    continue

            if available_vram is None:
                return

            if available_vram < min_vram:
                raise ConfigError(
                    f"Your GPU has {available_vram:.1f}GB VRAM but {model} requires {min_vram}GB",
                    guidance=f"Use a smaller model or GPU with at least {min_vram}GB VRAM",
                )
    except ImportError:
        pass


def get_default_config() -> dict:
    """Get default configuration values.

    Returns:
        Copy of default configuration dictionary
    """
    return DEFAULT_CONFIG.copy()
