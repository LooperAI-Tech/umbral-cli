"""Comando `umbral metrics` — dashboard de las 13 métricas (Sprint 6, sección 2.9)."""

from __future__ import annotations

import typer
from rich.console import Group
from rich.panel import Panel
from rich.table import Table

from umbral.core.metrics import compute_metrics
from umbral.storage.config_store import load_config
from umbral.storage.paths import find_project_root
from umbral.storage.profile_store import load_profile
from umbral.storage.telemetry_store import load_telemetry
from umbral.ui.console import console, print_error, print_header


def _fmt(v: float | int | None, is_percent: bool = False) -> str:
    if v is None:
        return "N/D"
    if is_percent:
        return f"{float(v):.1f} %"
    if isinstance(v, int):
        return str(v)
    return f"{float(v):.2f}"


def _row(name: str, code: str, value: str, note: str = "") -> tuple:
    return (f"{name} ({code})", value, note)


def metrics() -> None:
    """Muestra el dashboard de salud del framework (13 métricas)."""
    project_root = find_project_root()
    if project_root is None:
        print_error("No se encontró un proyecto Umbral. Ejecuta 'umbral init'.")
        raise typer.Exit(code=1)

    config = load_config(project_root)
    profile = load_profile(project_root)
    telemetry = load_telemetry(project_root)
    snap = compute_metrics(project_root, config, profile, telemetry)

    print_header("Métricas Umbral", config.project_name)

    t1 = Table(title="Comprensión", show_lines=True)
    t1.add_column("Métrica", style="bold", no_wrap=True)
    t1.add_column("Valor", style="cyan")
    t1.add_column("Nota", style="dim", max_width=36)
    for row in (
        _row("Comprehension Coverage", "CC", _fmt(snap.cc, True), "Código con huella de EDE"),
        _row("Comprehension Debt Ratio", "CDR", _fmt(snap.cdr, True), "Deuda / PRs"),
        _row("Anchor Redundancy Index", "ARI", _fmt(snap.ari, True), "Contextos ≥80 % mastery"),
    ):
        t1.add_row(*row)

    t2 = Table(title="Progresión", show_lines=True)
    t2.add_column("Métrica", style="bold", no_wrap=True)
    t2.add_column("Valor", style="cyan")
    t2.add_column("Nota", style="dim", max_width=36)
    for row in (
        _row(
            "Navigator → Anchor Velocity",
            "NAV",
            _fmt(snap.nav) if snap.nav is not None else "N/D",
            "Semanas (telemetría futura)",
        ),
        _row("Domain Knowledge Coverage", "DKC", _fmt(snap.dkc, True), "Mapa de dominio"),
        _row(
            "Learning by Building Ratio",
            "LBB",
            _fmt(snap.lbb, True),
            "Conceptos aprendidos / total",
        ),
    ):
        t2.add_row(*row)

    t3 = Table(title="Calidad técnica", show_lines=True)
    t3.add_column("Métrica", style="bold", no_wrap=True)
    t3.add_column("Valor", style="cyan")
    t3.add_column("Nota", style="dim", max_width=36)
    for row in (
        _row(
            "Context Rot Frequency",
            "CRF",
            _fmt(snap.crf) if snap.crf is not None else "N/D",
            "Ciclos/semana (v0.2)",
        ),
        _row(
            "EDE Drift Score",
            "EDS",
            _fmt(snap.eds),
            "0=alineado, 1=drift fuerte (media)",
        ),
    ):
        t3.add_row(*row)

    t4 = Table(title="Velocidad", show_lines=True)
    t4.add_column("Métrica", style="bold", no_wrap=True)
    t4.add_column("Valor", style="cyan")
    t4.add_column("Nota", style="dim", max_width=36)
    for row in (
        _row(
            "Effective Throughput",
            "ET",
            _fmt(snap.et) if snap.et is not None else "N/D",
            "Features 30d (v0.2)",
        ),
        _row(
            "Explorer → Product Time",
            "ETP",
            _fmt(snap.etp) if snap.etp is not None else "N/D",
            "Semanas hasta MVP (v0.2)",
        ),
    ):
        t4.add_row(*row)

    t5 = Table(title="Juez LLM", show_lines=True)
    t5.add_column("Métrica", style="bold", no_wrap=True)
    t5.add_column("Valor", style="cyan")
    t5.add_column("Nota", style="dim", max_width=36)
    for row in (
        _row(
            "Judge Invocation Rate",
            "JIR",
            str(snap.jir),
            "Intentos online con `umbral next`",
        ),
        _row(
            "Judge Concurrence Rate",
            "JCR",
            _fmt(snap.jcr, True) if snap.jcr is not None else "N/D",
            "complete / (complete + otros)",
        ),
        _row(
            "Judge Fallback Rate",
            "JFR",
            _fmt(snap.jfr, True) if snap.jfr is not None else "N/D",
            "API fallida / intentos online",
        ),
    ):
        t5.add_row(*row)

    group = Group(t1, "", t2, "", t3, "", t4, "", t5)
    console.print(Panel(group, border_style="blue", title="[bold]Dashboard v0.1.0[/bold]"))
