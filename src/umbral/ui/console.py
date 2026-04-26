"""Utilidades de consola Rich para Umbral CLI."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()
error_console = Console(stderr=True)


def print_success(message: str) -> None:
    """Imprime un mensaje de éxito en verde."""
    console.print(f"[bold green]✓[/bold green] {message}")


def print_error(message: str) -> None:
    """Imprime un mensaje de error en rojo."""
    error_console.print(f"[bold red]✗[/bold red] {message}")


def print_warning(message: str) -> None:
    """Imprime un mensaje de advertencia en amarillo."""
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def print_info(message: str) -> None:
    """Imprime un mensaje informativo en azul."""
    console.print(f"[bold blue]ℹ[/bold blue] {message}")


def print_header(title: str, subtitle: str = "") -> None:
    """Imprime un encabezado estilizado con Rich Panel."""
    text = Text(title, style="bold cyan")
    if subtitle:
        text.append(f"\n{subtitle}", style="dim")
    console.print(Panel(text, border_style="cyan", expand=False))


def print_next_step(command: str) -> None:
    """Imprime la sugerencia del siguiente paso."""
    console.print()
    console.print(
        Panel(
            f"[bold]Siguiente paso:[/bold] [cyan]{command}[/cyan]",
            border_style="green",
            expand=False,
        )
    )
