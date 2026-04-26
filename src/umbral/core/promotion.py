"""Evaluación de promoción de roles (sección 2.6.3)."""

from __future__ import annotations

from dataclasses import dataclass

from umbral.core.config import Role
from umbral.core.ede import EDE, EDEStatus
from umbral.core.profile import CognitiveProfile


@dataclass(frozen=True)
class PromotionResult:
    """Resultado de evaluación de promoción."""

    new_role: Role
    message: str
    promoted: bool


def evaluate_role_promotion(
    current: Role, profile: CognitiveProfile, edes: list[EDE]
) -> PromotionResult:
    """Decide si el usuario asciende de rol.

    Criterios (plan):
    - Explorer → Navigator: ≥ 3 EDEs N1 exitosas, DKC ≥ 50 %.
    - Navigator → Anchor: al menos 1 EDE N2+ exitosa, comprensión ≥ 80 % en
      al menos un bounded context.
    - Anchor: sin ascenso.
    """
    if current == Role.ANCHOR:
        return PromotionResult(
            new_role=Role.ANCHOR,
            message="Ya estás en el rol máximo (Anchor).",
            promoted=False,
        )

    l1_ok = sum(
        1
        for e in edes
        if e.metadata.level == 1
        and e.metadata.status == EDEStatus.APPROVED
        and e.is_valid
    )
    l2p_ok = [
        e
        for e in edes
        if e.metadata.level >= 2
        and e.metadata.status == EDEStatus.APPROVED
        and e.is_valid
    ]
    has_anchor_context = any(v >= 80.0 for v in profile.context_mastery.values())

    if current == Role.EXPLORER:
        if l1_ok >= 3 and profile.dkc >= 50.0:
            return PromotionResult(
                new_role=Role.NAVIGATOR,
                message=(
                    f"Cumples criterios: {l1_ok} EDE(s) N1 aprobadas, "
                    f"DKC {profile.dkc:.1f} % ≥ 50 % → Navigator."
                ),
                promoted=True,
            )
        return PromotionResult(
            new_role=Role.EXPLORER,
            message=(
                f"Navigator requiere ≥ 3 EDEs N1 válidas (tienes {l1_ok}) y "
                f"DKC ≥ 50 % (tienes {profile.dkc:.1f} %)."
            ),
            promoted=False,
        )

    # Navigator
    if len(l2p_ok) >= 1 and has_anchor_context:
        return PromotionResult(
            new_role=Role.ANCHOR,
            message=(
                "Cumples criterios: al menos 1 EDE N2+ válida y "
                "mastery ≥ 80 % en un bounded context → Anchor."
            ),
            promoted=True,
        )
    return PromotionResult(
        new_role=Role.NAVIGATOR,
        message=(
            f"Anchor requiere EDE N2+ aprobada (tienes {len(l2p_ok)} válidas) y "
            f"al menos un contexto con mastery ≥ 80 % (contexts: {profile.context_mastery})."
        ),
        promoted=False,
    )
