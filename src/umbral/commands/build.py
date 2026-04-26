"""Comando `umbral build` — Fase 3, scaffolding por bounded context (Sprint 5, 2.4.1)."""

from __future__ import annotations

import typer

from umbral.agents.orchestrator import deposit_build_prompt
from umbral.storage.config_store import load_config
from umbral.storage.paths import find_project_root
from umbral.ui.console import (
    print_error,
    print_header,
    print_info,
    print_next_step,
    print_success,
)


def build(
    context: str = typer.Option(
        ...,
        "--context",
        "-c",
        help="Slug de la EDE o bounded context a construir.",
    ),
) -> None:
    """Deposita el prompt de construcción (Guía, Andamio o Desbloqueo según mastery)."""
    project_root = find_project_root()
    if project_root is None:
        print_error("No se encontró un proyecto Umbral. Ejecuta 'umbral init'.")
        raise typer.Exit(code=1)

    config = load_config(project_root)
    print_header("Umbral Build", f"Contexto: {context} — {config.project_name}")

    path = deposit_build_prompt(project_root, context)
    rel = path.relative_to(project_root)
    print_success(f"Prompt depositado: {rel}")
    print_info(
        f"Modo de scaffolding según Perfil (contexto) y DKC. Agente: {config.agent.value}."
    )
    print_next_step("umbral next")
