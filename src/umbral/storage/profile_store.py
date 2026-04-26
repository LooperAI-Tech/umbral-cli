"""Persistencia del Perfil Cognitivo en .umbral/profile.yaml."""

from __future__ import annotations

from pathlib import Path

import yaml

from umbral.core.profile import CognitiveProfile
from umbral.storage.paths import get_profile_path


def save_profile(project_root: Path, profile: CognitiveProfile) -> Path:
    """Guarda el Perfil Cognitivo en disco.

    Args:
        project_root: Raíz del proyecto.
        profile: Perfil a guardar.

    Returns:
        Path al archivo guardado.
    """
    path = get_profile_path(project_root)
    data = profile.model_dump(mode="json")
    path.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True),
                    encoding="utf-8")
    return path


def load_profile(project_root: Path) -> CognitiveProfile:
    """Carga el Perfil Cognitivo desde disco.

    Args:
        project_root: Raíz del proyecto.

    Returns:
        CognitiveProfile cargado.

    Raises:
        FileNotFoundError: Si no existe profile.yaml.
    """
    path = get_profile_path(project_root)
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró perfil en {path}. "
            "¿Ejecutaste 'umbral init'?"
        )
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return CognitiveProfile(**data)
