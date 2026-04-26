"""Tests para judge/ — verdict, client_factory, prompt_builder, phase_judge."""

import json

import pytest

from umbral.core.config import ProjectConfig, Scale, Role, JudgeConfig, JudgeMode
from umbral.judge.verdict import Gap, JudgeVerdict, VerdictStatus
from umbral.judge.client_factory import create_judge_client
from umbral.judge.clients.anthropic_client import AnthropicJudgeClient
from umbral.judge.clients.gemini_client import GeminiJudgeClient
from umbral.judge.clients.openrouter_client import OpenRouterJudgeClient
from umbral.judge.prompt_builder import (
    build_judge_system_prompt,
    collect_artifacts,
    load_rubric,
)
from umbral.judge.phase_judge import _parse_verdict
from umbral.storage.config_store import save_config
from umbral.storage.paths import ensure_umbral_structure, get_phases_dir


class TestVerdict:
    """Tests para el schema JudgeVerdict."""

    def test_verdict_creation(self):
        v = JudgeVerdict(
            phase="0", status=VerdictStatus.COMPLETE, confidence=0.9,
            summary="OK", next_action="avanza",
        )
        assert v.is_complete
        assert not v.has_high_severity_gaps

    def test_verdict_with_gaps(self):
        v = JudgeVerdict(
            phase="0", status=VerdictStatus.INCOMPLETE,
            gaps=[Gap(category="edge_case", description="Falta X", severity="high")],
        )
        assert not v.is_complete
        assert v.has_high_severity_gaps

    def test_verdict_status_values(self):
        assert VerdictStatus.COMPLETE == "complete"
        assert VerdictStatus.INCOMPLETE == "incomplete"
        assert VerdictStatus.NEEDS_REVISION == "needs_revision"


class TestClientFactory:
    """Tests para la factory de clientes."""

    def test_create_anthropic(self):
        client = create_judge_client("anthropic")
        assert isinstance(client, AnthropicJudgeClient)

    def test_create_gemini(self):
        client = create_judge_client("gemini")
        assert isinstance(client, GeminiJudgeClient)

    def test_create_openrouter(self):
        client = create_judge_client("openrouter")
        assert isinstance(client, OpenRouterJudgeClient)

    def test_create_invalid(self):
        with pytest.raises(ValueError, match="no soportado"):
            create_judge_client("invalid")


class TestPromptBuilder:
    """Tests para el constructor de prompts del juez."""

    def test_load_rubric(self):
        rubric = load_rubric(0)
        assert "Discovery" in rubric or "discovery" in rubric.lower()

    def test_load_rubric_unknown(self):
        rubric = load_rubric(99)
        assert "Sin rúbrica" in rubric

    def test_build_system_prompt(self):
        config = ProjectConfig(project_name="test", domain="web")
        prompt = build_judge_system_prompt(0, config)
        assert "JSON" in prompt
        assert "status" in prompt

    def test_collect_discovery_artifacts(self, tmp_path):
        ensure_umbral_structure(tmp_path)
        config = ProjectConfig(project_name="test", current_phase=0)
        save_config(tmp_path, config)

        phases = get_phases_dir(tmp_path)
        (phases / "discovery-notes.md").write_text("Notas test", encoding="utf-8")

        artifacts = collect_artifacts(tmp_path, config)
        assert "Notas test" in artifacts


class TestParseVerdict:
    """Tests para el parseo de veredictos."""

    def test_parse_valid_json(self):
        response = json.dumps({
            "phase": "0", "status": "complete", "confidence": 0.9,
            "summary": "OK", "gaps": [], "next_action": "avanza",
            "artifacts_reviewed": ["notes.md"],
        })
        verdict = _parse_verdict(response, 0)
        assert verdict is not None
        assert verdict.is_complete

    def test_parse_json_with_text(self):
        response = 'Here is the verdict: {"phase": "0", "status": "incomplete", "confidence": 0.5, "summary": "Missing X", "gaps": [{"category": "scope", "description": "Falta scope", "severity": "high"}], "next_action": "add scope"} end'
        verdict = _parse_verdict(response, 0)
        assert verdict is not None
        assert not verdict.is_complete
        assert len(verdict.gaps) == 1

    def test_parse_invalid(self):
        verdict = _parse_verdict("not json at all", 0)
        assert verdict is None
