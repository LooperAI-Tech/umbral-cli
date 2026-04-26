"""Tests para validation/phase_validator.py — Capa 1."""

from umbral.core.config import ProjectConfig, Scale, Role
from umbral.core.ede import EDE, EDEMetadata, EDEStatus
from umbral.storage.config_store import save_config
from umbral.storage.ede_store import save_ede
from umbral.storage.paths import ensure_umbral_structure, get_phases_dir
from umbral.validation.phase_validator import validate_phase


def _setup(tmp_path, phase=0):
    ensure_umbral_structure(tmp_path)
    config = ProjectConfig(
        project_name="val-test", domain="web", current_phase=phase
    )
    save_config(tmp_path, config)
    return config


class TestDiscoveryValidation:
    """Tests para validación de Fase 0."""

    def test_missing_all(self, tmp_path):
        config = _setup(tmp_path, phase=0)
        result = validate_phase(tmp_path, config)
        assert not result.passed
        assert len(result.gaps) == 2

    def test_with_notes_and_map(self, tmp_path):
        config = _setup(tmp_path, phase=0)
        phases = get_phases_dir(tmp_path)
        (phases / "discovery-notes.md").write_text("A" * 60, encoding="utf-8")
        (tmp_path / ".umbral" / "domain-map.yaml").write_text(
            "concepts: [a]", encoding="utf-8"
        )
        result = validate_phase(tmp_path, config)
        assert result.passed

    def test_notes_too_short(self, tmp_path):
        config = _setup(tmp_path, phase=0)
        phases = get_phases_dir(tmp_path)
        (phases / "discovery-notes.md").write_text("short", encoding="utf-8")
        (tmp_path / ".umbral" / "domain-map.yaml").write_text("x", encoding="utf-8")
        result = validate_phase(tmp_path, config)
        assert not result.passed


class TestArticulationValidation:
    """Tests para validación de Fase 1."""

    def test_missing_spec(self, tmp_path):
        config = _setup(tmp_path, phase=1)
        result = validate_phase(tmp_path, config)
        assert not result.passed

    def test_with_spec(self, tmp_path):
        config = _setup(tmp_path, phase=1)
        phases = get_phases_dir(tmp_path)
        (phases / "spec-test.md").write_text(
            "caso borde\nmodo de falla\nalcance definido\ndatos de entrada",
            encoding="utf-8",
        )
        result = validate_phase(tmp_path, config)
        assert result.passed


class TestDesignValidation:
    """Tests para validación de Fase 2."""

    def test_no_edes(self, tmp_path):
        config = _setup(tmp_path, phase=2)
        result = validate_phase(tmp_path, config)
        assert not result.passed

    def test_draft_ede(self, tmp_path):
        config = _setup(tmp_path, phase=2)
        ede = EDE(
            metadata=EDEMetadata(slug="test", title="Test", level=1),
            what_and_how="X", why="Y",
        )
        save_ede(tmp_path, ede)
        result = validate_phase(tmp_path, config)
        assert not result.passed  # Not approved

    def test_approved_ede(self, tmp_path):
        config = _setup(tmp_path, phase=2)
        ede = EDE(
            metadata=EDEMetadata(
                slug="test", title="Test", level=1,
                status=EDEStatus.APPROVED
            ),
            what_and_how="X", why="Y",
        )
        save_ede(tmp_path, ede)
        result = validate_phase(tmp_path, config)
        assert result.passed


class TestVerificationValidation:
    """Tests para validación de Fase 4."""

    def test_no_checkpoint(self, tmp_path):
        config = _setup(tmp_path, phase=4)
        result = validate_phase(tmp_path, config)
        assert not result.passed

    def test_with_checkpoint(self, tmp_path):
        config = _setup(tmp_path, phase=4)
        phases = get_phases_dir(tmp_path)
        (phases / "checkpoint-test.yaml").write_text(
            """questions: ["Q1", "Q2"]
answers:
  - "Explico con detalle el primer concepto y por qué importa en el contexto del proyecto de forma concreta."
  - "Segunda respuesta sustancial con varias palabras para demostrar comprensión clara y útil."
self_assessment: "alta"
""",
            encoding="utf-8",
        )
        result = validate_phase(tmp_path, config)
        assert result.passed

    def test_checkpoint_too_shallow_fails(self, tmp_path):
        config = _setup(tmp_path, phase=4)
        phases = get_phases_dir(tmp_path)
        (phases / "checkpoint-bad.yaml").write_text(
            """questions: ["Q1", "Q2"]
answers: ["sí", "ok"]
self_assessment: "alta"
""",
            encoding="utf-8",
        )
        result = validate_phase(tmp_path, config)
        assert not result.passed
