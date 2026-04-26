"""Schema Pydantic del veredicto del juez LLM (sección 9.3 del plan)."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class VerdictStatus(str, Enum):
    """Estado del veredicto del juez."""

    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    NEEDS_REVISION = "needs_revision"


class Gap(BaseModel):
    """Un gap detectado por el juez.

    Attributes:
        category: Categoría del gap (edge_case, rationale, scope, etc.)
        description: Descripción del gap.
        severity: Severidad (high, medium, low).
    """

    category: str
    description: str
    severity: str = "medium"


class JudgeVerdict(BaseModel):
    """Veredicto completo del juez LLM.

    Attributes:
        phase: Nombre de la fase evaluada.
        status: Estado del veredicto.
        confidence: Nivel de confianza (0.0 a 1.0).
        summary: Resumen del veredicto.
        gaps: Lista de gaps detectados.
        next_action: Acción sugerida al usuario.
        artifacts_reviewed: Lista de artefactos revisados.
    """

    phase: str
    status: VerdictStatus
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    summary: str = ""
    gaps: list[Gap] = Field(default_factory=list)
    next_action: str = ""
    artifacts_reviewed: list[str] = Field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        """Verifica si el veredicto permite avanzar."""
        return self.status == VerdictStatus.COMPLETE

    @property
    def has_high_severity_gaps(self) -> bool:
        """Verifica si hay gaps de alta severidad."""
        return any(g.severity == "high" for g in self.gaps)
