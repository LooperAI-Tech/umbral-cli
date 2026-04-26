"""Construcción de prompts para el juez LLM (sección 9.4 del plan).

Carga la rúbrica correspondiente a la fase y recopila los artefactos
relevantes para enviar al juez.
"""

from __future__ import annotations

from pathlib import Path

from umbral.core.config import ProjectConfig
from umbral.core.ede import EDEStatus
from umbral.storage.ede_store import list_edes
from umbral.storage.paths import (
    get_domain_map_path,
    get_phases_dir,
    get_profile_path,
)

# Directorio de rúbricas
RUBRICS_DIR = Path(__file__).parent / "rubrics"

# Mapeo de fase a rúbrica
PHASE_RUBRICS: dict[int, str] = {
    0: "discovery.md",
    1: "articulation.md",
    2: "design.md",
    3: "construction.md",
    4: "verification.md",
}


def load_rubric(phase: int) -> str:
    """Carga la rúbrica de una fase.

    Args:
        phase: Número de fase.

    Returns:
        Contenido de la rúbrica como string.
    """
    rubric_name = PHASE_RUBRICS.get(phase)
    if rubric_name is None:
        return "Sin rúbrica definida para esta fase."
    path = RUBRICS_DIR / rubric_name
    if not path.exists():
        return "Rúbrica no encontrada."
    return path.read_text(encoding="utf-8")


def collect_artifacts(project_root: Path, config: ProjectConfig) -> str:
    """Recopila los artefactos relevantes para la fase actual.

    Lee los archivos del disco y los concatena como texto
    para enviar al juez LLM.

    Args:
        project_root: Raíz del proyecto.
        config: Configuración del proyecto.

    Returns:
        Texto con todos los artefactos concatenados.
    """
    collectors = {
        0: _collect_discovery,
        1: _collect_articulation,
        2: _collect_design,
        3: _collect_construction,
        4: _collect_verification,
    }
    collector = collectors.get(config.current_phase, _collect_empty)
    return collector(project_root, config)


def build_judge_system_prompt(phase: int, config: ProjectConfig) -> str:
    """Construye el prompt de sistema para el juez.

    Incluye la rúbrica y las instrucciones de formato de respuesta.
    """
    rubric = load_rubric(phase)
    return f"""{rubric}

## Instrucciones de evaluación:
- Rol del usuario: {config.role.value}
- Escala del proyecto: {config.scale.value}
- Dominio: {config.domain}

## Formato de respuesta (JSON estricto):
Responde SOLO con un JSON válido, sin texto adicional:
{{
    "phase": "{phase}",
    "status": "complete" | "incomplete" | "needs_revision",
    "confidence": 0.0-1.0,
    "summary": "resumen del veredicto",
    "gaps": [
        {{"category": "tipo", "description": "descripción", "severity": "high|medium|low"}}
    ],
    "next_action": "acción sugerida",
    "artifacts_reviewed": ["lista de artefactos"]
}}"""


def _collect_discovery(root: Path, config: ProjectConfig) -> str:
    """Recopila artefactos de Fase 0."""
    parts = [f"# Artefactos de Fase 0 — Proyecto: {config.project_name}\n"]

    notes = get_phases_dir(root) / "discovery-notes.md"
    if notes.exists():
        parts.append(f"## discovery-notes.md\n{notes.read_text(encoding='utf-8')}\n")

    domain_map = get_domain_map_path(root)
    if domain_map.exists():
        parts.append(
            f"## domain-map.yaml\n{domain_map.read_text(encoding='utf-8')}\n"
        )

    return "\n".join(parts)


def _collect_articulation(root: Path, config: ProjectConfig) -> str:
    """Recopila artefactos de Fase 1."""
    parts = [f"# Artefactos de Fase 1 — Proyecto: {config.project_name}\n"]

    for spec in get_phases_dir(root).glob("spec-*.md"):
        parts.append(f"## {spec.name}\n{spec.read_text(encoding='utf-8')}\n")

    return "\n".join(parts)


def _collect_design(root: Path, config: ProjectConfig) -> str:
    """Recopila artefactos de Fase 2."""
    parts = [f"# Artefactos de Fase 2 — Proyecto: {config.project_name}\n"]

    for ede in list_edes(root):
        ede_file = root / ".umbral" / "edes" / f"{ede.metadata.slug}.md"
        if ede_file.exists():
            parts.append(
                f"## EDE: {ede.metadata.slug}\n"
                f"{ede_file.read_text(encoding='utf-8')}\n"
            )

    return "\n".join(parts)


def _collect_construction(root: Path, config: ProjectConfig) -> str:
    """Recopila artefactos de Fase 3 (liviano en v0.1.0)."""
    parts = [f"# Artefactos de Fase 3 — Proyecto: {config.project_name}\n"]

    approved = [
        e for e in list_edes(root) if e.metadata.status == EDEStatus.APPROVED
    ]
    for ede in approved:
        parts.append(
            f"## EDE aprobada: {ede.metadata.slug}\n"
            f"Título: {ede.metadata.title}\n"
            f"Nivel: {ede.metadata.level}\n"
        )

    return "\n".join(parts)


def _collect_verification(root: Path, config: ProjectConfig) -> str:
    """Recopila artefactos de Fase 4."""
    parts = [f"# Artefactos de Fase 4 — Proyecto: {config.project_name}\n"]

    for checkpoint in get_phases_dir(root).glob("checkpoint-*.yaml"):
        parts.append(
            f"## {checkpoint.name}\n"
            f"{checkpoint.read_text(encoding='utf-8')}\n"
        )

    return "\n".join(parts)


def _collect_empty(root: Path, config: ProjectConfig) -> str:
    """Recopilador vacío para fases sin artefactos definidos."""
    return f"# Sin artefactos definidos para fase {config.current_phase}"
