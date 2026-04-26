"""Comando `umbral articulate` — Fase 1: Articulación (sección 2.2).

Deposita un prompt contextualizado para que el agente guíe
la co-creación de la spec: casos borde, modos de falla, alcance.
"""

from __future__ import annotations

import typer

from umbral.agents.orchestrator import deposit_phase_prompt
from umbral.storage.config_store import load_config
from umbral.storage.paths import find_project_root
from umbral.ui.console import (
    print_error,
    print_header,
    print_info,
    print_success,
)


def articulate() -> None:
    """Inicia la Fase 1 — Articulación.

    Deposita un prompt contextualizado con las preguntas de
    articulación adaptadas al rol del usuario, incluyendo
    EDEs existentes como contexto.
    """
    project_root = find_project_root()
    if project_root is None:
        print_error("No se encontró un proyecto Umbral. Ejecuta 'umbral init'.")
        raise typer.Exit(code=1)

    config = load_config(project_root)
    print_header("Fase 1 — Articulación", config.project_name)

    # Depositar prompt
    path = deposit_phase_prompt(
        project_root,
        template_name="phases/articulation.md",
        output_filename="articulate",
    )

    print_success(f"Prompt depositado: {path.relative_to(project_root)}")
    print_info(
        f"Abre tu agente ({config.agent.value}) y usa el prompt generado "
        "para co-crear la spec del proyecto."
    )
    print_info("Al terminar, ejecuta: umbral next")
