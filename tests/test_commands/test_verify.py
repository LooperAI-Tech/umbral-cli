"""Tests para commands/verify.py — Comprehension Gate (Sprint 4)."""

import types

import questionary
import yaml
from typer.testing import CliRunner

from umbral.cli import app
from umbral.core.config import ProjectConfig
from umbral.core.profile import CognitiveProfile
from umbral.storage.config_store import save_config
from umbral.storage.paths import ensure_umbral_structure, get_phases_dir
from umbral.storage.profile_store import save_profile

runner = CliRunner()


def test_verify_saves_rich_checkpoint(tmp_path, monkeypatch) -> None:
    """`umbral verify` persiste checkpoint con categorías y respuestas."""
    ensure_umbral_structure(tmp_path)
    config = ProjectConfig(
        project_name="verify-t", domain="ml", current_phase=4, role="explorer"
    )
    save_config(tmp_path, config)
    save_profile(tmp_path, CognitiveProfile())

    def mock_text(*_a, **_k):
        class _T:
            def ask(self) -> str:
                return (
                    "Explico con detalle en varias palabras el diseño, "
                    "el flujo y la razón de esta decisión en el proyecto."
                )

        return _T()

    def mock_select(*_a, **_k):
        class _S:
            def ask(self) -> str:
                return "alta"

        return _S()

    fake_q = types.SimpleNamespace(
        text=mock_text,
        select=mock_select,
        Choice=questionary.Choice,
    )
    monkeypatch.setattr("umbral.commands.verify.questionary", fake_q)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["verify", "--bounded-context", "bc-api"])
    assert result.exit_code == 0, result.output
    checkpoints = list(get_phases_dir(tmp_path).glob("checkpoint-*.yaml"))
    assert len(checkpoints) == 1
    data = yaml.safe_load(checkpoints[0].read_text(encoding="utf-8"))
    assert data.get("self_assessment")
    assert data.get("question_categories")
    assert data.get("concepts_evaluated") is not None
    assert len(data.get("answers", [])) == len(data.get("questions", []))


def test_verify_requires_project(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["verify"])
    assert result.exit_code == 1
