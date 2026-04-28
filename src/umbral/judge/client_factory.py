"""Factory de clientes del juez LLM (sección 9.2 del plan).

Selecciona el cliente según judge.provider en umbral.yaml.
"""

from __future__ import annotations

from umbral.judge.base_client import BaseJudgeClient
from umbral.judge.clients.anthropic_client import AnthropicJudgeClient
from umbral.judge.clients.gemini_client import GeminiJudgeClient
from umbral.judge.clients.openai_client import OpenAIJudgeClient
from umbral.judge.clients.openrouter_client import OpenRouterJudgeClient


def create_judge_client(
    provider: str, model: str = ""
) -> BaseJudgeClient:
    """Crea el cliente del juez según el proveedor configurado.

    Args:
        provider: Nombre del proveedor (anthropic, gemini, openai, openrouter).
        model: ID del modelo en el proveedor (p. ej. claude-haiku-4-5, gemini-2.0-flash).

    Returns:
        Instancia del cliente correspondiente.

    Raises:
        ValueError: Si el proveedor no es soportado.
    """
    m = (model or "").strip()
    if provider == "anthropic":
        return AnthropicJudgeClient(model=m or "claude-haiku-4-5")
    elif provider == "gemini":
        return GeminiJudgeClient(model=m or "gemini-2.0-flash")
    elif provider == "openai":
        return OpenAIJudgeClient(model=m or "gpt-4o-mini")
    elif provider == "openrouter":
        return OpenRouterJudgeClient(model=m or "anthropic/claude-haiku-4-5")
    else:
        raise ValueError(
            f"Proveedor no soportado: {provider}. "
            "Opciones: anthropic, gemini, openai, openrouter."
        )
