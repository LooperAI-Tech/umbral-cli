"""Tests para commands/ede_cmd.py — subcomandos ede list, show, validate, approve."""

import pytest
from typer.testing import CliRunner

from umbral.cli import app
from umbral.core.config import ProjectConfig
from umbral.core.ede import EDE, EDEMetadata, EDEStatus
from umbral.core.profile import CognitiveProfile
from umbral.storage.config_store import save_config
from umbral.storage.ede_store import save_ede
from umbral.storage.paths import ensure_umbral_structure
from umbral.storage.profile_store import save_profile

runner = CliRunner()


def _setup_project(tmp_path):
    """Helper: crea un proyecto con config y perfil."""
    ensure_umbral_structure(tmp_path)
    config = ProjectConfig(project_name="test-ede-cmd", domain="web")
    save_config(tmp_path, config)
    save_profile(tmp_path, CognitiveProfile())


def _make_ede(slug: str = "test-feature", complete: bool = True) -> EDE:
    """Helper: crea una EDE para tests."""
    meta = EDEMetadata(slug=slug, title=f"Feature {slug}", level=1)
    return EDE(
        metadata=meta,
        what_and_how="Esto hace X." if complete else "",
        why="Porque Y." if complete else "",
    )


class TestEDEList:
    """Tests para umbral ede list."""

    def test_list_empty(self, tmp_path, monkeypatch):
        _setup_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["ede", "list"])
        assert result.exit_code == 0
        assert "No hay EDEs" in result.output

    def test_list_with_edes(self, tmp_path, monkeypatch):
        _setup_project(tmp_path)
        save_ede(tmp_path, _make_ede("feature-a"))
        save_ede(tmp_path, _make_ede("feature-b"))
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["ede", "list"])
        assert result.exit_code == 0
        assert "feature-a" in result.output
        assert "feature-b" in result.output


class TestEDEShow:
    """Tests para umbral ede show."""

    def test_show_existing(self, tmp_path, monkeypatch):
        _setup_project(tmp_path)
        save_ede(tmp_path, _make_ede("my-feature"))
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["ede", "show", "my-feature"])
        assert result.exit_code == 0
        assert "my-feature" in result.output
        assert "Esto hace X." in result.output

    def test_show_not_found(self, tmp_path, monkeypatch):
        _setup_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["ede", "show", "no-existe"])
        assert result.exit_code == 1


class TestEDEValidate:
    """Tests para umbral ede validate."""

    def test_validate_complete(self, tmp_path, monkeypatch):
        _setup_project(tmp_path)
        save_ede(tmp_path, _make_ede("valid-ede", complete=True))
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["ede", "validate", "valid-ede"])
        assert result.exit_code == 0
        assert "presentes" in result.output

    def test_validate_incomplete(self, tmp_path, monkeypatch):
        _setup_project(tmp_path)
        save_ede(tmp_path, _make_ede("incomplete-ede", complete=False))
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["ede", "validate", "incomplete-ede"])
        assert result.exit_code == 1
        assert "faltante" in result.output

    def test_validate_not_found(self, tmp_path, monkeypatch):
        _setup_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["ede", "validate", "no-existe"])
        assert result.exit_code == 1


class TestEDEApprove:
    """Tests para umbral ede approve."""

    def test_approve_valid_ede(self, tmp_path, monkeypatch):
        _setup_project(tmp_path)
        save_ede(tmp_path, _make_ede("approvable"))
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["ede", "approve", "approvable"])
        assert result.exit_code == 0
        assert "aprobada" in result.output

    def test_approve_incomplete_ede(self, tmp_path, monkeypatch):
        _setup_project(tmp_path)
        save_ede(tmp_path, _make_ede("incomplete", complete=False))
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["ede", "approve", "incomplete"])
        assert result.exit_code == 1
        assert "faltan" in result.output

    def test_approve_already_approved(self, tmp_path, monkeypatch):
        _setup_project(tmp_path)
        ede = _make_ede("already")
        ede.metadata.status = EDEStatus.APPROVED
        save_ede(tmp_path, ede)
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["ede", "approve", "already"])
        assert result.exit_code == 0
        assert "ya está aprobada" in result.output
