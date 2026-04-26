"""Factory de clientes del juez LLM (sección 9.2 del plan).

Selecciona el cliente según judge.provider en umbral.yaml.
"""

from __future__ import annotations

from umbral.judge.base_client import BaseJudgeClient
from umbral.judge.clients.anthropic_client import AnthropicJudgeClient
from umbral.judge.clients.gemini_client import GeminiJudgeClient
from umbral.judge.clients.openrouter_client import OpenRouterJudgeClient


def create_judge_client(
    provider: str, model: str = ""
) -> BaseJudgeClient:
    """Crea el cliente del juez según el proveedor configurado.

    Args:
        provider: Nombre del proveedor (anthropic, gemini, openrouter).
        model: Modelo específico (solo usado por openrouter).

    Returns:
        Instancia del cliente correspondiente.

    Raises:
        ValueError: Si el proveedor no es soportado.
    """
    if provider == "anthropic":
        return AnthropicJudgeClient()
    elif provider == "gemini":
        return GeminiJudgeClient()
    elif provider == "openrouter":
        return OpenRouterJudgeClient(model=model or "anthropic/claude-haiku-4-5")
    else:
        raise ValueError(
            f"Proveedor no soportado: {provider}. "
            "Opciones: anthropic, gemini, openrouter."
        )
