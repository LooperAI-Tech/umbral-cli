"""Comando `umbral consolidate` — Fase 5 (Sprint 5, sección 2.6)."""

from __future__ import annotations

from pathlib import Path

import typer
import yaml
from rich.table import Table

from umbral.core.config import Role
from umbral.core.ede import EDEStatus
from umbral.core.governance import governance_for_bounded_context
from umbral.core.profile import CognitiveProfile
from umbral.core.promotion import evaluate_role_promotion
from umbral.storage.config_store import load_config, save_config
from umbral.storage.ede_store import list_edes
from umbral.storage.paths import find_project_root, get_phases_dir
from umbral.storage.profile_store import load_profile, save_profile
from umbral.ui.console import (
    console,
    print_error,
    print_header,
    print_info,
    print_next_step,
    print_success,
    print_warning,
)
from umbral.validation.drift_detector import DriftLevel, assess_drift


def _context_key(ede) -> str:
    return (ede.metadata.bounded_context or ede.metadata.slug or "").strip() or ede.metadata.slug


def _sync_from_edes(profile: CognitiveProfile, edes) -> None:
    c1 = c2 = c3 = 0
    for e in edes:
        if e.metadata.status != EDEStatus.APPROVED or not e.is_valid:
            continue
        if e.metadata.level == 1:
            c1 += 1
        elif e.metadata.level == 2:
            c2 += 1
        elif e.metadata.level == 3:
            c3 += 1
    profile.edes_written = {
        "level_1": c1,
        "level_2": c2,
        "level_3": c3,
    }
    for e in edes:
        if e.metadata.status == EDEStatus.APPROVED:
            k = _context_key(e)
            if k and k not in profile.system_contexts:
                profile.system_contexts.append(k)
            cur = profile.context_mastery.get(k, 0.0)
            profile.context_mastery[k] = max(float(cur), float(profile.dkc))


def _ingest_checkpoints(project_root: Path, profile: CognitiveProfile) -> None:
    phases = get_phases_dir(project_root)
    if not phases.exists():
        return
    for path in phases.glob("checkpoint-*.yaml"):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError):
            continue
        if not isinstance(data, dict):
            continue
        slug = str(data.get("ede_slug") or path.stem.replace("checkpoint-", "")).strip()
        if not slug:
            continue
        if data.get("has_debt"):
            v = max(profile.dkc, profile.context_mastery.get(slug, 0.0))
        else:
            v = max(85.0, profile.context_mastery.get(slug, 0.0))
        profile.context_mastery[slug] = min(100.0, float(v))


def consolidate(
    known_area: bool = typer.Option(
        True,
        "--known-area/--new-area",
        help="Próximo feature: área conocida (Fase 1) vs nueva (Fase 0).",
    ),
) -> None:
    """Consolida EDE + Perfil, evalúa drift, promoción y governance (Fase 5)."""
    project_root = find_project_root()
    if project_root is None:
        print_error("No se encontró un proyecto Umbral. Ejecuta 'umbral init'.")
        raise typer.Exit(code=1)

    config = load_config(project_root)
    profile = load_profile(project_root)
    edes = list_edes(project_root)

    print_header("Consolidación (Fase 5)", config.project_name)

    # Drift
    table = Table(title="Drift EDE ↔ código (heurística)", show_header=True)
    table.add_column("EDE", style="bold")
    table.add_column("Nivel", style="cyan")
    table.add_column("Resultado", style="magenta")
    table.add_column("Nota", style="dim")

    for ede in edes:
        if ede.metadata.status != EDEStatus.APPROVED:
            continue
        rep = assess_drift(ede, project_root)
        if rep.level == DriftLevel.SIGNIFICANT:
            print_warning(
                f"Drift significativo en '{rep.ede_slug}': {rep.note} "
                "— documenta en ADR si aplica (sección 2.6.1)."
            )
        if rep.level == DriftLevel.NONE:
            color = "green"
        elif rep.level == DriftLevel.MINOR:
            color = "yellow"
        else:
            color = "red"
        table.add_row(
            rep.ede_slug,
            str(ede.metadata.level),
            f"[{color}]{rep.level.value}[/{color}] {rep.overlap_ratio:.2f}",
            rep.note,
        )
    if table.rows:
        console.print(table)

    _sync_from_edes(profile, edes)
    _ingest_checkpoints(project_root, profile)
    profile.consolidation_runs += 1
    profile.next_feature_known_area = known_area
    save_profile(project_root, profile)

    # Governance
    ctxs = {_context_key(e) for e in edes} or {""}
    print_info("Governance por contexto:")
    for ctx in sorted(x for x in ctxs if x) or [""]:
        mode, expl = governance_for_bounded_context(ctx, edes)
        console.print(f"  • [bold]{ctx}[/bold]: {mode.value} — {expl}")

    # Promoción
    res = evaluate_role_promotion(config.role, profile, edes)
    if res.promoted:
        config.role = res.new_role
        save_config(project_root, config)
        print_success(f"Promoción: {res.message}")
    else:
        print_info(res.message)

    save_profile(project_root, profile)  # por si se tocó de nuevo
    if known_area:
        print_next_step("umbral articulate")
    else:
        print_next_step("umbral discover")
