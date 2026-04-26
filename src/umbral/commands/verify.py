"""Comando `umbral verify` — Comprehension Gate (sección 9.7/2.5).

Genera preguntas calibradas al rol, el usuario responde,
se autoevalúa, y el Perfil Cognitivo se actualiza.
"""

from __future__ import annotations

import questionary
import typer

from umbral.core.ede import EDEStatus
from umbral.storage.config_store import load_config
from umbral.storage.ede_store import list_edes
from umbral.storage.paths import find_project_root
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
from umbral.ui.prompts import UMBRAL_STYLE
from umbral.validation.comprehension_gate import (
    ComprehensionCheckpoint,
    GateQuestion,
    generate_questions,
    save_checkpoint,
)


def verify(
    bounded_context: str = typer.Option(
        "",
        "--bounded-context",
        "-bc",
        help="Slug del bounded context (EDE) a verificar.",
    ),
) -> None:
    """Ejecuta el Comprehension Gate adaptativo."""
    project_root = find_project_root()
    if project_root is None:
        print_error("No se encontró un proyecto Umbral. Ejecuta 'umbral init'.")
        raise typer.Exit(code=1)

    config = load_config(project_root)
    profile = load_profile(project_root)

    # Determinar el bounded context
    ede_slug = bounded_context
    if not ede_slug:
        edes = list_edes(project_root)
        approved = [e for e in edes if e.metadata.status == EDEStatus.APPROVED]
        if approved:
            ede_slug = approved[-1].metadata.slug
        else:
            ede_slug = "general"

    print_header(
        "Comprehension Gate",
        f"Verificando: {ede_slug} — Rol: {config.role.value}",
    )

    # Generar preguntas
    gate_questions: list[GateQuestion] = generate_questions(config.role, profile)

    console.print(
        f"\n[bold]Se te harán {len(gate_questions)} preguntas.[/bold]\n"
    )

    # Recoger respuestas
    answers = []
    for i, gq in enumerate(gate_questions, 1):
        console.print(f"[bold cyan]Pregunta {i}/{len(gate_questions)}:[/bold cyan]")
        console.print(f"  {gq.text}\n")
        answer = questionary.text(
            "Tu respuesta:",
            multiline=True,
            style=UMBRAL_STYLE,
        ).ask()
        answers.append(answer or "")
        console.print()

    # Autoevaluación
    assessment = questionary.select(
        "¿Cómo evalúas tu comprensión general?",
        choices=[
            questionary.Choice("Alta — Entiendo todo", value="alta"),
            questionary.Choice("Parcial — Entiendo la mayoría", value="parcial"),
            questionary.Choice("Baja — Necesito más práctica", value="baja"),
        ],
        style=UMBRAL_STYLE,
    ).ask()

    # Evaluar resultado
    has_debt = assessment in ("parcial", "baja")
    empty_answers = sum(1 for a in answers if not a.strip())

    if empty_answers > len(answers) // 2:
        print_warning("Demasiadas respuestas vacías. Se registra deuda.")
        has_debt = True

    # Guardar checkpoint
    checkpoint = ComprehensionCheckpoint(
        ede_slug=ede_slug,
        role=config.role.value,
        questions=[g.text for g in gate_questions],
        question_categories=[g.category for g in gate_questions],
        concepts_evaluated=[g.concept for g in gate_questions],
        answers=answers,
        self_assessment=assessment or "",
        has_debt=has_debt,
    )
    path = save_checkpoint(project_root, checkpoint)

    # Actualizar perfil
    if has_debt:
        profile.comprehension_debt += 1
        print_warning("Comprehension debt registrada.")
    else:
        print_success("Comprensión verificada sin deuda ✓")

    profile.total_prs += 1
    save_profile(project_root, profile)

    print_success(f"Checkpoint guardado: {path.name}")
    print_next_step("umbral next")
