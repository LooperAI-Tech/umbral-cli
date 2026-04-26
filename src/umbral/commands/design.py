"""Comando `umbral design` — Creación de EDEs (Sprint 2, sección 2.3).

Presenta al usuario los componentes requeridos para su nivel,
aplica Scale-Aware Guidance, y guarda la EDE como draft.
"""

from __future__ import annotations

import re
from pathlib import Path

import questionary
import typer

from umbral.core.config import Scale
from umbral.core.ede import (
    COMPONENT_NAMES,
    REQUIRED_COMPONENTS,
    EDE,
    EDEMetadata,
    EDEStatus,
)
from umbral.storage.config_store import load_config
from umbral.storage.ede_store import list_edes, save_ede
from umbral.storage.paths import find_project_root
from umbral.ui.console import (
    console,
    print_error,
    print_header,
    print_info,
    print_next_step,
    print_success,
    print_warning,
)
from umbral.ui.prompts import UMBRAL_STYLE


# Scale-Aware Guidance (sección 2.3.3)
SCALE_GUIDANCE: dict[str, str] = {
    "learning": (
        "🧪 Escala Learning: Jupyter + datos locales. "
        "Enfócate en entender conceptos, no en deploy."
    ),
    "mvp": (
        "🚀 Escala MVP: Stack mínimo viable. "
        "Streamlit + SQLite o equivalente simple."
    ),
    "startup": (
        "🏗️  Escala Startup: Arquitectura desacoplada. "
        "API + base de datos + frontend."
    ),
}


def design(
    level: int = typer.Option(
        1, "--level", "-l", min=1, max=3,
        help="Nivel de la EDE (1=Explorer, 2=Navigator, 3=Anchor).",
    ),
) -> None:
    """Crea una nueva EDE según el nivel especificado."""
    project_root = find_project_root()
    if project_root is None:
        print_error("No se encontró un proyecto Umbral. Ejecuta 'umbral init'.")
        raise typer.Exit(code=1)

    config = load_config(project_root)
    print_header("Umbral Design", f"Creando EDE Nivel {level}")

    # Scale-Aware Guidance
    guidance = SCALE_GUIDANCE.get(config.scale.value, "")
    if guidance:
        print_info(guidance)
        console.print()

    # Mostrar componentes requeridos
    required = REQUIRED_COMPONENTS[level]
    console.print("[bold]Componentes requeridos para este nivel:[/bold]")
    for comp in required:
        console.print(f"  • {COMPONENT_NAMES[comp]}")
    console.print()

    # Recoger metadatos
    title = questionary.text(
        "Título de la EDE:", style=UMBRAL_STYLE,
    ).ask()
    if not title:
        print_error("Título requerido.")
        raise typer.Exit(code=1)

    slug = _to_slug(title)
    bounded_context = questionary.text(
        "Bounded context (ej: auth, ml-pipeline, api):",
        style=UMBRAL_STYLE,
    ).ask() or ""

    # Verificar duplicados
    existing = list_edes(project_root)
    existing_slugs = [e.metadata.slug for e in existing]
    if slug in existing_slugs:
        print_warning(f"Ya existe una EDE con slug '{slug}'. Se sobrescribirá.")

    # Recoger componentes
    components = _collect_components(required)

    # Crear EDE
    metadata = EDEMetadata(
        slug=slug,
        title=title,
        level=level,
        status=EDEStatus.DRAFT,
        bounded_context=bounded_context,
        scale=config.scale.value,
    )
    ede = EDE(metadata=metadata, **components)

    # Guardar
    path = save_ede(project_root, ede)
    print_success(f"EDE guardada como draft: {path.name}")

    # Validar componentes
    missing = ede.validate_components()
    if missing:
        names = [COMPONENT_NAMES[m] for m in missing]
        print_warning(f"Componentes vacíos: {', '.join(names)}")
        print_info("Completa estos componentes y ejecuta 'umbral ede validate'.")
    else:
        print_success("Todos los componentes están presentes.")
        print_info(
            "Para aprobar la EDE, usa 'umbral ede validate' "
            "y luego edita el status a 'approved'."
        )

    print_next_step("umbral ede validate " + slug)


def _to_slug(title: str) -> str:
    """Convierte un título a slug en kebab-case."""
    slug = title.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def _collect_components(required: list[str]) -> dict[str, str]:
    """Recoge el contenido de cada componente vía prompts."""
    components: dict[str, str] = {}
    for comp in required:
        name = COMPONENT_NAMES[comp]
        console.print(f"\n[bold cyan]── {name} ──[/bold cyan]")
        content = questionary.text(
            f"Contenido para '{name}' (Enter para dejar vacío):",
            multiline=True,
            style=UMBRAL_STYLE,
        ).ask() or ""
        components[comp] = content
    return components
