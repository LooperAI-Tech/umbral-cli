"""Modos de scaffolding por nivel de dominio (sección 2.4.1)."""

from __future__ import annotations

from enum import Enum


class ScaffoldingMode(str, Enum):
    """Modo de construcción según dominio en el bounded context."""

    GUIA = "guia"  # >= 80 %
    ANDAMIO = "andamio"  # 40–79 %
    DESBLOQUEO = "desbloqueo"  # < 40 %


def select_scaffolding_mode(mastery_percent: float) -> ScaffoldingMode:
    """Elige el modo a partir del % de dominio en el contexto (0–100)."""
    if mastery_percent >= 80.0:
        return ScaffoldingMode.GUIA
    if mastery_percent >= 40.0:
        return ScaffoldingMode.ANDAMIO
    return ScaffoldingMode.DESBLOQUEO
