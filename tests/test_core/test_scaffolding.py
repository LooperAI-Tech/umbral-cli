"""Tests para core/scaffolding.py."""

from umbral.core.scaffolding import ScaffoldingMode, select_scaffolding_mode


def test_mastery_high_guia():
    assert select_scaffolding_mode(80) == ScaffoldingMode.GUIA
    assert select_scaffolding_mode(100) == ScaffoldingMode.GUIA


def test_mastery_andamio():
    assert select_scaffolding_mode(40) == ScaffoldingMode.ANDAMIO
    assert select_scaffolding_mode(79) == ScaffoldingMode.ANDAMIO


def test_mastery_desbloqueo():
    assert select_scaffolding_mode(0) == ScaffoldingMode.DESBLOQUEO
    assert select_scaffolding_mode(39) == ScaffoldingMode.DESBLOQUEO
