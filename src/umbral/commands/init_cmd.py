"""Comando `umbral init` — Bootstrap del proyecto (Sprint 1)."""

from __future__ import annotations

import os
from pathlib import Path

import typer

from umbral.agents.adapter_setup import setup_adapter
from umbral.core.config import (
    AgentType,
    JudgeConfig,
    JudgeMode,
    ProjectConfig,
    Role,
    Scale,
)
from umbral.core.profile import CognitiveProfile
from umbral.storage.config_store import save_config
from umbral.storage.paths import ensure_umbral_structure, get_umbral_dir
from umbral.storage.profile_store import save_profile
from umbral.ui.console import (
    print_error,
    print_header,
    print_info,
    print_next_step,
    print_success,
    print_warning,
)
from umbral.ui.prompts import (
    ask_agent,
    ask_domain,
    ask_judge_mode,
    ask_project_name,
    ask_role,
    ask_scale,
)


def init_project(
    project_name: str = typer.Argument(
        ..., help="Nombre del proyecto a inicializar."
    ),
    directory: Path = typer.Option(
        Path("."),
        "--dir",
        "-d",
        help="Directorio donde inicializar. Por defecto: directorio actual.",
    ),
    non_interactive: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Modo no interactivo con valores por defecto.",
    ),
) -> None:
    """Inicializa un proyecto Umbral con toda la estructura necesaria."""
    project_root = directory.resolve()
    print_header("Umbral Init", f"Inicializando proyecto: {project_name}")

    # Verificar si ya existe
    umbral_dir = get_umbral_dir(project_root)
    if umbral_dir.exists():
        print_warning(f"Ya existe {umbral_dir}. Se sobrescribirá la configuración.")

    # Recoger configuración
    if non_interactive:
        config = _default_config(project_name)
    else:
        config = _interactive_config(project_name)

    if config is None:
        print_error("Inicialización cancelada.")
        raise typer.Exit(code=1)

    # Crear estructura
    ensure_umbral_structure(project_root)

    # Guardar configuración
    save_config(project_root, config)
    print_success("Configuración guardada en .umbral/umbral.yaml")

    # Inicializar Perfil Cognitivo vacío
    profile = CognitiveProfile()
    save_profile(project_root, profile)
    print_success("Perfil Cognitivo inicializado en .umbral/profile.yaml")

    # Setup del adapter
    adapter_path = setup_adapter(project_root, config.agent)
    print_success(f"Adapter configurado: {adapter_path.relative_to(project_root)}")

    # Resumen
    _print_summary(config)
    print_next_step("umbral status")


def _default_config(project_name: str) -> ProjectConfig:
    """Crea configuración con valores por defecto."""
    has_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    return ProjectConfig(
        project_name=project_name,
        domain="general",
        scale=Scale.MVP,
        role=Role.EXPLORER,
        agent=AgentType.CLAUDE_CODE,
        judge=JudgeConfig(
            mode=JudgeMode.ONLINE if has_key else JudgeMode.OFFLINE
        ),
    )


def _interactive_config(project_name: str) -> ProjectConfig | None:
    """Recoge configuración vía prompts interactivos."""
    domain = ask_domain()
    if domain is None:
        return None

    scale = ask_scale()
    if scale is None:
        return None

    role = ask_role()
    if role is None:
        return None

    agent = ask_agent()
    if agent is None:
        return None

    has_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    if has_key:
        print_info("ANTHROPIC_API_KEY detectada ✓")
    else:
        print_warning("ANTHROPIC_API_KEY no detectada.")

    judge_mode = ask_judge_mode(has_key)
    if judge_mode is None:
        return None

    return ProjectConfig(
        project_name=project_name,
        domain=domain,
        scale=scale,
        role=role,
        agent=agent,
        judge=JudgeConfig(mode=judge_mode),
    )


def _print_summary(config: ProjectConfig) -> None:
    """Imprime un resumen de la configuración creada."""
    from umbral.ui.console import console

    console.print()
    console.print("[bold]Configuración del proyecto:[/bold]")
    console.print(f"  Proyecto:  [cyan]{config.project_name}[/cyan]")
    console.print(f"  Dominio:   [cyan]{config.domain}[/cyan]")
    console.print(f"  Escala:    [cyan]{config.scale.value}[/cyan]")
    console.print(f"  Rol:       [cyan]{config.role.value}[/cyan]")
    console.print(f"  Agente:    [cyan]{config.agent.value}[/cyan]")
    console.print(f"  Juez:      [cyan]{config.judge.mode.value}[/cyan]")
