"""Definición de fases del framework Umbral."""

from __future__ import annotations

from enum import IntEnum


class Phase(IntEnum):
    """Fases del framework (sección 2 del plan)."""

    DISCOVERY = 0       # Fase 0 — Descubrimiento
    ARTICULATION = 1    # Fase 1 — Articulación
    DESIGN = 2          # Fase 2 — Diseño
    CONSTRUCTION = 3    # Fase 3 — Construcción
    VERIFICATION = 4    # Fase 4 — Verificación
    CONSOLIDATION = 5   # Fase 5 — Consolidación


# Mapeo de fase a nombre legible
PHASE_NAMES: dict[Phase, str] = {
    Phase.DISCOVERY: "Descubrimiento",
    Phase.ARTICULATION: "Articulación",
    Phase.DESIGN: "Diseño",
    Phase.CONSTRUCTION: "Construcción",
    Phase.VERIFICATION: "Verificación",
    Phase.CONSOLIDATION: "Consolidación",
}

# Mapeo de fase a comando asociado
PHASE_COMMANDS: dict[Phase, str] = {
    Phase.DISCOVERY: "umbral discover",
    Phase.ARTICULATION: "umbral articulate",
    Phase.DESIGN: "umbral design",
    Phase.CONSTRUCTION: "umbral build",
    Phase.VERIFICATION: "umbral verify",
    Phase.CONSOLIDATION: "umbral consolidate",
}


def get_phase_name(phase: int) -> str:
    """Retorna el nombre legible de una fase."""
    try:
        return PHASE_NAMES[Phase(phase)]
    except ValueError:
        return f"Fase {phase} (desconocida)"


def get_phase_command(phase: int) -> str:
    """Retorna el comando asociado a una fase."""
    try:
        return PHASE_COMMANDS[Phase(phase)]
    except ValueError:
        return "umbral status"
