"""Cliente del juez para OpenAI (GPT)."""

from __future__ import annotations

import json
import logging
import os
from urllib.request import Request, urlopen
from urllib.error import URLError

from umbral.judge.base_client import BaseJudgeClient

logger = logging.getLogger(__name__)

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


class OpenAIJudgeClient(BaseJudgeClient):
    """Cliente que usa la API de OpenAI para el juez LLM."""

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self._model = model

    @property
    def provider_name(self) -> str:
        return "openai"

    def complete(
        self,
        system: str,
        user: str,
        max_tokens: int = 800,
        temperature: float = 0.2,
    ) -> str | None:
        """Llama a la API de OpenAI."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY no configurada.")
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
                OPENAI_API_URL,
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
            logger.error(f"Error llamando a OpenAI: {e}")
            return None
