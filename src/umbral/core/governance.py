"""Governance Gradient por bounded context (sección 2.7)."""

from __future__ import annotations

from enum import Enum

from umbral.core.ede import EDE, EDEStatus, EDELevel


class GovernanceMode(str, Enum):
    """Autonomía del agente según madurez de la EDE en el contexto."""

    SUPERVISED = "supervisado"  # Sin EDE
    HYBRID = "hibrido"  # EDE N1–2
    AUTONOMOUS = "autonomo"  # EDE N3 completa


def _matches_context(ede: EDE, context: str) -> bool:
    ctx = (ede.metadata.bounded_context or ede.metadata.slug or "").strip()
    if not context:
        return True
    return context == ctx or ede.metadata.slug == context


def governance_for_bounded_context(
    context: str, edes: list[EDE]
) -> tuple[GovernanceMode, str]:
    """Calcula el modo y una descripción breve.

    Returns:
        Tupla (modo, explicación).
    """
    relevant = [e for e in edes if _matches_context(e, context)]
    if not relevant:
        return (
            GovernanceMode.SUPERVISED,
            "Sin EDE: revisión humana completa y comprehension check.",
        )

    approved = [e for e in relevant if e.metadata.status == EDEStatus.APPROVED]
    if not approved:
        return (
            GovernanceMode.SUPERVISED,
            "Solo EDEs en draft: tratar como supervisado.",
        )

    # Mayor nivel aprobado en el contexto
    max_level = max(e.metadata.level for e in approved)
    if max_level >= EDELevel.LEVEL_3:
        return (
            GovernanceMode.AUTONOMOUS,
            "EDE Nivel 3 aprobada: operación autónoma dentro de la EDE.",
        )
    return (
        GovernanceMode.HYBRID,
        "EDE N1–2: gates en cambios de alto impacto.",
    )
