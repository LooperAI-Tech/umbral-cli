"""Resolución de rutas para la estructura .umbral/ del proyecto."""

from pathlib import Path


# Nombre del directorio raíz de Umbral dentro del proyecto del usuario
UMBRAL_DIR = ".umbral"


def find_project_root(start: Path | None = None) -> Path | None:
    """Busca la raíz del proyecto Umbral subiendo desde `start`.

    Busca un directorio que contenga `.umbral/umbral.yaml`.
    Si no se encuentra, retorna None.

    Args:
        start: Directorio desde donde empezar la búsqueda.
               Por defecto usa el directorio de trabajo actual.

    Returns:
        Path a la raíz del proyecto o None si no se encuentra.
    """
    current = (start or Path.cwd()).resolve()
    for parent in [current, *current.parents]:
        if (parent / UMBRAL_DIR / "umbral.yaml").exists():
            return parent
    return None


def get_umbral_dir(project_root: Path) -> Path:
    """Retorna la ruta al directorio .umbral/ del proyecto.

    Args:
        project_root: Raíz del proyecto.

    Returns:
        Path al directorio .umbral/
    """
    return project_root / UMBRAL_DIR


def get_config_path(project_root: Path) -> Path:
    """Ruta al archivo de configuración principal."""
    return get_umbral_dir(project_root) / "umbral.yaml"


def get_profile_path(project_root: Path) -> Path:
    """Ruta al archivo de Perfil Cognitivo."""
    return get_umbral_dir(project_root) / "profile.yaml"


def get_domain_map_path(project_root: Path) -> Path:
    """Ruta al Mapa de Dominio."""
    return get_umbral_dir(project_root) / "domain-map.yaml"


def get_edes_dir(project_root: Path) -> Path:
    """Ruta al directorio de EDEs."""
    return get_umbral_dir(project_root) / "edes"


def get_phases_dir(project_root: Path) -> Path:
    """Ruta al directorio de fases."""
    return get_umbral_dir(project_root) / "phases"


def get_telemetry_path(project_root: Path) -> Path:
    """Ruta a telemetría local (métricas del juez y señales futuras)."""
    return get_umbral_dir(project_root) / "telemetry.yaml"


def ensure_umbral_structure(project_root: Path) -> None:
    """Crea toda la estructura de directorios .umbral/ si no existe.

    Directorios creados:
        .umbral/
        .umbral/edes/
        .umbral/phases/

    Args:
        project_root: Raíz del proyecto donde crear la estructura.
    """
    umbral = get_umbral_dir(project_root)
    umbral.mkdir(exist_ok=True)
    get_edes_dir(project_root).mkdir(exist_ok=True)
    get_phases_dir(project_root).mkdir(exist_ok=True)
