"""Configuration-related exception classes."""

from src.errors.base import ConfigError


class ConfigNotFoundError(ConfigError):
    def __init__(self, config_path: str):
        message = f"Config file '{config_path}' not found."
        guidance = "Create a config file in the ./config/ directory or specify a different path."
        super().__init__(message, guidance)


class ConfigValidationError(ConfigError):
    def __init__(self, field: str, issue: str = "is required"):
        message = f"Invalid config: '{field}' {issue}."
        guidance = f"Add the '{field}' field to your config file."
        super().__init__(message, guidance)


class ConfigCompatibilityError(ConfigError):
    def __init__(self, field: str, model_requirement: str):
        message = f"Config value for '{field}' not compatible with model requirements."
        guidance = (
            f"The model requires: {model_requirement}. Update your config accordingly."
        )
        super().__init__(message, guidance)


class ConfigValueError(ConfigError):
    def __init__(self, field: str, allowed_values: list):
        message = f"Invalid value for '{field}'. Got: {{value}}"
        guidance = f"Use one of: {', '.join(str(v) for v in allowed_values)}"
        super().__init__(message, guidance)
