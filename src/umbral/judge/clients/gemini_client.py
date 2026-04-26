"""Cliente del juez para Google Gemini."""

from __future__ import annotations

import json
import logging
import os
from urllib.request import Request, urlopen
from urllib.error import URLError

from umbral.judge.base_client import BaseJudgeClient

logger = logging.getLogger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiJudgeClient(BaseJudgeClient):
    """Cliente que usa la API REST de Gemini para el juez LLM."""

    def __init__(self, model: str = "gemini-2.0-flash") -> None:
        self._model = model

    @property
    def provider_name(self) -> str:
        return "gemini"

    def complete(
        self,
        system: str,
        user: str,
        max_tokens: int = 800,
        temperature: float = 0.2,
    ) -> str | None:
        """Llama a la API de Gemini vía HTTP."""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY no configurada.")
            return None

        try:
            url = f"{GEMINI_API_URL}/{self._model}:generateContent?key={api_key}"

            payload = {
                "system_instruction": {"parts": [{"text": system}]},
                "contents": [{"parts": [{"text": user}]}],
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": temperature,
                },
            }

            req = Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (URLError, KeyError, Exception) as e:
            logger.error(f"Error llamando a Gemini: {e}")
            return None
