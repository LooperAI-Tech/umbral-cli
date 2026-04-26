"""Tests para core/metrics.py."""

from pathlib import Path

from umbral.core.config import ProjectConfig, Role, Scale
from umbral.core.metrics import compute_metrics
from umbral.core.profile import CognitiveProfile, ConceptStatus
from umbral.core.telemetry import UmbralTelemetry


def test_compute_metrics_basic(tmp_path: Path) -> None:
    (tmp_path / ".umbral").mkdir()
    (tmp_path / ".umbral" / "umbral.yaml").write_text(
        "project_name: x\ndomain: web\nscale: mvp\nrole: explorer\n"
        "current_phase: 0\n"
        "judge:\n  mode: offline\n",
        encoding="utf-8",
    )
    prof = CognitiveProfile(
        domain_concepts=[
            ConceptStatus(name="a", learned=True),
            ConceptStatus(name="b", learned=False),
        ],
        total_prs=4,
        comprehension_debt=1,
        context_mastery={"api": 85.0},
    )
    tel = UmbralTelemetry(
        judge_online_attempts=2,
        judge_verdict_complete=1,
        judge_verdict_not_complete=1,
        judge_api_fail_fallback=0,
    )
    cfg = ProjectConfig(
        project_name="x", domain="web", scale=Scale.MVP, role=Role.EXPLORER
    )
    m = compute_metrics(tmp_path, cfg, prof, tel)
    assert m.dkc == 50.0
    assert m.cdr == 25.0
    assert m.jir == 2
    assert m.jcr == 50.0
    assert m.jfr == 0.0
