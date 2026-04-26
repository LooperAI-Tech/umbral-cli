"""Tests para `umbral metrics`."""

from umbral.core.config import ProjectConfig
from umbral.storage.config_store import save_config
from umbral.storage.paths import ensure_umbral_structure
from umbral.storage.profile_store import save_profile
from umbral.core.profile import CognitiveProfile
from typer.testing import CliRunner

from umbral.cli import app

runner = CliRunner()


def test_metrics_no_project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    r = runner.invoke(app, ["metrics"])
    assert r.exit_code == 1


def test_metrics_ok(tmp_path, monkeypatch):
    ensure_umbral_structure(tmp_path)
    save_config(tmp_path, ProjectConfig(project_name="m"))
    save_profile(tmp_path, CognitiveProfile())
    monkeypatch.chdir(tmp_path)
    r = runner.invoke(app, ["metrics"])
    assert r.exit_code == 0
    assert "CC" in r.output or "Comprehension" in r.output
