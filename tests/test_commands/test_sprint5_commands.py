"""Tests CLI — Sprint 5 (build, profile show, consolidate)."""

from umbral.core.config import ProjectConfig, Role
from umbral.core.ede import EDE, EDEMetadata, EDEStatus
from umbral.core.profile import CognitiveProfile, ConceptStatus
from umbral.storage.config_store import save_config
from umbral.storage.ede_store import save_ede
from umbral.storage.paths import ensure_umbral_structure
from umbral.storage.profile_store import save_profile
from typer.testing import CliRunner

from umbral.cli import app

runner = CliRunner()


def _project(tmp_path):
    ensure_umbral_structure(tmp_path)
    cfg = ProjectConfig(project_name="p", role=Role.NAVIGATOR, current_phase=3)
    save_config(tmp_path, cfg)
    p = CognitiveProfile(
        context_mastery={"api": 90.0},
        domain_concepts=[ConceptStatus(name="http", learned=True)],
    )
    save_profile(tmp_path, p)
    return cfg


def test_build_deposits_prompt(tmp_path, monkeypatch):
    _project(tmp_path)
    ede = EDE(
        metadata=EDEMetadata(
            slug="api", title="API", level=2, status=EDEStatus.APPROVED,
        ),
        what_and_how="A" * 20,
        why="B" * 20,
        what_not_to_do="C" * 20,
        what_next="D" * 20,
    )
    save_ede(tmp_path, ede)
    monkeypatch.chdir(tmp_path)
    r = runner.invoke(app, ["build", "-c", "api"])
    assert r.exit_code == 0, r.output
    assert (tmp_path / ".claude" / "commands" / "build-api.md").exists()


def test_profile_show_runs(tmp_path, monkeypatch):
    _project(tmp_path)
    monkeypatch.chdir(tmp_path)
    r = runner.invoke(app, ["profile", "show"])
    assert r.exit_code == 0
    assert "DKC" in r.output


def test_consolidate_runs(tmp_path, monkeypatch):
    _project(tmp_path)
    ede = EDE(
        metadata=EDEMetadata(
            slug="api", title="A", level=1, status=EDEStatus.APPROVED,
        ),
        what_and_how="A" * 20,
        why="B" * 20,
    )
    save_ede(tmp_path, ede)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "x.py").write_text("hello world" * 5, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    r = runner.invoke(app, ["consolidate", "--new-area"])
    assert r.exit_code == 0, r.output
    out = r.output.replace("\n", " ").lower()
    assert "discover" in out
