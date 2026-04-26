"""Entry point de Typer para Umbral CLI."""

import typer
from rich.console import Console

from umbral import __version__
from umbral.commands.init_cmd import init_project
from umbral.commands.status import status

app = typer.Typer(
    name="umbral",
    help="Framework de desarrollo con comprensión sostenible.",
    no_args_is_help=True,
    invoke_without_command=True,
    rich_markup_mode="rich",
)
console = Console()


@app.callback()
def main(ctx: typer.Context) -> None:
    """Umbral CLI — Framework de desarrollo con comprensión sostenible."""
    pass


@app.command()
def version() -> None:
    """Muestra la versión actual de Umbral CLI."""
    console.print(f"umbral v{__version__}")


# Registrar comandos de Sprint 1
app.command(name="init")(init_project)
app.command(name="status")(status)


if __name__ == "__main__":
    app()
