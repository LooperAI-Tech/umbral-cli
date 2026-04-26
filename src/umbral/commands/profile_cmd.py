"""Comandos `umbral profile show|update` — Perfil cognitivo (Sprint 5, 2.8)."""

from __future__ import annotations

import questionary
import typer
from rich.table import Table

from umbral.core.governance import governance_for_bounded_context
from umbral.storage.config_store import load_config
from umbral.storage.ede_store import list_edes
from umbral.storage.paths import find_project_root
from umbral.storage.profile_store import load_profile, save_profile
from umbral.ui.console import (
    console,
    print_error,
    print_header,
    print_info,
    print_success,
)
from umbral.ui.prompts import UMBRAL_STYLE

profile_app = typer.Typer(
    name="profile",
    help="Perfil cognitivo (dominio + sistema).",
    no_args_is_help=True,
    invoke_without_command=True,
)


@profile_app.callback()
def _profile_callback() -> None:
    """Perfil cognitivo."""


@profile_app.command("show")
def profile_show() -> None:
    """Muestra el Perfil Cognitivo y el Governance por contexto."""
    project_root = find_project_root()
    if project_root is None:
        print_error("No se encontró un proyecto Umbral. Ejecuta 'umbral init'.")
        raise typer.Exit(code=1)

    config = load_config(project_root)
    profile = load_profile(project_root)
    edes = list_edes(project_root)

    print_header("Perfil cognitivo", config.project_name)

    t1 = Table(title="Métricas", show_header=True)
    t1.add_column("Métrica", style="bold")
    t1.add_column("Valor", style="cyan")
    t1.add_row("DKC (dominio)", f"{profile.dkc:.1f} %")
    t1.add_row("CDR (deuda / PRs)", f"{profile.cdr:.1f} %")
    t1.add_row("PRs totales", str(profile.total_prs))
    t1.add_row("Deuda de comprensión (count)", str(profile.comprehension_debt))
    t1.add_row("Consolidaciones", str(profile.consolidation_runs))
    t1.add_row("Próximo feature en área conocida", "sí" if profile.next_feature_known_area else "no")
    console.print(t1)

    t2 = Table(title="EDEs por nivel (persistido)", show_header=True)
    t2.add_column("Nivel", style="bold")
    t2.add_column("Cantidad", style="cyan")
    for k, v in profile.edes_written.items():
        t2.add_row(k, str(v))
    console.print(t2)

    if profile.domain_concepts:
        t3 = Table(title="Conceptos de dominio", show_header=True)
        t3.add_column("Concepto", style="bold")
        t3.add_column("Estado", style="cyan")
        for c in profile.domain_concepts:
            t3.add_row(c.name, "aprendido" if c.learned else "pendiente")
        console.print(t3)

    if profile.context_mastery:
        t4 = Table(title="Mastery por contexto (%)", show_header=True)
        t4.add_column("Contexto", style="bold")
        t4.add_column("Mastery", style="cyan")
        for name, val in profile.context_mastery.items():
            t4.add_row(name, f"{val:.0f} %")
        console.print(t4)

    if profile.system_contexts:
        print_info("Bounded contexts (sistema): " + ", ".join(profile.system_contexts))

    # Governance por EDE / contexto
    ctxs = {e.metadata.bounded_context or e.metadata.slug for e in edes if e.metadata.slug}
    for ctx in sorted(ctxs) or [""]:
        mode, expl = governance_for_bounded_context(ctx, edes)
        console.print(
            f"[bold]{ctx or '(global)'}:[/bold] {mode.value} — {expl}"
        )


@profile_app.command("update")
def profile_update() -> None:
    """Edita el perfil de forma interactiva (conceptos, contextos, mastery)."""
    project_root = find_project_root()
    if project_root is None:
        print_error("No se encontró un proyecto Umbral. Ejecuta 'umbral init'.")
        raise typer.Exit(code=1)

    profile = load_profile(project_root)
    print_header("Actualizar perfil", "Selecciona una acción")

    action = questionary.select(
        "¿Qué deseas actualizar?",
        choices=[
            questionary.Choice("Marcar / desmarcar un concepto del dominio", value="concept"),
            questionary.Choice("Añadir un bounded context al sistema", value="context"),
            questionary.Choice("Ajustar mastery (0–100) en un contexto", value="mastery"),
            questionary.Choice("Indicar si el próximo feature es área conocida", value="area"),
        ],
        style=UMBRAL_STYLE,
    ).ask()

    if not action:
        raise typer.Exit(0)

    if action == "concept" and profile.domain_concepts:
        names = [c.name for c in profile.domain_concepts]
        name = questionary.select("Concepto", choices=names, style=UMBRAL_STYLE).ask()
        for c in profile.domain_concepts:
            if c.name == name:
                toggle = questionary.confirm(
                    f"¿Marcar '{name}' como aprendido?", style=UMBRAL_STYLE
                ).ask()
                c.learned = bool(toggle)
                break
    elif action == "concept":
        print_info("No hay conceptos en el perfil. Completa el mapa con `umbral discover` o edita profile.yaml.")
        raise typer.Exit(0)
    elif action == "context":
        line = questionary.text(
            "Nombre del bounded context:", style=UMBRAL_STYLE
        ).ask()
        if line and line.strip() and line.strip() not in profile.system_contexts:
            profile.system_contexts.append(line.strip())
    elif action == "mastery":
        ctx = questionary.text(
            "Nombre del contexto (slug o bounded context):", style=UMBRAL_STYLE
        ).ask()
        val_s = questionary.text(
            "Mastery 0-100:", style=UMBRAL_STYLE
        ).ask()
        if ctx and val_s is not None:
            try:
                v = min(100.0, max(0.0, float(str(val_s).replace(",", "."))))
                profile.context_mastery[ctx.strip()] = v
            except ValueError:
                print_error("Valor inválido.")
                raise typer.Exit(1) from None
    elif action == "area":
        v = questionary.confirm(
            "¿El próximo feature es en un área que ya conoces (saltar a articulación)?",
            default=profile.next_feature_known_area,
            style=UMBRAL_STYLE,
        ).ask()
        if v is not None:
            profile.next_feature_known_area = v

    save_profile(project_root, profile)
    print_success("Perfil guardado en .umbral/profile.yaml")
