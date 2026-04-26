"""Telemetría local para métricas del juez y series temporales (Sprint 6, sección 2.9)."""

from __future__ import annotations

from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field


class UmbralTelemetry(BaseModel):
    """Estado guardado en `.umbral/telemetry.yaml`.

    Se actualiza con `umbral next` (invocación del juez online) y, en el futuro,
    con otras señales (CRF, ET,…).
    """

    model_config = ConfigDict(extra="ignore")

    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    # Juez (Capa 2) — v2.0
    judge_online_attempts: int = 0
    judge_verdict_complete: int = 0
    judge_verdict_not_complete: int = 0
    judge_api_fail_fallback: int = 0
    # Series temporales — opcional, v0.1.0 mayormente N/D
    crf_guess_fail_per_week: float | None = None
    nav_navigator_to_anchor_weeks: float | None = None
    et_effective_features_30d: int | None = None
    etp_explorer_to_mvp_weeks: float | None = None
    # Timestamps mínimos para aproximaciones
    first_umbral_init_at: str | None = None
