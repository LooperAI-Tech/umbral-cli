"""Comando `umbral status` — Muestra el estado actual del proyecto."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.table import Table

from umbral.core.phase import get_phase_command, get_phase_name
from umbral.storage.config_store import load_config
from umbral.storage.paths import find_project_root
from umbral.storage.profile_store import load_profile
from umbral.ui.console import console, print_error, print_header, print_next_step


ROLE_ICONS = {
    "explorer": "🔰",
    "navigator": "🧭",
    "anchor": "⚓",
}

SCALE_ICONS = {
    "learning": "🧪",
    "mvp": "🚀",
    "startup": "🏗️",
}


def status() -> None:
    """Muestra el estado actual del proyecto Umbral."""
    project_root = find_project_root()
    if project_root is None:
        print_error(
            "No se encontró un proyecto Umbral. "
            "Ejecuta 'umbral init <nombre>' para crear uno."
        )
        raise typer.Exit(code=1)

    config = load_config(project_root)
    profile = load_profile(project_root)

    print_header("Umbral Status", config.project_name)

    # Tabla de estado
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Campo", style="bold")
    table.add_column("Valor", style="cyan")

    phase_name = get_phase_name(config.current_phase)
    role_icon = ROLE_ICONS.get(config.role.value, "")
    scale_icon = SCALE_ICONS.get(config.scale.value, "")

    table.add_row("Proyecto", config.project_name)
    table.add_row("Dominio", config.domain)
    table.add_row("Escala", f"{scale_icon} {config.scale.value}")
    table.add_row("Rol", f"{role_icon} {config.role.value}")
    table.add_row("Fase actual", f"{config.current_phase} — {phase_name}")
    table.add_row("Agente", config.agent.value)
    table.add_row("Juez", config.judge.mode.value)
    table.add_row("DKC", f"{profile.dkc:.0f}%")
    table.add_row("CDR", f"{profile.cdr:.0f}%")

    console.print(table)

    # Siempre sugerir umbral next
    print_next_step("umbral next")
