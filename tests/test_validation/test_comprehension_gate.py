"""Tests para validation/comprehension_gate.py."""

from umbral.core.config import Role
from umbral.core.profile import CognitiveProfile, ConceptStatus
from umbral.storage.paths import ensure_umbral_structure
from umbral.validation.comprehension_gate import (
    ComprehensionCheckpoint,
    generate_questions,
    save_checkpoint,
)


class TestGenerateQuestions:
    """Tests para generación de preguntas."""

    def test_explorer_questions(self):
        profile = CognitiveProfile()
        questions = generate_questions(Role.EXPLORER, profile)
        assert 2 <= len(questions) <= 5

    def test_navigator_questions(self):
        profile = CognitiveProfile()
        questions = generate_questions(Role.NAVIGATOR, profile)
        assert 3 <= len(questions) <= 7

    def test_anchor_questions(self):
        profile = CognitiveProfile()
        questions = generate_questions(Role.ANCHOR, profile)
        assert 3 <= len(questions) <= 7

    def test_adds_concept_questions(self):
        profile = CognitiveProfile(
            domain_concepts=[
                ConceptStatus(name="REST", learned=False),
                ConceptStatus(name="HTTP", learned=True),
            ]
        )
        questions = generate_questions(Role.EXPLORER, profile)
        concept_qs = [q for q in questions if "REST" in q]
        assert len(concept_qs) >= 1


class TestCheckpoint:
    """Tests para persistencia de checkpoints."""

    def test_save_checkpoint(self, tmp_path):
        ensure_umbral_structure(tmp_path)
        checkpoint = ComprehensionCheckpoint(
            ede_slug="auth",
            role="explorer",
            questions=["¿Qué hace X?"],
            answers=["X hace Y"],
            self_assessment="alta",
            has_debt=False,
        )
        path = save_checkpoint(tmp_path, checkpoint)
        assert path.exists()
        assert "checkpoint-auth.yaml" in path.name
        content = path.read_text(encoding="utf-8")
        assert "auth" in content

    def test_checkpoint_with_debt(self, tmp_path):
        ensure_umbral_structure(tmp_path)
        checkpoint = ComprehensionCheckpoint(
            ede_slug="api",
            role="navigator",
            questions=["Q1", "Q2"],
            answers=["A1", ""],
            self_assessment="parcial",
            has_debt=True,
        )
        path = save_checkpoint(tmp_path, checkpoint)
        content = path.read_text(encoding="utf-8")
        assert "has_debt: true" in content
