"""Prompts interactivos con Questionary para Umbral CLI."""

from __future__ import annotations

import os

import questionary
from questionary import Style

from umbral.core.config import (
    AgentType,
    JudgeMode,
    LLMProvider,
    PROVIDER_DEFAULT_MODELS,
    PROVIDER_ENV_KEYS,
    Role,
    Scale,
)

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

_OTHER_SENTINEL = "__other__"

DOMAIN_CHOICES = [
    questionary.Choice("🌐 Web", value="web"),
    questionary.Choice("📱 Mobile", value="mobile"),
    questionary.Choice("📊 Data Science", value="data-science"),
    questionary.Choice("🤖 Machine Learning / AI", value="ml-ai"),
    questionary.Choice("⚙️  DevOps / Infra", value="devops"),
    questionary.Choice("🔌 Backend / API", value="backend"),
    questionary.Choice("🎮 Videojuegos", value="games"),
    questionary.Choice("🔒 Seguridad / Ciberseguridad", value="security"),
    questionary.Choice("📦 CLI / Herramientas", value="cli"),
    questionary.Choice("✏️  Otro (escribir manualmente)", value=_OTHER_SENTINEL),
]


def ask_project_name(default: str = "") -> str:
    """Pregunta el nombre del proyecto."""
    return questionary.text(
        "Nombre del proyecto:",
        default=default,
        style=UMBRAL_STYLE,
    ).ask()


def ask_domain() -> str | None:
    """Pregunta el dominio del proyecto con selector y fallback manual."""
    value = questionary.select(
        "¿Cuál es el dominio del proyecto?",
        choices=DOMAIN_CHOICES,
        style=UMBRAL_STYLE,
    ).ask()
    if value is None:
        return None
    if value == _OTHER_SENTINEL:
        return questionary.text(
            "Escribe el dominio de tu proyecto:",
            style=UMBRAL_STYLE,
        ).ask()
    return value


def ask_llm_provider() -> LLMProvider | None:
    """Pregunta qué proveedor de LLM quiere usar."""
    choices = [
        questionary.Choice("🟠 Anthropic (Claude)", value="anthropic"),
        questionary.Choice("🔵 Google Gemini", value="gemini"),
        questionary.Choice("🟢 OpenAI (GPT)", value="openai"),
        questionary.Choice("🟣 OpenRouter (multi-modelo)", value="openrouter"),
    ]
    value = questionary.select(
        "¿Qué proveedor de LLM quieres usar para el juez?",
        choices=choices,
        style=UMBRAL_STYLE,
    ).ask()
    if value is None:
        return None
    return LLMProvider(value)


def ask_api_key(provider: LLMProvider) -> str | None:
    """Solicita la API key para el proveedor elegido.

    Si ya existe en el entorno, ofrece usarla; si no, la pide.
    Retorna la key (o None si el usuario cancela).
    """
    env_var = PROVIDER_ENV_KEYS[provider.value]
    existing = os.environ.get(env_var, "").strip()

    if existing:
        masked = existing[:4] + "..." + existing[-4:]
        use_existing = questionary.confirm(
            f"{env_var} detectada ({masked}). ¿Usar esta key?",
            default=True,
            style=UMBRAL_STYLE,
        ).ask()
        if use_existing is None:
            return None
        if use_existing:
            return existing

    key = questionary.password(
        f"Pega tu {env_var}:",
        style=UMBRAL_STYLE,
    ).ask()
    return key


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
