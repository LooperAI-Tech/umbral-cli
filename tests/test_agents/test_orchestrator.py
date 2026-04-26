"""Tests para agents/orchestrator.py."""

from umbral.agents.orchestrator import (
    get_adapter,
    render_prompt,
    deposit_phase_prompt,
)
from umbral.agents.adapters.claude_code import ClaudeCodeAdapter
from umbral.agents.adapters.cursor import CursorAdapter
from umbral.agents.context_builder import PromptContext
from umbral.core.config import AgentType, ProjectConfig, Scale, Role
from umbral.core.profile import CognitiveProfile
from umbral.storage.config_store import save_config
from umbral.storage.paths import ensure_umbral_structure
from umbral.storage.profile_store import save_profile


class TestGetAdapter:
    """Tests para la factory de adapters."""

    def test_claude_code(self):
        adapter = get_adapter(AgentType.CLAUDE_CODE)
        assert isinstance(adapter, ClaudeCodeAdapter)

    def test_cursor(self):
        adapter = get_adapter(AgentType.CURSOR)
        assert isinstance(adapter, CursorAdapter)


class TestRenderPrompt:
    """Tests para renderización de templates Jinja2."""

    def test_render_discovery_explorer(self):
        ctx = PromptContext(
            project_name="test-proj",
            domain="web",
            scale="mvp",
            role="explorer",
        )
        result = render_prompt("phases/discovery.md", ctx)
        assert "test-proj" in result
        assert "web" in result
        assert "Explorer" in result
        assert "¿Qué problema real resuelve esto?" in result

    def test_render_discovery_navigator(self):
        ctx = PromptContext(
            project_name="test-proj",
            domain="web",
            scale="mvp",
            role="navigator",
        )
        result = render_prompt("phases/discovery.md", ctx)
        assert "Navigator" in result

    def test_render_discovery_anchor(self):
        ctx = PromptContext(
            project_name="test-proj",
            domain="web",
            scale="startup",
            role="anchor",
        )
        result = render_prompt("phases/discovery.md", ctx)
        assert "Anchor" in result

    def test_render_articulation(self):
        ctx = PromptContext(
            project_name="test-proj",
            domain="data-science",
            scale="learning",
            role="explorer",
        )
        result = render_prompt("phases/articulation.md", ctx)
        assert "Articulación" in result
        assert "¿Qué debería mostrar la app" in result

    def test_render_articulation_with_edes(self):
        ctx = PromptContext(
            project_name="test-proj",
            role="navigator",
            related_edes=[
                {"slug": "auth", "title": "Auth", "level": 1},
            ],
        )
        result = render_prompt("phases/articulation.md", ctx)
        assert "auth" in result

    def test_render_construction(self):
        ctx = PromptContext(
            project_name="test-proj",
            domain="web",
            role="explorer",
            dkc=20.0,
        )
        result = render_prompt("phases/construction.md", ctx)
        assert "DESBLOQUEO" in result

    def test_render_construction_guide_mode(self):
        ctx = PromptContext(
            project_name="test-proj",
            role="anchor",
            dkc=90.0,
        )
        result = render_prompt("phases/construction.md", ctx)
        assert "GUÍA" in result

    def test_render_contains_umbral_next(self):
        ctx = PromptContext(project_name="test", role="explorer")
        for template in [
            "phases/discovery.md",
            "phases/articulation.md",
            "phases/construction.md",
            "phases/verification.md",
        ]:
            result = render_prompt(template, ctx)
            assert "umbral next" in result


class TestDepositPhasePrompt:
    """Tests para el flujo completo de deposit."""

    def _setup_project(self, tmp_path, agent=AgentType.CLAUDE_CODE):
        ensure_umbral_structure(tmp_path)
        config = ProjectConfig(
            project_name="deposit-test",
            domain="web",
            scale=Scale.MVP,
            role=Role.EXPLORER,
            agent=agent,
        )
        save_config(tmp_path, config)
        save_profile(tmp_path, CognitiveProfile())

    def test_deposit_discovery_claude(self, tmp_path):
        self._setup_project(tmp_path, agent=AgentType.CLAUDE_CODE)
        path = deposit_phase_prompt(
            tmp_path, "phases/discovery.md", "discover"
        )
        assert path.exists()
        assert path.name == "discover.md"
        content = path.read_text(encoding="utf-8")
        assert "deposit-test" in content
        assert "Descubrimiento" in content

    def test_deposit_discovery_cursor(self, tmp_path):
        self._setup_project(tmp_path, agent=AgentType.CURSOR)
        path = deposit_phase_prompt(
            tmp_path, "phases/discovery.md", "discover"
        )
        assert path.exists()
        assert path.name == "discover.mdc"

    def test_deposit_articulation(self, tmp_path):
        self._setup_project(tmp_path)
        path = deposit_phase_prompt(
            tmp_path, "phases/articulation.md", "articulate"
        )
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "Articulación" in content
