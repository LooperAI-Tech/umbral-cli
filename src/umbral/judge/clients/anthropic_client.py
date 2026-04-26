"""Cliente del juez para Anthropic (Claude)."""

from __future__ import annotations

import os
import logging

from umbral.judge.base_client import BaseJudgeClient

logger = logging.getLogger(__name__)


class AnthropicJudgeClient(BaseJudgeClient):
    """Cliente que usa la API de Anthropic para el juez LLM."""

    def __init__(self, model: str = "claude-haiku-4-5") -> None:
        self._model = model

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def complete(
        self,
        system: str,
        user: str,
        max_tokens: int = 800,
        temperature: float = 0.2,
    ) -> str | None:
        """Llama a la API de Anthropic."""
        try:
            import anthropic
        except ImportError:
            logger.warning("anthropic SDK no instalado.")
            return None

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY no configurada.")
            return None

        try:
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error llamando a Anthropic: {e}")
            return None
