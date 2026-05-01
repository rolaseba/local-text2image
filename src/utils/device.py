"""Device selection helpers for image generation."""

from dataclasses import dataclass


SUPPORTED_DEVICE_OPTIONS = ("auto", "cuda", "mps", "xpu", "cpu")


@dataclass(frozen=True)
class DeviceSelection:
    """Selected compute device and support metadata."""

    name: str
    requested: str
    is_accelerated: bool
    is_experimental: bool = False

    @property
    def warning(self) -> str | None:
        if self.name == "cpu":
            return "Using CPU. Generation is supported but will be very slow."
        if self.is_experimental:
            return (
                f"Using {self.name.upper()} backend. This is experimental and "
                "depends on your PyTorch build."
            )
        return None


def normalize_device_option(device: str | None) -> str:
    """Normalize a user-provided device option."""
    selected = (device or "auto").strip().lower()
    if selected not in SUPPORTED_DEVICE_OPTIONS:
        allowed = ", ".join(SUPPORTED_DEVICE_OPTIONS)
        raise ValueError(f"Unsupported device '{device}'. Use one of: {allowed}")
    return selected


def select_device(device: str | None = "auto") -> DeviceSelection:
    """Select the best available generation device."""
    requested = normalize_device_option(device)

    try:
        import torch
    except ImportError as exc:
        raise RuntimeError("PyTorch is not installed") from exc

    available = {
        "cuda": torch.cuda.is_available(),
        "mps": bool(
            hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
        ),
        "xpu": bool(hasattr(torch, "xpu") and torch.xpu.is_available()),
        "cpu": True,
    }

    if requested == "auto":
        for candidate in ("cuda", "mps", "xpu", "cpu"):
            if available[candidate]:
                return _build_selection(candidate, requested)

    if available.get(requested):
        return _build_selection(requested, requested)

    raise RuntimeError(f"Requested device '{requested}' is not available")


def _build_selection(name: str, requested: str) -> DeviceSelection:
    return DeviceSelection(
        name=name,
        requested=requested,
        is_accelerated=name != "cpu",
        is_experimental=name in {"mps", "xpu"},
    )
