"""Hardware-related exception classes."""

from src.errors.base import HardwareError


class InsufficientMemoryError(HardwareError):
    def __init__(self, memory_type: str = "VRAM"):
        message = f"Not enough {memory_type} available."
        guidance = "Try closing other GPU applications or use a smaller model."
        super().__init__(message, guidance)


class CudaNotAvailableError(HardwareError):
    def __init__(self):
        message = "CUDA not available."
        guidance = "This app requires a GPU with CUDA support. Check your GPU drivers and PyTorch CUDA installation."
        super().__init__(message, guidance)
