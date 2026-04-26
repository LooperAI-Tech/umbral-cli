"""Prompts interactivos con Questionary para Umbral CLI."""

from __future__ import annotations

import questionary
from questionary import Style

from umbral.core.config import AgentType, JudgeMode, Role, Scale

# Estilo personalizado para los prompts
UMBRAL_STYLE = Style(
    [
        ("qmark", "fg:cyan bold"),
        ("question", "bold"),
        ("answer", "fg:cyan"),
        ("pointer", "fg:cyan bold"),
        ("highlighted", "fg:cyan bold"),
        ("selected", "fg:cyan"),
    ]
)


def ask_project_name(default: str = "") -> str:
    """Pregunta el nombre del proyecto."""
    return questionary.text(
        "Nombre del proyecto:",
        default=default,
        style=UMBRAL_STYLE,
    ).ask()


def ask_domain() -> str:
    """Pregunta el dominio del proyecto."""
    return questionary.text(
        "Dominio del proyecto (ej: web, data-science, mobile, devops):",
        style=UMBRAL_STYLE,
    ).ask()


def ask_scale() -> Scale:
    """Pregunta la escala del proyecto."""
    choices = [
        questionary.Choice("🧪 Aprender haciendo (learning)", value="learning"),
        questionary.Choice("🚀 Validar una idea (MVP)", value="mvp"),
        questionary.Choice("🏗️  Producto escalable (startup)", value="startup"),
    ]
    value = questionary.select(
        "¿Cuál es el objetivo del proyecto?",
        choices=choices,
        style=UMBRAL_STYLE,
    ).ask()
    return Scale(value)


def ask_role() -> Role:
    """Pregunta el nivel de experiencia del usuario."""
    choices = [
        questionary.Choice(
            "🔰 Principiante — Estoy aprendiendo (Explorer)", value="explorer"
        ),
        questionary.Choice(
            "🧭 Intermedio — Tengo experiencia (Navigator)", value="navigator"
        ),
        questionary.Choice(
            "⚓ Avanzado — Domino el área (Anchor)", value="anchor"
        ),
    ]
    value = questionary.select(
        "¿Cuál es tu nivel de experiencia en este dominio?",
        choices=choices,
        style=UMBRAL_STYLE,
    ).ask()
    return Role(value)


def ask_agent() -> AgentType:
    """Pregunta qué agente de IA usa el usuario."""
    choices = [
        questionary.Choice("Claude Code", value="claude-code"),
        questionary.Choice("Cursor", value="cursor"),
    ]
    value = questionary.select(
        "¿Qué agente de IA usas?",
        choices=choices,
        style=UMBRAL_STYLE,
    ).ask()
    return AgentType(value)


def ask_judge_mode(has_api_key: bool) -> JudgeMode:
    """Pregunta el modo del juez LLM.

    Si no hay API key detectada, advierte antes de ofrecer online.
    """
    if not has_api_key:
        choices = [
            questionary.Choice(
                "📴 Offline — Solo validación estructural (sin API key detectada)",
                value="offline",
            ),
            questionary.Choice(
                "🌐 Online — Configurar API key después",
                value="online",
            ),
        ]
    else:
        choices = [
            questionary.Choice(
                "🌐 Online — Validación estructural + semántica (API key detectada ✓)",
                value="online",
            ),
            questionary.Choice(
                "📴 Offline — Solo validación estructural",
                value="offline",
            ),
        ]
    value = questionary.select(
        "Modo del juez LLM:",
        choices=choices,
        style=UMBRAL_STYLE,
    ).ask()
    return JudgeMode(value)
