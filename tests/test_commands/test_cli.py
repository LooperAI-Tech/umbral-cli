"""Tests para el CLI de Umbral — Sprint 0."""

from typer.testing import CliRunner

from umbral import __version__
from umbral.cli import app

runner = CliRunner()


def test_version_command_output():
    """Verifica que `umbral version` muestra la versión correcta."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert f"umbral v{__version__}" in result.output


def test_version_command_shows_semver():
    """Verifica que la salida contiene un formato semver válido."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    # Debe contener "v" seguido de X.Y.Z
    assert "v0.1.0" in result.output


def test_no_args_shows_help():
    """Verifica que sin argumentos se muestra la ayuda."""
    result = runner.invoke(app, [])
    # Typer/Click devuelve exit code 2 con no_args_is_help=True
    assert result.exit_code == 2
    assert "Usage" in result.output or "usage" in result.output.lower()


def test_help_flag():
    """Verifica que --help funciona correctamente."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "umbral" in result.output.lower()
