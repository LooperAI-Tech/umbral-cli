"""Cálculo de las 13 métricas de salud (sección 2.9) — Sprint 6."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from umbral.core.config import ProjectConfig, Role
from umbral.core.ede import EDEStatus
from umbral.core.profile import CognitiveProfile
from umbral.core.telemetry import UmbralTelemetry
from umbral.storage.ede_store import list_edes
from umbral.validation.drift_detector import (
    DriftLevel,
    _ede_tokens,
    _iter_code_files,
    _text_tokens,
    assess_drift,
)


@dataclass(frozen=True)
class MetricsSnapshot:
    """Instantánea de las 13 métricas. ``None`` = dato no disponible (v0.1.0)."""

    cc: float
    cdr: float
    ari: float
    nav: float | None
    dkc: float
    lbb: float
    crf: float | None
    eds: float
    et: int | None
    etp: float | None
    jir: int
    jcr: float | None
    jfr: float | None


def _comprehension_coverage(project_root: Path, edes: list) -> float:
    """% de archivos de código con término compartido con alguna EDE aprobada."""
    approved = [e for e in edes if e.metadata.status == EDEStatus.APPROVED]
    if not approved:
        return 0.0
    et_sets = [_ede_tokens(e) for e in approved]
    files = _iter_code_files(project_root)
    if not files:
        return 0.0
    covered = 0
    for fpath in files:
        try:
            text = fpath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        ft = _text_tokens(text)
        if not ft:
            continue
        if any(et & ft for et in et_sets):
            covered += 1
    return 100.0 * (covered / max(len(files), 1))


def _eds_score(project_root: Path, edes: list) -> float:
    """0-1: drift promedio (mayor = peor alineación EDE-código)."""
    approved = [e for e in edes if e.metadata.status == EDEStatus.APPROVED]
    if not approved:
        return 0.0
    acc = 0.0
    for e in approved:
        r = assess_drift(e, project_root)
        if r.level == DriftLevel.SIGNIFICANT:
            acc += 1.0
        elif r.level == DriftLevel.MINOR:
            acc += 0.5
    return acc / len(approved)


def _anchor_ratio_index(
    profile: CognitiveProfile, config: ProjectConfig
) -> float:
    """Contextos con mastery de ancla (≥80) / contextos con registro; proxy ARI."""
    if not profile.context_mastery:
        return 1.0 if config.role == Role.ANCHOR else 0.0
    n = len([v for v in profile.context_mastery.values() if v >= 80.0])
    return n / max(len(profile.context_mastery), 1)


def _lbb(profile: CognitiveProfile) -> float:
    """Mismo que DKC a falta de bit «aprendido construyendo» (v0.1.0)."""
    if not profile.domain_concepts:
        return 0.0
    learned = sum(1 for c in profile.domain_concepts if c.learned)
    return 100.0 * learned / len(profile.domain_concepts)


def _jcr(tel: UmbralTelemetry) -> float | None:
    """% veredictos complete entre respuestas con veredicto del API."""
    tot = tel.judge_verdict_complete + tel.judge_verdict_not_complete
    if tot == 0:
        return None
    return 100.0 * tel.judge_verdict_complete / tot


def _jfr(tel: UmbralTelemetry) -> float | None:
    """% intentos online que cayeron en fallback (API falló)."""
    if tel.judge_online_attempts == 0:
        return None
    return 100.0 * tel.judge_api_fail_fallback / tel.judge_online_attempts


def compute_metrics(
    project_root: Path,
    config: ProjectConfig,
    profile: CognitiveProfile,
    telemetry: UmbralTelemetry,
) -> MetricsSnapshot:
    """Calcula la instantánea a partir de disco y telemetría local."""
    edes = list_edes(project_root)
    return MetricsSnapshot(
        cc=_comprehension_coverage(project_root, edes),
        cdr=profile.cdr,
        ari=_anchor_ratio_index(profile, config),
        nav=telemetry.nav_navigator_to_anchor_weeks,
        dkc=profile.dkc,
        lbb=_lbb(profile),
        crf=telemetry.crf_guess_fail_per_week,
        eds=_eds_score(project_root, edes),
        et=telemetry.et_effective_features_30d,
        etp=telemetry.etp_explorer_to_mvp_weeks,
        jir=telemetry.judge_online_attempts,
        jcr=_jcr(telemetry),
        jfr=_jfr(telemetry),
    )
