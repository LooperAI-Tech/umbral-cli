"""Tests para el módulo __init__ de Umbral CLI."""

from umbral import __version__


def test_version_string():
    """Verifica que __version__ está definida y es semver válida."""
    assert __version__ == "0.1.0"
    parts = __version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)
