"""Visualización de veredictos del juez con Rich."""

from __future__ import annotations

from rich.panel import Panel
from rich.table import Table

from umbral.judge.verdict import JudgeVerdict, VerdictStatus
from umbral.ui.console import console, print_info, print_success, print_warning
from umbral.validation.phase_validator import ValidationResult


def display_validation_result(result: ValidationResult) -> None:
    """Muestra el resultado de la validación determinista (Capa 1)."""
    if result.passed:
        print_success("Capa 1 (determinista): ✓ Validación pasada.")
        if result.artifacts_found:
            artifacts = ", ".join(result.artifacts_found)
            print_info(f"Artefactos encontrados: {artifacts}")
    else:
        print_warning("Capa 1 (determinista): ✗ Gaps estructurales detectados.")
        for gap in result.gaps:
            console.print(f"  [red]•[/red] {gap}")


def display_verdict(verdict: JudgeVerdict) -> None:
    """Muestra el veredicto del juez LLM (Capa 2)."""
    # Color según status
    status_colors = {
        VerdictStatus.COMPLETE: "green",
        VerdictStatus.INCOMPLETE: "yellow",
        VerdictStatus.NEEDS_REVISION: "red",
    }
    color = status_colors.get(verdict.status, "white")

    # Panel principal
    console.print()
    console.print(
        Panel(
            f"[bold {color}]{verdict.status.value.upper()}[/bold {color}]"
            f" — Confianza: {verdict.confidence:.0%}\n\n"
            f"{verdict.summary}",
            title="[bold]Capa 2 (Juez LLM)[/bold]",
            border_style=color,
        )
    )

    # Gaps
    if verdict.gaps:
        table = Table(
            title="Gaps detectados",
            show_header=True,
            header_style="bold",
        )
        table.add_column("Severidad", justify="center", width=10)
        table.add_column("Categoría", width=15)
        table.add_column("Descripción")

        severity_colors = {"high": "red", "medium": "yellow", "low": "dim"}
        for gap in verdict.gaps:
            sev_color = severity_colors.get(gap.severity, "white")
            table.add_row(
                f"[{sev_color}]{gap.severity}[/{sev_color}]",
                gap.category,
                gap.description,
            )
        console.print(table)

    # Acción sugerida
    if verdict.next_action:
        print_info(f"Acción sugerida: {verdict.next_action}")


def display_offline_notice() -> None:
    """Muestra aviso de modo offline."""
    print_warning(
        "Juez LLM no disponible. Solo se ejecutó validación estructural (Capa 1). "
        "Configura ANTHROPIC_API_KEY para validación semántica."
    )
