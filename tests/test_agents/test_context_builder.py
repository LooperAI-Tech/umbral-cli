"""Tests para agents/context_builder.py."""

from umbral.agents.context_builder import PromptContext, build_context
from umbral.core.config import ProjectConfig, Scale, Role
from umbral.core.ede import EDE, EDEMetadata
from umbral.core.profile import CognitiveProfile, ConceptStatus
from umbral.storage.config_store import save_config
from umbral.storage.ede_store import save_ede
from umbral.storage.paths import ensure_umbral_structure
from umbral.storage.profile_store import save_profile


def _setup_project(tmp_path, role=Role.EXPLORER, concepts=None):
    """Helper: crea proyecto con config, perfil y opcionalmente EDEs."""
    ensure_umbral_structure(tmp_path)
    config = ProjectConfig(
        project_name="ctx-test",
        domain="web",
        scale=Scale.MVP,
        role=role,
    )
    save_config(tmp_path, config)

    profile = CognitiveProfile(
        domain_concepts=concepts or [],
    )
    save_profile(tmp_path, profile)
    return config


class TestPromptContext:
    """Tests para el dataclass PromptContext."""

    def test_defaults(self):
        ctx = PromptContext()
        assert ctx.project_name == ""
        assert ctx.edes == []
        assert ctx.dkc == 0.0


class TestBuildContext:
    """Tests para la función build_context."""

    def test_basic_context(self, tmp_path):
        _setup_project(tmp_path)
        ctx = build_context(tmp_path)
        assert ctx.project_name == "ctx-test"
        assert ctx.domain == "web"
        assert ctx.scale == "mvp"
        assert ctx.role == "explorer"
        assert ctx.current_phase == 0
        assert ctx.phase_name == "Descubrimiento"

    def test_context_with_concepts(self, tmp_path):
        concepts = [
            ConceptStatus(name="HTTP", learned=True),
            ConceptStatus(name="REST", learned=False),
        ]
        _setup_project(tmp_path, concepts=concepts)
        ctx = build_context(tmp_path)
        assert len(ctx.domain_concepts) == 2
        assert ctx.next_concept == "REST"
        assert ctx.dkc == 50.0

    def test_context_no_pending_concepts(self, tmp_path):
        concepts = [ConceptStatus(name="HTTP", learned=True)]
        _setup_project(tmp_path, concepts=concepts)
        ctx = build_context(tmp_path)
        assert ctx.next_concept == ""

    def test_context_with_edes(self, tmp_path):
        _setup_project(tmp_path)
        ede = EDE(
            metadata=EDEMetadata(slug="auth", title="Auth Module", level=1),
            what_and_how="Login",
            why="Seguridad",
        )
        save_ede(tmp_path, ede)
        ctx = build_context(tmp_path)
        assert len(ctx.edes) == 1
        assert ctx.edes[0]["slug"] == "auth"

    def test_domain_map_summary_empty(self, tmp_path):
        _setup_project(tmp_path)
        ctx = build_context(tmp_path)
        assert "Sin conceptos" in ctx.domain_map_summary

    def test_domain_map_summary_with_concepts(self, tmp_path):
        concepts = [
            ConceptStatus(name="HTTP", learned=True),
            ConceptStatus(name="REST", learned=False),
        ]
        _setup_project(tmp_path, concepts=concepts)
        ctx = build_context(tmp_path)
        assert "✅ HTTP" in ctx.domain_map_summary
        assert "⬜ REST" in ctx.domain_map_summary
