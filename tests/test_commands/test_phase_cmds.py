"""Tests para commands/discover.py y commands/articulate.py."""

from typer.testing import CliRunner

from umbral.cli import app
from umbral.core.config import ProjectConfig, Scale, Role
from umbral.core.profile import CognitiveProfile
from umbral.storage.config_store import save_config
from umbral.storage.paths import ensure_umbral_structure
from umbral.storage.profile_store import save_profile

runner = CliRunner()


def _setup_project(tmp_path):
    """Helper: crea un proyecto para tests."""
    ensure_umbral_structure(tmp_path)
    config = ProjectConfig(
        project_name="phase-test",
        domain="web",
        scale=Scale.MVP,
        role=Role.EXPLORER,
    )
    save_config(tmp_path, config)
    save_profile(tmp_path, CognitiveProfile())


class TestDiscoverCommand:
    """Tests para umbral discover."""

    def test_discover_deposits_prompt(self, tmp_path, monkeypatch):
        _setup_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["discover"])
        assert result.exit_code == 0
        assert "discover" in result.output.lower()
        # Verifica que se creó el archivo
        assert (tmp_path / ".claude" / "commands" / "discover.md").exists()

    def test_discover_prompt_content(self, tmp_path, monkeypatch):
        _setup_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        runner.invoke(app, ["discover"])
        content = (tmp_path / ".claude" / "commands" / "discover.md").read_text(
            encoding="utf-8"
        )
        assert "phase-test" in content
        assert "¿Qué problema real resuelve esto?" in content

    def test_discover_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["discover"])
        assert result.exit_code == 1

    def test_discover_suggests_next(self, tmp_path, monkeypatch):
        _setup_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["discover"])
        assert "umbral next" in result.output


class TestArticulateCommand:
    """Tests para umbral articulate."""

    def test_articulate_deposits_prompt(self, tmp_path, monkeypatch):
        _setup_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["articulate"])
        assert result.exit_code == 0
        assert (tmp_path / ".claude" / "commands" / "articulate.md").exists()

    def test_articulate_prompt_content(self, tmp_path, monkeypatch):
        _setup_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        runner.invoke(app, ["articulate"])
        content = (tmp_path / ".claude" / "commands" / "articulate.md").read_text(
            encoding="utf-8"
        )
        assert "phase-test" in content
        assert "Articulación" in content

    def test_articulate_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["articulate"])
        assert result.exit_code == 1
