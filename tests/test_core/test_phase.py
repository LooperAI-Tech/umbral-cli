"""Tests para core/phase.py."""

from umbral.core.phase import Phase, get_phase_command, get_phase_name


def test_phase_values():
    """Verifica los valores enteros de las fases."""
    assert Phase.DISCOVERY == 0
    assert Phase.ARTICULATION == 1
    assert Phase.DESIGN == 2
    assert Phase.CONSTRUCTION == 3
    assert Phase.VERIFICATION == 4
    assert Phase.CONSOLIDATION == 5


def test_get_phase_name():
    """Verifica los nombres de cada fase."""
    assert get_phase_name(0) == "Descubrimiento"
    assert get_phase_name(1) == "Articulación"
    assert get_phase_name(5) == "Consolidación"


def test_get_phase_name_unknown():
    """Verifica manejo de fase desconocida."""
    assert "desconocida" in get_phase_name(99)


def test_get_phase_command():
    """Verifica los comandos asociados a cada fase."""
    assert get_phase_command(0) == "umbral discover"
    assert get_phase_command(2) == "umbral design"
    assert get_phase_command(4) == "umbral verify"


def test_get_phase_command_unknown():
    """Verifica manejo de fase desconocida."""
    assert get_phase_command(99) == "umbral status"
