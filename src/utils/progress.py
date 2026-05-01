"""Rich progress utilities for text2image."""

from typing import Optional
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
)

progress = Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    TimeRemainingColumn(),
)


def create_progress_bar(description: str) -> Optional[object]:
    """Create a progress bar for long-running operations.

    Returns a task ID that can be used to update progress.
    """
    return progress.add_task(description)


def start_progress() -> None:
    """Start the progress display."""
    if not progress.live.is_started:
        progress.start()


def stop_progress() -> None:
    """Stop the progress display."""
    if progress.live.is_started:
        progress.stop()
