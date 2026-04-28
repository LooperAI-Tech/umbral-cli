"""Comando `umbral init` — Bootstrap del proyecto (Sprint 1)."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import typer

from umbral.agents.adapter_setup import setup_adapter
from umbral.core.config import (
    AgentType,
    JudgeConfig,
    JudgeMode,
    LLMProvider,
    PROVIDER_DEFAULT_MODELS,
    PROVIDER_ENV_KEYS,
    ProjectConfig,
    Role,
    Scale,
)
from umbral.core.profile import CognitiveProfile
from umbral.core.telemetry import UmbralTelemetry
from umbral.storage.config_store import save_config
from umbral.storage.paths import ensure_umbral_structure, get_telemetry_path, get_umbral_dir
from umbral.storage.profile_store import save_profile
from umbral.storage.telemetry_store import save_telemetry
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
    ask_api_key,
    ask_domain,
    ask_judge_mode,
    ask_llm_provider,
    ask_project_name,
    ask_role,
    ask_scale,
)


def init_project(
    project_name: str = typer.Argument(
        ..., help="Nombre del proyecto a inicializar (y de la subcarpeta que se crea por defecto)."
    ),
    directory: Path | None = typer.Option(
        None,
        "--dir",
        "-d",
        help=(
            "Directorio raíz del proyecto. "
            "Si se omite, se crea una subcarpeta con el nombre del proyecto "
            "en el directorio actual. Usa -d . para usar solo el directorio actual."
        ),
    ),
    non_interactive: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Modo no interactivo con valores por defecto.",
    ),
) -> None:
    """Inicializa un proyecto Umbral con toda la estructura necesaria."""
    if directory is None:
        project_root = (Path.cwd() / project_name).resolve()
    else:
        project_root = directory.resolve()

    if not _is_safe_project_folder_name(project_name) and directory is None:
        print_error(
            "El nombre del proyecto no puede contener separadores de ruta (\\ o /). "
            "Usa un identificador simple (p. ej. mi-app-api)."
        )
        raise typer.Exit(code=1)

    project_root.mkdir(parents=True, exist_ok=True)

    print_header("Umbral Init", f"Inicializando proyecto: {project_name}")
    print_info(f"Raíz del proyecto: {project_root}")

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

    if not get_telemetry_path(project_root).exists():
        save_telemetry(
            project_root,
            UmbralTelemetry(
                first_umbral_init_at=datetime.now(timezone.utc).isoformat()
            ),
        )

    # Setup del adapter
    adapter_path = setup_adapter(project_root, config.agent)
    print_success(f"Adapter configurado: {adapter_path.relative_to(project_root)}")

    # Resumen
    _print_summary(config)
    print_next_step("umbral status")


def _is_safe_project_folder_name(name: str) -> bool:
    """Evita nombres que confundan la ruta (.., o separadores)."""
    if ".." in name or "/" in name or "\\" in name:
        return False
    if not name.strip():
        return False
    return True


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
    # 1. Proveedor de LLM
    provider = ask_llm_provider()
    if provider is None:
        return None

    # 2. API Key
    api_key = ask_api_key(provider)
    if api_key is None:
        return None

    has_key = bool(api_key.strip()) if api_key else False

    if has_key:
        env_var = PROVIDER_ENV_KEYS[provider.value]
        os.environ[env_var] = api_key
        print_info(f"{env_var} configurada ✓")
    else:
        print_warning("No se proporcionó API key.")

    # 3. Dominio
    domain = ask_domain()
    if domain is None:
        return None

    # 4. Escala
    scale = ask_scale()
    if scale is None:
        return None

    # 5. Rol
    role = ask_role()
    if role is None:
        return None

    # 6. Agente
    agent = ask_agent()
    if agent is None:
        return None

    # 7. Modo del juez
    judge_mode = ask_judge_mode(has_key)
    if judge_mode is None:
        return None

    return ProjectConfig(
        project_name=project_name,
        domain=domain,
        scale=scale,
        role=role,
        agent=agent,
        judge=JudgeConfig(
            mode=judge_mode,
            provider=provider.value,
            model=PROVIDER_DEFAULT_MODELS[provider.value],
        ),
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
    console.print(f"  Proveedor: [cyan]{config.judge.provider}[/cyan]")
    console.print(f"  Modelo:    [cyan]{config.judge.model}[/cyan]")
    console.print(f"  Juez:      [cyan]{config.judge.mode.value}[/cyan]")
