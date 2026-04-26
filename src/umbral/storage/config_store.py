"""Persistencia de la configuración del proyecto en .umbral/umbral.yaml."""

from __future__ import annotations

from pathlib import Path

import yaml

from umbral.core.config import ProjectConfig
from umbral.storage.paths import get_config_path


def save_config(project_root: Path, config: ProjectConfig) -> Path:
    """Guarda la configuración del proyecto en disco.

    Args:
        project_root: Raíz del proyecto.
        config: Configuración a guardar.

    Returns:
        Path al archivo guardado.
    """
    path = get_config_path(project_root)
    data = config.model_dump(mode="json")
    path.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True),
                    encoding="utf-8")
    return path


def load_config(project_root: Path) -> ProjectConfig:
    """Carga la configuración del proyecto desde disco.

    Args:
        project_root: Raíz del proyecto.

    Returns:
        ProjectConfig cargada.

    Raises:
        FileNotFoundError: Si no existe umbral.yaml.
    """
    path = get_config_path(project_root)
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró configuración en {path}. "
            "¿Ejecutaste 'umbral init'?"
        )
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return ProjectConfig(**data)
