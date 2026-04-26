"""Tests para commands/next_cmd.py."""

from typer.testing import CliRunner

from umbral.cli import app
from umbral.core.config import ProjectConfig, Scale, Role
from umbral.core.ede import EDE, EDEMetadata, EDEStatus
from umbral.core.profile import CognitiveProfile
from umbral.storage.config_store import load_config, save_config
from umbral.storage.ede_store import save_ede
from umbral.storage.paths import ensure_umbral_structure, get_phases_dir
from umbral.storage.profile_store import save_profile

runner = CliRunner()


def _setup(tmp_path, phase=0):
    ensure_umbral_structure(tmp_path)
    config = ProjectConfig(
        project_name="next-test", domain="web", current_phase=phase
    )
    save_config(tmp_path, config)
    save_profile(tmp_path, CognitiveProfile())
    return config


class TestNextCommand:
    """Tests para umbral next."""

    def test_next_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["next"])
        assert result.exit_code == 1

    def test_next_phase0_fails_no_artifacts(self, tmp_path, monkeypatch):
        _setup(tmp_path, phase=0)
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["next"])
        assert result.exit_code == 1
        assert "gap" in result.output.lower() or "Falta" in result.output

    def test_next_phase0_passes_offline(self, tmp_path, monkeypatch):
        _setup(tmp_path, phase=0)
        phases = get_phases_dir(tmp_path)
        (phases / "discovery-notes.md").write_text("A" * 60, encoding="utf-8")
        (tmp_path / ".umbral" / "domain-map.yaml").write_text(
            "concepts: [a]", encoding="utf-8"
        )
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["next"])
        assert result.exit_code == 0
        # Should advance to phase 1
        config = load_config(tmp_path)
        assert config.current_phase == 1

    def test_next_phase2_passes_with_approved_ede(self, tmp_path, monkeypatch):
        _setup(tmp_path, phase=2)
        ede = EDE(
            metadata=EDEMetadata(
                slug="feat", title="Feat", level=1,
                status=EDEStatus.APPROVED,
            ),
            what_and_how="X", why="Y",
        )
        save_ede(tmp_path, ede)
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["next"])
        assert result.exit_code == 0
        config = load_config(tmp_path)
        assert config.current_phase == 3

    def test_next_advances_phase(self, tmp_path, monkeypatch):
        """Verifica que next avanza la fase correctamente."""
        config = _setup(tmp_path, phase=3)
        # Phase 3 needs approved EDE
        ede = EDE(
            metadata=EDEMetadata(
                slug="test", title="Test", level=1,
                status=EDEStatus.APPROVED,
            ),
            what_and_how="X", why="Y",
        )
        save_ede(tmp_path, ede)
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["next"])
        assert result.exit_code == 0
        config = load_config(tmp_path)
        assert config.current_phase == 4
