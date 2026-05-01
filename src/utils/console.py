"""Rich console utilities for text2image."""

from rich.console import Console
from rich.theme import Theme

custom_theme = Theme(
    {
        "info": "cyan",
        "success": "green",
        "warning": "yellow",
        "error": "bold red",
    }
)

console = Console(theme=custom_theme)


def print_info(message: str) -> None:
    """Print info message."""
    console.print(message, style="info")


def print_success(message: str) -> None:
    """Print success message."""
    console.print(message, style="success")


def print_warning(message: str) -> None:
    """Print warning message."""
    console.print(message, style="warning")


def print_error(message: str) -> None:
    """Print error message."""
    console.print(f"Error: {message}", style="error")


def print_header(message: str) -> None:
    """Print header message."""
    console.print(f"[bold]{message}[/bold]")


def print_command(message: str) -> None:
    """Print command output."""
    console.print(message)
