"""Comando `umbral ede` — Gestión de EDEs (list, show, validate, approve).

Subcomandos:
  - umbral ede list      — Lista todas las EDEs
  - umbral ede show      — Muestra una EDE completa
  - umbral ede validate  — Valida estructura de una EDE
  - umbral ede approve   — Aprueba una EDE draft
"""

from __future__ import annotations

import typer
from rich.table import Table

from umbral.core.ede import COMPONENT_NAMES, EDEStatus
from umbral.storage.config_store import load_config
from umbral.storage.ede_store import list_edes, load_ede, save_ede
from umbral.storage.paths import find_project_root
from umbral.ui.console import (
    console,
    print_error,
    print_header,
    print_info,
    print_success,
    print_warning,
)

ede_app = typer.Typer(
    name="ede",
    help="Gestión de EDEs (Estructuras de Decisión Explícita).",
    no_args_is_help=True,
    invoke_without_command=True,
)


@ede_app.callback()
def ede_callback(ctx: typer.Context) -> None:
    """Gestión de EDEs."""
    pass


@ede_app.command(name="list")
def ede_list() -> None:
    """Lista todas las EDEs del proyecto."""
    project_root = find_project_root()
    if project_root is None:
        print_error("No se encontró un proyecto Umbral.")
        raise typer.Exit(code=1)

    edes = list_edes(project_root)
    if not edes:
        print_info("No hay EDEs registradas. Usa 'umbral design' para crear una.")
        return

    print_header("EDEs del proyecto")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Slug", style="white")
    table.add_column("Título", style="white")
    table.add_column("Nivel", justify="center")
    table.add_column("Estado", justify="center")
    table.add_column("Contexto", style="dim")

    for ede in edes:
        status_style = "green" if ede.metadata.status == EDEStatus.APPROVED else "yellow"
        table.add_row(
            ede.metadata.slug,
            ede.metadata.title,
            str(ede.metadata.level),
            f"[{status_style}]{ede.metadata.status.value}[/{status_style}]",
            ede.metadata.bounded_context,
        )

    console.print(table)


@ede_app.command(name="show")
def ede_show(
    slug: str = typer.Argument(..., help="Slug de la EDE a mostrar."),
) -> None:
    """Muestra el contenido completo de una EDE."""
    project_root = find_project_root()
    if project_root is None:
        print_error("No se encontró un proyecto Umbral.")
        raise typer.Exit(code=1)

    try:
        ede = load_ede(project_root, slug)
    except FileNotFoundError:
        print_error(f"EDE no encontrada: {slug}")
        raise typer.Exit(code=1)

    # Encabezado
    status_style = "green" if ede.metadata.status == EDEStatus.APPROVED else "yellow"
    print_header(
        ede.metadata.title,
        f"Nivel {ede.metadata.level} · [{status_style}]{ede.metadata.status.value}[/{status_style}]",
    )

    # Metadatos
    console.print(f"  [dim]Slug:[/dim] {ede.metadata.slug}")
    console.print(f"  [dim]Contexto:[/dim] {ede.metadata.bounded_context}")
    console.print(f"  [dim]Escala:[/dim] {ede.metadata.scale}")
    console.print(f"  [dim]Creada:[/dim] {ede.metadata.created_at}")
    console.print()

    # Componentes
    for comp_key, comp_name in COMPONENT_NAMES.items():
        content = ede.get_component(comp_key)
        if content and content.strip():
            console.print(f"[bold cyan]## {comp_name}[/bold cyan]")
            console.print(content.strip())
            console.print()


@ede_app.command(name="validate")
def ede_validate(
    slug: str = typer.Argument(..., help="Slug de la EDE a validar."),
) -> None:
    """Valida la estructura de una EDE según su nivel."""
    project_root = find_project_root()
    if project_root is None:
        print_error("No se encontró un proyecto Umbral.")
        raise typer.Exit(code=1)

    try:
        ede = load_ede(project_root, slug)
    except FileNotFoundError:
        print_error(f"EDE no encontrada: {slug}")
        raise typer.Exit(code=1)

    print_header("Validación de EDE", f"{ede.metadata.title} (Nivel {ede.metadata.level})")

    missing = ede.validate_components()
    if missing:
        for comp in missing:
            print_warning(f"Componente faltante: {COMPONENT_NAMES[comp]}")
        print_error(
            f"{len(missing)} componente(s) faltante(s). "
            "Completa el archivo y vuelve a validar."
        )
        raise typer.Exit(code=1)
    else:
        print_success("Todos los componentes están presentes y con contenido.")
        if ede.metadata.status == EDEStatus.DRAFT:
            print_info("La EDE está en draft. Usa 'umbral ede approve' para aprobarla.")


@ede_app.command(name="approve")
def ede_approve(
    slug: str = typer.Argument(..., help="Slug de la EDE a aprobar."),
) -> None:
    """Aprueba una EDE draft (cambia status a approved)."""
    project_root = find_project_root()
    if project_root is None:
        print_error("No se encontró un proyecto Umbral.")
        raise typer.Exit(code=1)

    try:
        ede = load_ede(project_root, slug)
    except FileNotFoundError:
        print_error(f"EDE no encontrada: {slug}")
        raise typer.Exit(code=1)

    # Validar primero
    missing = ede.validate_components()
    if missing:
        names = [COMPONENT_NAMES[m] for m in missing]
        print_error(
            f"No se puede aprobar: faltan componentes ({', '.join(names)}). "
            "Valida primero con 'umbral ede validate'."
        )
        raise typer.Exit(code=1)

    if ede.metadata.status == EDEStatus.APPROVED:
        print_info(f"La EDE '{slug}' ya está aprobada.")
        return

    ede.metadata.status = EDEStatus.APPROVED
    save_ede(project_root, ede)
    print_success(f"EDE '{slug}' aprobada ✓")
