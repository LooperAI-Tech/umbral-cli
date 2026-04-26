"""Comando `umbral next` — Validación híbrida y avance de fase (sección 9.6).

Ejecuta la cascada: Capa 1 (determinista) → Capa 2 (LLM juez).
Avanza la fase automáticamente si el veredicto es `complete`.
Degrada a modo offline si no hay API key o la API falla.
"""

from __future__ import annotations

import typer

from umbral.core.config import JudgeMode
from umbral.core.phase import get_phase_command, get_phase_name
from umbral.judge.phase_judge import judge_phase
from umbral.storage.config_store import load_config, save_config
from umbral.storage.paths import find_project_root
from umbral.ui.console import (
    print_error,
    print_header,
    print_info,
    print_next_step,
    print_success,
    print_warning,
)
from umbral.ui.verdict_display import (
    display_offline_notice,
    display_validation_result,
    display_verdict,
)
from umbral.validation.phase_validator import validate_phase


def next_cmd() -> None:
    """Ejecuta validación híbrida y avanza la fase si corresponde."""
    project_root = find_project_root()
    if project_root is None:
        print_error("No se encontró un proyecto Umbral. Ejecuta 'umbral init'.")
        raise typer.Exit(code=1)

    config = load_config(project_root)
    phase_name = get_phase_name(config.current_phase)
    print_header(
        "Umbral Next",
        f"Evaluando Fase {config.current_phase} — {phase_name}",
    )

    # === Capa 1: Validación determinista ===
    validation = validate_phase(project_root, config)
    display_validation_result(validation)

    if not validation.passed:
        print_error("La validación estructural falló. Corrige los gaps antes de continuar.")
        raise typer.Exit(code=1)

    # === Capa 2: Juez LLM (solo si Capa 1 pasa) ===
    if config.judge.mode == JudgeMode.OFFLINE:
        display_offline_notice()
        _advance_phase(project_root, config)
        return

    # Intentar juez online
    verdict = judge_phase(project_root, config)

    if verdict is None:
        # Fallback a offline
        if config.judge.fallback_to_offline:
            display_offline_notice()
            _advance_phase(project_root, config)
        else:
            print_error(
                "El juez LLM no respondió y fallback_to_offline está desactivado."
            )
            raise typer.Exit(code=1)
        return

    # Mostrar veredicto
    display_verdict(verdict)

    if verdict.is_complete:
        _advance_phase(project_root, config)
    else:
        print_warning(
            "La fase no está completa según el juez. "
            "Revisa los gaps y vuelve a ejecutar 'umbral next'."
        )


def _advance_phase(project_root, config) -> None:
    """Avanza a la siguiente fase."""
    if config.current_phase >= 5:
        print_success(
            "¡Todas las fases completadas! "
            "Ejecuta 'umbral consolidate' para finalizar."
        )
        return

    old_phase = config.current_phase
    config.current_phase += 1
    save_config(project_root, config)

    new_name = get_phase_name(config.current_phase)
    new_cmd = get_phase_command(config.current_phase)
    print_success(
        f"Fase {old_phase} completada → "
        f"Avanzando a Fase {config.current_phase} — {new_name}"
    )
    print_next_step(new_cmd)
