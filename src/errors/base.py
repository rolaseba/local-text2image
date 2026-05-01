"""Base exception classes for text2image."""


class Text2ImageError(Exception):
    """Base exception for all text2image errors."""

    def __init__(self, message: str, guidance: str = ""):
        self.message = message
        self.guidance = guidance
        full_message = message
        if guidance:
            if not message.endswith("."):
                full_message = f"{message}. {guidance}"
            else:
                full_message = f"{message} {guidance}"
        super().__init__(full_message)


class ModelError(Text2ImageError):
    """Base exception for model-related errors."""

    pass


class ConfigError(Text2ImageError):
    """Base exception for configuration-related errors."""

    pass


class HardwareError(Text2ImageError):
    """Base exception for hardware-related errors."""

    pass
