"""Constructor de contexto para inyectar en prompts (sección 8 del plan).

Recopila toda la información del proyecto necesaria para renderizar
un prompt contextualizado: config, perfil, EDEs, fase activa.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from umbral.core.config import ProjectConfig
from umbral.core.ede import EDE
from umbral.core.phase import get_phase_command, get_phase_name
from umbral.core.profile import CognitiveProfile
from umbral.storage.config_store import load_config
from umbral.storage.ede_store import list_edes
from umbral.storage.profile_store import load_profile


@dataclass
class PromptContext:
    """Contexto completo para renderizar un prompt.

    Contiene toda la información del proyecto que los templates
    de Jinja2 necesitan para generar prompts contextualizados.
    """

    project_name: str = ""
    domain: str = ""
    scale: str = ""
    role: str = ""
    current_phase: int = 0
    phase_name: str = ""
    phase_command: str = ""
    agent: str = ""

    # Perfil Cognitivo
    dkc: float = 0.0
    domain_concepts: list[dict] = field(default_factory=list)
    next_concept: str = ""

    # EDEs
    edes: list[dict] = field(default_factory=list)
    related_edes: list[dict] = field(default_factory=list)

    # Mapa de dominio resumen
    domain_map_summary: str = ""


def build_context(project_root: Path) -> PromptContext:
    """Construye el contexto completo del proyecto.

    Lee config, perfil y EDEs del disco para crear un PromptContext
    que se inyecta en los templates de prompts.

    Args:
        project_root: Raíz del proyecto.

    Returns:
        PromptContext con toda la información del proyecto.
    """
    config = load_config(project_root)
    profile = load_profile(project_root)
    edes = list_edes(project_root)

    ctx = PromptContext(
        project_name=config.project_name,
        domain=config.domain,
        scale=config.scale.value,
        role=config.role.value,
        current_phase=config.current_phase,
        phase_name=get_phase_name(config.current_phase),
        phase_command=get_phase_command(config.current_phase),
        agent=config.agent.value,
        dkc=profile.dkc,
    )

    # Conceptos del dominio
    ctx.domain_concepts = [
        {"name": c.name, "learned": c.learned}
        for c in profile.domain_concepts
    ]

    # Siguiente concepto a enseñar
    pending = [c for c in profile.domain_concepts if not c.learned]
    ctx.next_concept = pending[0].name if pending else ""

    # EDEs como dicts para templates
    ctx.edes = [
        {
            "slug": e.metadata.slug,
            "title": e.metadata.title,
            "level": e.metadata.level,
            "status": e.metadata.status.value,
            "bounded_context": e.metadata.bounded_context,
        }
        for e in edes
    ]
    ctx.related_edes = ctx.edes  # Para v0.1.0 todas son "related"

    # Resumen del mapa de dominio
    ctx.domain_map_summary = _build_domain_summary(profile)

    return ctx


def _build_domain_summary(profile: CognitiveProfile) -> str:
    """Construye un resumen textual del mapa de dominio."""
    if not profile.domain_concepts:
        return "Sin conceptos definidos aún."

    lines = []
    for c in profile.domain_concepts:
        icon = "✅" if c.learned else "⬜"
        lines.append(f"  {icon} {c.name}")
    return "\n".join(lines)
