"""Modelo Pydantic del Perfil Cognitivo (sección 2.8 del plan).

El Perfil Cognitivo tiene dos dimensiones:
  - Dominio técnico: conceptos del dominio del proyecto.
  - Sistema: conocimiento sobre el sistema construido.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ConceptStatus(BaseModel):
    """Estado de un concepto en el Mapa de Dominio."""

    name: str
    learned: bool = False  # True = ✅, False = ⬜


class CognitiveProfile(BaseModel):
    """Perfil Cognitivo del usuario.

    Persistido en .umbral/profile.yaml.

    Attributes:
        domain_concepts: Lista de conceptos del dominio técnico.
        system_contexts: Lista de bounded contexts cubiertos.
        edes_written: Cantidad de EDEs escritas por nivel.
        comprehension_debt: PRs con deuda de comprensión.
        total_prs: Total de PRs evaluados.
    """

    domain_concepts: list[ConceptStatus] = Field(default_factory=list)
    system_contexts: list[str] = Field(default_factory=list)
    edes_written: dict[str, int] = Field(
        default_factory=lambda: {"level_1": 0, "level_2": 0, "level_3": 0}
    )
    comprehension_debt: int = 0
    total_prs: int = 0

    @property
    def dkc(self) -> float:
        """Domain Knowledge Coverage — % de conceptos aprendidos."""
        if not self.domain_concepts:
            return 0.0
        learned = sum(1 for c in self.domain_concepts if c.learned)
        return (learned / len(self.domain_concepts)) * 100

    @property
    def cdr(self) -> float:
        """Comprehension Debt Ratio — PRs con deuda / total."""
        if self.total_prs == 0:
            return 0.0
        return (self.comprehension_debt / self.total_prs) * 100
