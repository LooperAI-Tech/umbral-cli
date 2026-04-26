"""Tests para commands/status.py."""

import yaml
from typer.testing import CliRunner

from umbral.cli import app
from umbral.core.config import ProjectConfig, Scale, Role
from umbral.storage.config_store import save_config
from umbral.storage.paths import ensure_umbral_structure
from umbral.storage.profile_store import save_profile
from umbral.core.profile import CognitiveProfile

runner = CliRunner()


def _setup_project(tmp_path):
    """Helper: crea un proyecto completo para tests."""
    ensure_umbral_structure(tmp_path)
    config = ProjectConfig(
        project_name="test-status",
        domain="web",
        scale=Scale.MVP,
        role=Role.EXPLORER,
    )
    save_config(tmp_path, config)
    save_profile(tmp_path, CognitiveProfile())
    return config


def test_status_no_project(tmp_path, monkeypatch):
    """Verifica error cuando no hay proyecto."""
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 1
    assert "umbral init" in result.output


def test_status_shows_info(tmp_path, monkeypatch):
    """Verifica que status muestra la información del proyecto."""
    _setup_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "test-status" in result.output
    assert "web" in result.output


def test_status_suggests_next(tmp_path, monkeypatch):
    """Verifica que status siempre sugiere 'umbral next'."""
    _setup_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["status"])
    assert "umbral next" in result.output
