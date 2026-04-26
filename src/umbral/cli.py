"""Entry point de Typer para Umbral CLI."""

import typer
from rich.console import Console

from umbral import __version__
from umbral.commands.init_cmd import init_project
from umbral.commands.status import status
from umbral.commands.design import design
from umbral.commands.ede_cmd import ede_app
from umbral.commands.discover import discover
from umbral.commands.articulate import articulate
from umbral.commands.next_cmd import next_cmd
from umbral.commands.verify import verify
from umbral.commands.build import build
from umbral.commands.consolidate import consolidate
from umbral.commands.profile_cmd import profile_app
from umbral.commands.metrics_cmd import metrics

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


# Sprint 1
app.command(name="init")(init_project)
app.command(name="status")(status)

# Sprint 2
app.command(name="design")(design)
app.add_typer(ede_app, name="ede")

# Sprint 3
app.command(name="discover")(discover)
app.command(name="articulate")(articulate)

# Sprint 4
app.command(name="next")(next_cmd)
app.command(name="verify")(verify)

# Sprint 5
app.add_typer(profile_app, name="profile")
app.command(name="build")(build)
app.command(name="consolidate")(consolidate)

# Sprint 6
app.command(name="metrics")(metrics)


if __name__ == "__main__":
    app()
