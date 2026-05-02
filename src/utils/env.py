"""Environment variable helpers."""

import os
from pathlib import Path
from typing import Union


def load_dotenv(path: Union[str, Path] = ".env") -> bool:
    """Load simple KEY=VALUE entries from a local .env file.

    Existing environment variables are left unchanged so shell-provided values
    keep priority over local development defaults.
    """
    env_path = Path(path)
    if not env_path.exists():
        return False

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if key.startswith("export "):
            key = key.removeprefix("export ").strip()

        if not key or key in os.environ:
            continue

        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]

        os.environ[key] = value

    return True
