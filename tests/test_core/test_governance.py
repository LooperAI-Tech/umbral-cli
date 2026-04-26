"""Tests para core/governance.py."""

from umbral.core.ede import EDE, EDEMetadata, EDEStatus
from umbral.core.governance import GovernanceMode, governance_for_bounded_context


def test_no_ede_supervised():
    mode, _ = governance_for_bounded_context("payment", [])
    assert mode == GovernanceMode.SUPERVISED


def test_approved_l1_hybrid():
    ede = EDE(
        metadata=EDEMetadata(
            slug="x",
            title="T",
            level=1,
            status=EDEStatus.APPROVED,
            bounded_context="payment",
        ),
        what_and_how="A",
        why="B",
    )
    m, _ = governance_for_bounded_context("payment", [ede])
    assert m == GovernanceMode.HYBRID


def test_approved_l3_autonomous():
    ede = EDE(
        metadata=EDEMetadata(
            slug="p",
            title="P",
            level=3,
            status=EDEStatus.APPROVED,
        ),
        what_and_how="A" * 20,
        why="B" * 20,
        what_not_to_do="C" * 20,
        what_next="D" * 20,
    )
    m, _ = governance_for_bounded_context("p", [ede])
    assert m == GovernanceMode.AUTONOMOUS
