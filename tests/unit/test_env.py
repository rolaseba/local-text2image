"""Unit tests for environment helpers."""

import os

from src.utils.env import load_dotenv


def test_load_dotenv_sets_missing_values(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        """
# local secrets
HF_TOKEN="hf_test_token"
export HF_HUB_DOWNLOAD_TIMEOUT=60
EMPTY=
""",
        encoding="utf-8",
    )

    monkeypatch.delenv("HF_TOKEN", raising=False)
    monkeypatch.delenv("HF_HUB_DOWNLOAD_TIMEOUT", raising=False)
    monkeypatch.delenv("EMPTY", raising=False)

    assert load_dotenv(env_file) is True
    assert os.environ["HF_TOKEN"] == "hf_test_token"
    assert os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] == "60"
    assert os.environ["EMPTY"] == ""


def test_load_dotenv_does_not_override_shell_values(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("HF_TOKEN=from_file\n", encoding="utf-8")
    monkeypatch.setenv("HF_TOKEN", "from_shell")

    assert load_dotenv(env_file) is True
    assert os.environ["HF_TOKEN"] == "from_shell"


def test_load_dotenv_missing_file_returns_false(tmp_path):
    assert load_dotenv(tmp_path / ".env") is False
