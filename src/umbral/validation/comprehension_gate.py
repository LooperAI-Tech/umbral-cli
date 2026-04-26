"""Comprehension Gate — preguntas deterministas (sección 9.5/2.5 del plan).

Genera preguntas basadas en: conceptos tocados, rol del usuario,
y conceptos aún no verificados en el Perfil Cognitivo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from umbral.core.config import Role
from umbral.core.profile import CognitiveProfile
from umbral.storage.paths import get_phases_dir


# Preguntas por rol (sección 2.5.1)
EXPLORER_QUESTIONS = [
    "¿Por qué elegiste esta estructura y no otra?",
    "¿Qué pasa si llegan datos inesperados o vacíos?",
    "¿Puedes explicar con tus palabras qué hace cada parte?",
]

NAVIGATOR_QUESTIONS = [
    "¿Por qué esta estrategia y no la alternativa?",
    "¿Qué trade-off aceptamos con este diseño?",
    "¿Cómo afecta esto a la mantenibilidad del sistema?",
    "¿Qué modos de falla existen y cómo los manejamos?",
    "¿Qué invariantes debe mantener este módulo?",
]

ANCHOR_QUESTIONS = [
    "¿Cómo afecta este cambio al blast radius del servicio?",
    "¿Qué validators faltan para operar sin supervisión?",
    "¿Qué governance constraints aplican a este cambio?",
    "¿Cómo impacta esto en la deuda técnica existente?",
    "¿Qué métricas deberíamos monitorear tras este cambio?",
]


@dataclass(frozen=True)
class GateQuestion:
    """Pregunta del gate con metadatos (sección 2.5.3 — categoría y concepto)."""

    text: str
    category: str = "general"
    concept: str = ""


@dataclass
class ComprehensionCheckpoint:
    """Checkpoint del Comprehension Gate.

    Persiste preguntas, respuestas y autoevaluación.
    """

    ede_slug: str
    role: str
    questions: list[str] = field(default_factory=list)
    answers: list[str] = field(default_factory=list)
    self_assessment: str = ""
    has_debt: bool = False
    question_categories: list[str] = field(default_factory=list)
    concepts_evaluated: list[str] = field(default_factory=list)


def generate_questions(role: Role, profile: CognitiveProfile) -> list[GateQuestion]:
    """Genera preguntas de comprensión calibradas al rol.

    La cantidad varía por rol:
    - Explorer: 2-3 preguntas
    - Navigator: 3-5 preguntas
    - Anchor: 3-5 preguntas

    Se priorizan conceptos no verificados del perfil.
    """
    if role == Role.EXPLORER:
        base_texts = EXPLORER_QUESTIONS[:3]
        base_cats = ["conceptual", "práctica", "código"][: len(base_texts)]
    elif role == Role.NAVIGATOR:
        base_texts = NAVIGATOR_QUESTIONS[:5]
        base_cats = [
            "diseño",
            "trade-off",
            "mantenibilidad",
            "falla",
            "invariantes",
        ][: len(base_texts)]
    else:
        base_texts = ANCHOR_QUESTIONS[:5]
        base_cats = [
            "blast_radius",
            "governance",
            "gobernanza",
            "deuda_técnica",
            "observabilidad",
        ][: len(base_texts)]

    out: list[GateQuestion] = [
        GateQuestion(text=t, category=c, concept="")
        for t, c in zip(base_texts, base_cats, strict=False)
    ]

    # Agregar preguntas sobre conceptos no aprendidos
    pending = [c for c in profile.domain_concepts if not c.learned]
    for concept in pending[:2]:
        out.append(
            GateQuestion(
                text=(
                    f"Explica con tus palabras: ¿qué es '{concept.name}' "
                    "y por qué es relevante aquí?"
                ),
                category="dominio",
                concept=concept.name,
            )
        )

    return out


def save_checkpoint(
    project_root: Path, checkpoint: ComprehensionCheckpoint
) -> Path:
    """Guarda el checkpoint en disco.

    Args:
        project_root: Raíz del proyecto.
        checkpoint: Checkpoint a guardar.

    Returns:
        Path al archivo guardado.
    """
    phases_dir = get_phases_dir(project_root)
    phases_dir.mkdir(parents=True, exist_ok=True)

    path = phases_dir / f"checkpoint-{checkpoint.ede_slug}.yaml"
    data = {
        "ede_slug": checkpoint.ede_slug,
        "role": checkpoint.role,
        "questions": checkpoint.questions,
        "question_categories": checkpoint.question_categories,
        "concepts_evaluated": checkpoint.concepts_evaluated,
        "answers": checkpoint.answers,
        "self_assessment": checkpoint.self_assessment,
        "has_debt": checkpoint.has_debt,
    }
    path.write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True),
        encoding="utf-8",
    )
    return path
