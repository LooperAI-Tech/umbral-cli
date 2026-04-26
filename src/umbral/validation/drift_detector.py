"""Detección heurística de drift EDE vs código (sección 2.6.1).

v0.1.0: sin análisis AST; solapamiento léxico EDE vs archivos de código.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from umbral.core.ede import EDE

# Excluir directorios ruidosos
_SKIP_DIRS = {
    ".git",
    ".umbral",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    "dist",
    "build",
}


class DriftLevel(str, Enum):
    """Nivel de divergencia detectado."""

    NONE = "none"  # Coherente o sin código para comparar
    MINOR = "minor"  # Bajo solapamiento intermedio
    SIGNIFICANT = "significant"  # Código presente sin huella de la EDE


@dataclass(frozen=True)
class DriftReport:
    """Resultado de la detección."""

    ede_slug: str
    level: DriftLevel
    overlap_ratio: float
    note: str


def _text_tokens(text: str) -> set[str]:
    """Palabras alfanuméricas ≥ 4 chars (misma raíz, casefold)."""
    return {
        t.lower()
        for t in re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]{3,}", text, re.UNICODE)
    }


def _ede_tokens(ede: EDE) -> set[str]:
    """Tokens de toda la EDE + slug/título."""
    parts = [
        ede.metadata.slug,
        ede.metadata.title,
        ede.what_and_how,
        ede.why,
        ede.what_not_to_do,
        ede.what_next,
    ]
    return _text_tokens("\n".join(p for p in parts if p))


def _iter_code_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix not in {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java"}:
            continue
        if any(part in _SKIP_DIRS for part in p.parts):
            continue
        out.append(p)
    return out[: 5000]  # tope de seguridad


def _code_tokens(root: Path) -> set[str]:
    toks: set[str] = set()
    for path in _iter_code_files(root):
        try:
            toks |= _text_tokens(
                path.read_text(encoding="utf-8", errors="replace")
            )
        except OSError:
            continue
    return toks


def assess_drift(ede: EDE, project_root: Path) -> DriftReport:
    """Compara vocabulario de la EDE con el del código bajo el proyecto.

    - Sin archivos de código: ``NONE`` (p. ej. solo notebooks / doc).
    - Ratio Jaccard bajo: ``SIGNIFICANT``; intermedio: ``MINOR``; alto: ``NONE``.
    """
    et = _ede_tokens(ede)
    if not et:
        return DriftReport(
            ede_slug=ede.metadata.slug,
            level=DriftLevel.NONE,
            overlap_ratio=0.0,
            note="EDE sin términos extraíbles; no se evalúa drift.",
        )

    ct = _code_tokens(project_root)
    if not ct:
        return DriftReport(
            ede_slug=ede.metadata.slug,
            level=DriftLevel.NONE,
            overlap_ratio=0.0,
            note="No hay archivos de código rastreables; sin comparación.",
        )

    inter = len(et & ct)
    union = len(et | ct) or 1
    ratio = inter / max(len(et), 1)
    jacc = inter / union

    if ratio >= 0.35 or jacc >= 0.12:
        lvl = DriftLevel.NONE
        note = "Coherencia léxica razonable entre EDE y código."
    elif ratio >= 0.12 or jacc >= 0.04:
        lvl = DriftLevel.MINOR
        note = "Posible drift menor: revisa que los términos de la EDE vivan en el código."
    else:
        lvl = DriftLevel.SIGNIFICANT
        note = "Poco solapamiento EDE-código: documenta el drift (ADR) si es intencional."

    return DriftReport(
        ede_slug=ede.metadata.slug, level=lvl, overlap_ratio=round(ratio, 3), note=note
    )
