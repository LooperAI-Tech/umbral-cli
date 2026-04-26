"""PhaseValidator — Capa 1: validación determinista (sección 9.1).

Lee artefactos del disco y verifica presencia, estructura y formato.
Sin red, sin costo, sin latencia.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from umbral.core.config import ProjectConfig
from umbral.core.ede import EDEStatus
from umbral.storage.ede_store import list_edes
from umbral.storage.paths import (
    get_domain_map_path,
    get_phases_dir,
    get_profile_path,
)


@dataclass
class ValidationResult:
    """Resultado de la validación determinista.

    Attributes:
        passed: Si la validación pasó.
        gaps: Lista de gaps estructurales encontrados.
        artifacts_found: Artefactos encontrados en disco.
    """

    passed: bool = True
    gaps: list[str] = field(default_factory=list)
    artifacts_found: list[str] = field(default_factory=list)

    def add_gap(self, gap: str) -> None:
        """Agrega un gap y marca como no pasado."""
        self.gaps.append(gap)
        self.passed = False


def validate_phase(project_root: Path, config: ProjectConfig) -> ValidationResult:
    """Valida la fase actual del proyecto.

    Ejecuta los chequeos deterministas según la fase activa.
    Si falla, no se invoca la Capa 2 (juez LLM).

    Args:
        project_root: Raíz del proyecto.
        config: Configuración del proyecto.

    Returns:
        ValidationResult con el resultado.
    """
    validators = {
        0: _validate_discovery,
        1: _validate_articulation,
        2: _validate_design,
        3: _validate_construction,
        4: _validate_verification,
        5: _validate_consolidation,
    }
    validator = validators.get(config.current_phase)
    if validator is None:
        result = ValidationResult()
        result.add_gap(f"Fase desconocida: {config.current_phase}")
        return result
    return validator(project_root, config)


def _validate_discovery(root: Path, config: ProjectConfig) -> ValidationResult:
    """Fase 0: discovery-notes.md + domain-map.yaml."""
    result = ValidationResult()
    phases_dir = get_phases_dir(root)

    # discovery-notes.md
    notes = phases_dir / "discovery-notes.md"
    if notes.exists():
        result.artifacts_found.append("discovery-notes.md")
        content = notes.read_text(encoding="utf-8").strip()
        if len(content) < 50:
            result.add_gap(
                "discovery-notes.md existe pero tiene muy poco contenido "
                "(mínimo 50 caracteres)."
            )
    else:
        result.add_gap(
            "Falta .umbral/phases/discovery-notes.md — "
            "Ejecuta 'umbral discover' y completa el diálogo."
        )

    # domain-map.yaml
    domain_map = get_domain_map_path(root)
    if domain_map.exists():
        result.artifacts_found.append("domain-map.yaml")
    else:
        result.add_gap(
            "Falta .umbral/domain-map.yaml — "
            "El Mapa de Dominio debe generarse durante el descubrimiento."
        )

    return result


def _validate_articulation(root: Path, config: ProjectConfig) -> ValidationResult:
    """Fase 1: spec-*.md con secciones requeridas."""
    result = ValidationResult()
    phases_dir = get_phases_dir(root)

    specs = list(phases_dir.glob("spec-*.md"))
    if not specs:
        result.add_gap(
            "Falta spec en .umbral/phases/spec-*.md — "
            "Ejecuta 'umbral articulate' y co-crea la spec."
        )
        return result

    result.artifacts_found.extend([s.name for s in specs])

    # Verificar secciones requeridas en la spec
    for spec in specs:
        content = spec.read_text(encoding="utf-8").lower()
        required_sections = ["caso", "falla", "alcance", "dato"]
        for section in required_sections:
            if section not in content:
                result.add_gap(
                    f"{spec.name}: falta sección sobre '{section}'. "
                    "La spec debe cubrir: casos borde, modos de falla, "
                    "alcance, y datos de entrada."
                )

    return result


def _validate_design(root: Path, config: ProjectConfig) -> ValidationResult:
    """Fase 2: al menos una EDE con status approved."""
    result = ValidationResult()

    edes = list_edes(root)
    if not edes:
        result.add_gap(
            "No hay EDEs. Ejecuta 'umbral design --level 1' para crear una."
        )
        return result

    result.artifacts_found.extend([f"{e.metadata.slug}.md" for e in edes])

    approved = [e for e in edes if e.metadata.status == EDEStatus.APPROVED]
    if not approved:
        result.add_gap(
            "Ninguna EDE tiene status 'approved'. "
            "Valida con 'umbral ede validate' y aprueba con 'umbral ede approve'."
        )

    # Verificar componentes
    for ede in approved:
        missing = ede.validate_components()
        if missing:
            from umbral.core.ede import COMPONENT_NAMES
            names = [COMPONENT_NAMES[m] for m in missing]
            result.add_gap(
                f"EDE '{ede.metadata.slug}' aprobada pero con componentes "
                f"faltantes: {', '.join(names)}."
            )

    return result


def _validate_construction(root: Path, config: ProjectConfig) -> ValidationResult:
    """Fase 3: EDE aprobada + código coherente (liviano en v0.1.0)."""
    result = ValidationResult()

    edes = list_edes(root)
    approved = [e for e in edes if e.metadata.status == EDEStatus.APPROVED]
    if not approved:
        result.add_gap("No hay EDE aprobada para la fase de construcción.")
        return result

    result.artifacts_found.extend([f"{e.metadata.slug}.md" for e in approved])
    return result


def _validate_verification(root: Path, config: ProjectConfig) -> ValidationResult:
    """Fase 4: checkpoint-*.yaml presente y con contenido mínimo (sección 2.5.3)."""
    result = ValidationResult()
    phases_dir = get_phases_dir(root)

    checkpoints = list(phases_dir.glob("checkpoint-*.yaml"))
    if not checkpoints:
        result.add_gap(
            "Falta checkpoint en .umbral/phases/checkpoint-*.yaml — "
            "Ejecuta 'umbral verify' para completar el Comprehension Gate."
        )
        return result

    result.artifacts_found.extend([c.name for c in checkpoints])

    for cp in checkpoints:
        _validate_checkpoint_file(cp, result)

    return result


def _is_substantial_answer(text: str) -> bool:
    """Heurística: no monosílabos ni respuestas triviales (Apéndice C.5)."""
    t = text.strip()
    if len(t) < 12:
        return False
    words = t.split()
    if len(words) < 3:
        return False
    return True


def _validate_checkpoint_file(path: Path, result: ValidationResult) -> None:
    """Valida estructura y calidad mínima de un checkpoint."""
    try:
        raw = path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
    except (OSError, yaml.YAMLError):
        result.add_gap(f"{path.name}: YAML inválido o ilegible.")
        return

    if not isinstance(data, dict):
        result.add_gap(f"{path.name}: se esperaba un mapping YAML.")
        return

    answers = data.get("answers")
    if not isinstance(answers, list) or not answers:
        result.add_gap(
            f"{path.name}: falta 'answers' con al menos una respuesta."
        )
        return

    assessment = (data.get("self_assessment") or "").strip()
    if not assessment:
        result.add_gap(
            f"{path.name}: falta autoevaluación ('self_assessment')."
        )

    substantial = sum(1 for a in answers if isinstance(a, str) and _is_substantial_answer(a))
    if substantial < max(1, (len(answers) + 1) // 2):
        result.add_gap(
            f"{path.name}: la mayoría de respuestas son demasiado breves o genéricas "
            "(se espera contenido real, no monosílabos)."
        )


def _validate_consolidation(
    root: Path, config: ProjectConfig
) -> ValidationResult:
    """Fase 5: EDE actualizada + perfil consolidado."""
    result = ValidationResult()

    # Perfil debe existir
    profile_path = get_profile_path(root)
    if profile_path.exists():
        result.artifacts_found.append("profile.yaml")
    else:
        result.add_gap("Falta profile.yaml para consolidación.")

    # EDEs deben existir
    edes = list_edes(root)
    if not edes:
        result.add_gap("No hay EDEs para consolidar.")
    else:
        result.artifacts_found.extend([f"{e.metadata.slug}.md" for e in edes])

    return result
