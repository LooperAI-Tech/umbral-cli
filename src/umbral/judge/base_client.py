"""Interfaz abstracta del cliente del juez LLM (sección 9.2 del plan).

Un único método: complete(system, user, max_tokens, temperature) -> str | None
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseJudgeClient(ABC):
    """Interfaz abstracta que todos los clientes del juez deben implementar."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Nombre del proveedor."""
        ...

    @abstractmethod
    def complete(
        self,
        system: str,
        user: str,
        max_tokens: int = 800,
        temperature: float = 0.2,
    ) -> str | None:
        """Envía un prompt al LLM y retorna la respuesta.

        Args:
            system: Prompt de sistema (rúbrica).
            user: Prompt de usuario (artefactos a evaluar).
            max_tokens: Máximo de tokens en la respuesta.
            temperature: Temperatura de generación.

        Returns:
            Respuesta del LLM como string, o None si falla.
        """
        ...
