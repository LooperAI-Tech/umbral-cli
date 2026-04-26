"""Cliente del juez para OpenRouter (multi-modelo)."""

from __future__ import annotations

import json
import logging
import os
from urllib.request import Request, urlopen
from urllib.error import URLError

from umbral.judge.base_client import BaseJudgeClient

logger = logging.getLogger(__name__)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterJudgeClient(BaseJudgeClient):
    """Cliente que usa la API de OpenRouter para el juez LLM."""

    def __init__(self, model: str = "anthropic/claude-haiku-4-5"):
        self._model = model

    @property
    def provider_name(self) -> str:
        return "openrouter"

    def complete(
        self,
        system: str,
        user: str,
        max_tokens: int = 800,
        temperature: float = 0.2,
    ) -> str | None:
        """Llama a la API de OpenRouter."""
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            logger.warning("OPENROUTER_API_KEY no configurada.")
            return None

        try:
            payload = {
                "model": self._model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            }

            req = Request(
                OPENROUTER_API_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                method="POST",
            )
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            return data["choices"][0]["message"]["content"]
        except (URLError, KeyError, Exception) as e:
            logger.error(f"Error llamando a OpenRouter: {e}")
            return None
