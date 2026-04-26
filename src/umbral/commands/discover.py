"""Comando `umbral discover` — Fase 0: Descubrimiento (sección 2.1).

Deposita un prompt contextualizado para que el agente del usuario
guíe el proceso de descubrimiento: validación de problemática,
evaluación de escala, y generación del Mapa de Dominio.
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


def discover() -> None:
    """Inicia la Fase 0 — Descubrimiento.

    Deposita un prompt contextualizado con las preguntas de
    problemática adaptadas al rol del usuario.
    """
    project_root = find_project_root()
    if project_root is None:
        print_error("No se encontró un proyecto Umbral. Ejecuta 'umbral init'.")
        raise typer.Exit(code=1)

    config = load_config(project_root)
    print_header("Fase 0 — Descubrimiento", config.project_name)

    # Depositar prompt
    path = deposit_phase_prompt(
        project_root,
        template_name="phases/discovery.md",
        output_filename="discover",
    )

    print_success(f"Prompt depositado: {path.relative_to(project_root)}")
    print_info(
        f"Abre tu agente ({config.agent.value}) y usa el prompt generado "
        "para iniciar el diálogo de descubrimiento."
    )
    print_info("Al terminar, ejecuta: umbral next")
