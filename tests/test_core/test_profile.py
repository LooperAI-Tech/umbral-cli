"""Tests para core/profile.py."""

from umbral.core.profile import CognitiveProfile, ConceptStatus


def test_concept_status_default():
    """Verifica que un concepto empieza como no aprendido."""
    concept = ConceptStatus(name="overfitting")
    assert concept.name == "overfitting"
    assert concept.learned is False


def test_cognitive_profile_empty():
    """Verifica un perfil vacío."""
    profile = CognitiveProfile()
    assert profile.domain_concepts == []
    assert profile.system_contexts == []
    assert profile.context_mastery == {}
    assert profile.edes_written == {"level_1": 0, "level_2": 0, "level_3": 0}
    assert profile.comprehension_debt == 0
    assert profile.total_prs == 0
    assert profile.consolidation_runs == 0
    assert profile.next_feature_known_area is True


def test_dkc_empty():
    """DKC con 0 conceptos debe ser 0."""
    profile = CognitiveProfile()
    assert profile.dkc == 0.0


def test_dkc_with_concepts():
    """DKC con conceptos parcialmente aprendidos."""
    profile = CognitiveProfile(
        domain_concepts=[
            ConceptStatus(name="a", learned=True),
            ConceptStatus(name="b", learned=False),
            ConceptStatus(name="c", learned=True),
            ConceptStatus(name="d", learned=False),
        ]
    )
    assert profile.dkc == 50.0


def test_dkc_all_learned():
    """DKC con todos los conceptos aprendidos."""
    profile = CognitiveProfile(
        domain_concepts=[
            ConceptStatus(name="a", learned=True),
            ConceptStatus(name="b", learned=True),
        ]
    )
    assert profile.dkc == 100.0


def test_cdr_no_prs():
    """CDR sin PRs debe ser 0."""
    profile = CognitiveProfile()
    assert profile.cdr == 0.0


def test_cdr_with_debt():
    """CDR con deuda de comprensión."""
    profile = CognitiveProfile(comprehension_debt=2, total_prs=10)
    assert profile.cdr == 20.0


def test_profile_serialization():
    """Verifica round-trip de serialización."""
    profile = CognitiveProfile(
        domain_concepts=[ConceptStatus(name="x", learned=True)],
        system_contexts=["auth"],
        edes_written={"level_1": 2, "level_2": 0, "level_3": 0},
    )
    data = profile.model_dump(mode="json")
    restored = CognitiveProfile(**data)
    assert restored.domain_concepts[0].name == "x"
    assert restored.domain_concepts[0].learned is True
    assert restored.system_contexts == ["auth"]
