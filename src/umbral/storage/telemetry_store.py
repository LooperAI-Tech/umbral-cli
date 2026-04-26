"""Persistencia de telemetría en `.umbral/telemetry.yaml`."""

from __future__ import annotations

from pathlib import Path

import yaml

from umbral.core.telemetry import UmbralTelemetry
from umbral.storage.paths import get_telemetry_path


def load_telemetry(project_root: Path) -> UmbralTelemetry:
    """Carga telemetría o valores por defecto si no existe el archivo."""
    path = get_telemetry_path(project_root)
    if not path.exists():
        return UmbralTelemetry()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        return UmbralTelemetry()
    return UmbralTelemetry.model_validate(data)


def save_telemetry(project_root: Path, tel: UmbralTelemetry) -> Path:
    from datetime import datetime, timezone

    tel.updated_at = datetime.now(timezone.utc).isoformat()
    path = get_telemetry_path(project_root)
    path.write_text(
        yaml.dump(
            tel.model_dump(mode="json", exclude_none=True),
            default_flow_style=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    return path
