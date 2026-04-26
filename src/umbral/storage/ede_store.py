"""Persistencia de EDEs en disco (.umbral/edes/{slug}.md).

Formato: frontmatter YAML entre --- + body Markdown con H2 por componente.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import yaml

from umbral.core.ede import COMPONENT_NAMES, EDE, EDEMetadata
from umbral.storage.paths import get_edes_dir


def save_ede(project_root: Path, ede: EDE) -> Path:
    """Guarda una EDE en disco como Markdown con frontmatter YAML.

    Args:
        project_root: Raíz del proyecto.
        ede: EDE a guardar.

    Returns:
        Path al archivo creado.
    """
    edes_dir = get_edes_dir(project_root)
    edes_dir.mkdir(parents=True, exist_ok=True)

    # Actualizar timestamp
    ede.metadata.updated_at = datetime.now().isoformat(timespec="seconds")

    path = edes_dir / f"{ede.metadata.slug}.md"
    content = _serialize_ede(ede)
    path.write_text(content, encoding="utf-8")
    return path


def load_ede(project_root: Path, slug: str) -> EDE:
    """Carga una EDE desde disco.

    Args:
        project_root: Raíz del proyecto.
        slug: Identificador de la EDE.

    Returns:
        EDE cargada.

    Raises:
        FileNotFoundError: Si no existe la EDE.
    """
    path = get_edes_dir(project_root) / f"{slug}.md"
    if not path.exists():
        raise FileNotFoundError(f"EDE no encontrada: {slug}")
    return _deserialize_ede(path.read_text(encoding="utf-8"))


def list_edes(project_root: Path) -> list[EDE]:
    """Lista todas las EDEs del proyecto.

    Args:
        project_root: Raíz del proyecto.

    Returns:
        Lista de EDEs ordenadas por fecha de creación.
    """
    edes_dir = get_edes_dir(project_root)
    if not edes_dir.exists():
        return []

    edes = []
    for md_file in sorted(edes_dir.glob("*.md")):
        try:
            ede = _deserialize_ede(md_file.read_text(encoding="utf-8"))
            edes.append(ede)
        except Exception:
            continue  # Saltar archivos mal formados
    return edes


def delete_ede(project_root: Path, slug: str) -> bool:
    """Elimina una EDE del disco.

    Args:
        project_root: Raíz del proyecto.
        slug: Identificador de la EDE.

    Returns:
        True si se eliminó, False si no existía.
    """
    path = get_edes_dir(project_root) / f"{slug}.md"
    if path.exists():
        path.unlink()
        return True
    return False


def _serialize_ede(ede: EDE) -> str:
    """Convierte una EDE a formato Markdown con frontmatter YAML."""
    # Frontmatter
    meta = ede.metadata.model_dump(mode="json")
    frontmatter = yaml.dump(meta, default_flow_style=False, allow_unicode=True)

    # Body: H2 por componente
    sections = []
    for comp_key, comp_name in COMPONENT_NAMES.items():
        content = ede.get_component(comp_key)
        if content and content.strip():
            sections.append(f"## {comp_name}\n\n{content.strip()}")

    body = "\n\n".join(sections)

    return f"---\n{frontmatter}---\n\n{body}\n"


def _deserialize_ede(text: str) -> EDE:
    """Parsea un archivo Markdown con frontmatter YAML a un objeto EDE."""
    # Separar frontmatter del body
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Formato inválido: falta frontmatter YAML.")

    meta_raw = parts[1].strip()
    body = parts[2].strip()

    # Parsear metadatos
    meta_dict = yaml.safe_load(meta_raw)
    metadata = EDEMetadata(**meta_dict)

    # Parsear componentes del body
    components = _parse_components(body)

    return EDE(metadata=metadata, **components)


# Mapeo inverso: nombre legible → campo del modelo
_REVERSE_NAMES: dict[str, str] = {v: k for k, v in COMPONENT_NAMES.items()}


def _parse_components(body: str) -> dict[str, str]:
    """Parsea secciones H2 del body Markdown a componentes."""
    components: dict[str, str] = {}
    current_key: str | None = None
    current_lines: list[str] = []

    for line in body.split("\n"):
        if line.startswith("## "):
            # Guardar sección anterior
            if current_key:
                components[current_key] = "\n".join(current_lines).strip()

            # Iniciar nueva sección
            heading = line[3:].strip()
            current_key = _REVERSE_NAMES.get(heading)
            current_lines = []
        else:
            current_lines.append(line)

    # Guardar última sección
    if current_key:
        components[current_key] = "\n".join(current_lines).strip()

    return components
