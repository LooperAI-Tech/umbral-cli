"""Modelo Pydantic de la EDE (Estructura de Decisión Explícita).

Sección 2.3 del plan — Niveles de EDE por rol:
  - Nivel 1 (Explorer): 2 componentes (Qué/Cómo + Por Qué básico)
  - Nivel 2 (Navigator): 4 componentes (+ Qué No Hacer + Qué Sigue)
  - Nivel 3 (Anchor): 4+ componentes (+ tool bindings, ADR formal, blast radius)

Formato: frontmatter YAML + body Markdown con H2 por componente.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, model_validator


class EDEStatus(str, Enum):
    """Estado de una EDE en su ciclo de vida."""

    DRAFT = "draft"
    APPROVED = "approved"


class EDELevel(int, Enum):
    """Niveles de EDE (sección 2.3.1 del plan)."""

    LEVEL_1 = 1  # Explorer — 2 componentes
    LEVEL_2 = 2  # Navigator — 4 componentes
    LEVEL_3 = 3  # Anchor — 4+ componentes


# Componentes requeridos por nivel
REQUIRED_COMPONENTS: dict[int, list[str]] = {
    1: ["what_and_how", "why"],
    2: ["what_and_how", "why", "what_not_to_do", "what_next"],
    3: ["what_and_how", "why", "what_not_to_do", "what_next"],
}

# Nombres legibles de los componentes
COMPONENT_NAMES: dict[str, str] = {
    "what_and_how": "Qué y Cómo",
    "why": "Por Qué",
    "what_not_to_do": "Qué No Hacer",
    "what_next": "Qué Sigue",
}


class EDEMetadata(BaseModel):
    """Metadatos de la EDE (frontmatter YAML).

    Attributes:
        slug: Identificador único en kebab-case.
        title: Título descriptivo de la EDE.
        level: Nivel de la EDE (1, 2 o 3).
        status: Estado del ciclo de vida (draft/approved).
        bounded_context: Contexto delimitado que cubre.
        scale: Escala del proyecto al momento de creación.
        created_at: Fecha de creación.
        updated_at: Fecha de última actualización.
    """

    slug: str
    title: str
    level: int = Field(ge=1, le=3)
    status: EDEStatus = EDEStatus.DRAFT
    bounded_context: str = ""
    scale: str = ""
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )


class EDE(BaseModel):
    """Modelo completo de una EDE.

    Una EDE tiene metadatos (frontmatter) y componentes (body).
    Los componentes requeridos dependen del nivel.
    """

    metadata: EDEMetadata
    what_and_how: str = ""
    why: str = ""
    what_not_to_do: str = ""
    what_next: str = ""

    def get_component(self, name: str) -> str:
        """Obtiene el contenido de un componente por nombre."""
        return getattr(self, name, "")

    def set_component(self, name: str, content: str) -> None:
        """Establece el contenido de un componente."""
        if hasattr(self, name):
            setattr(self, name, content)

    @property
    def required_components(self) -> list[str]:
        """Retorna los componentes requeridos para el nivel de esta EDE."""
        return REQUIRED_COMPONENTS.get(self.metadata.level, [])

    def validate_components(self) -> list[str]:
        """Valida que los componentes requeridos tengan contenido.

        Returns:
            Lista de nombres de componentes faltantes (vacía si todo OK).
        """
        missing = []
        for comp in self.required_components:
            content = self.get_component(comp)
            if not content or not content.strip():
                missing.append(comp)
        return missing

    @property
    def is_valid(self) -> bool:
        """Verifica si la EDE tiene todos los componentes requeridos."""
        return len(self.validate_components()) == 0
