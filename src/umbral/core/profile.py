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
        domain_concepts: Dimensión dominio — conceptos del mapa (sección 2.8).
        system_contexts: Dimensión sistema — bounded contexts cubiertos.
        context_mastery: Comprensión 0-100 % por contexto (promoción Anchor, 2.6.3).
        edes_written: EDEs por nivel (se actualiza en consolidación).
        comprehension_debt: PRs con deuda de comprensión.
        total_prs: Total de PRs evaluados.
        consolidation_runs: Veces que se ejecutó `umbral consolidate`.
        next_feature_known_area: Si el próximo feature es área conocida (2.6.4).
    """

    domain_concepts: list[ConceptStatus] = Field(default_factory=list)
    system_contexts: list[str] = Field(default_factory=list)
    context_mastery: dict[str, float] = Field(default_factory=dict)
    edes_written: dict[str, int] = Field(
        default_factory=lambda: {"level_1": 0, "level_2": 0, "level_3": 0}
    )
    comprehension_debt: int = 0
    total_prs: int = 0
    consolidation_runs: int = 0
    next_feature_known_area: bool = True

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
