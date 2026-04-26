"""Tests para core/promotion.py."""

from umbral.core.config import Role
from umbral.core.ede import EDE, EDEMetadata, EDEStatus
from umbral.core.profile import CognitiveProfile
from umbral.core.promotion import evaluate_role_promotion


def _ede(slug, level, approved=True) -> EDE:
    st = EDEStatus.APPROVED if approved else EDEStatus.DRAFT
    wn = "N" * 10
    wnx = "S" * 10
    if level >= 2:
        return EDE(
            metadata=EDEMetadata(
                slug=slug, title=slug, level=level, status=st, bounded_context=slug
            ),
            what_and_how="Q" * 10,
            why="R" * 10,
            what_not_to_do=wn,
            what_next=wnx,
        )
    return EDE(
        metadata=EDEMetadata(
            slug=slug, title=slug, level=level, status=st, bounded_context=slug
        ),
        what_and_how="Q" * 10,
        why="R" * 10,
    )


def test_explorer_to_navigator():
    from umbral.core.profile import ConceptStatus

    edes = [_ede("a", 1), _ede("b", 1), _ede("c", 1)]
    profile = CognitiveProfile(
        domain_concepts=[
            ConceptStatus(name="x", learned=True),
            ConceptStatus(name="y", learned=True),
        ]
    )  # 100% dkc, 3 EDEs N1
    r = evaluate_role_promotion(Role.EXPLORER, profile, edes)
    assert r.promoted
    assert r.new_role == Role.NAVIGATOR


def test_navigator_to_anchor():
    edes = [_ede("a", 2)]
    p = CognitiveProfile(
        context_mastery={"a": 85.0},
    )
    r = evaluate_role_promotion(Role.NAVIGATOR, p, edes)
    assert r.promoted
    assert r.new_role == Role.ANCHOR
