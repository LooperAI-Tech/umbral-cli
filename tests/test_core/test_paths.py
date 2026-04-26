"""Tests para storage/paths.py."""

from pathlib import Path

from umbral.storage.paths import (
    UMBRAL_DIR,
    ensure_umbral_structure,
    find_project_root,
    get_config_path,
    get_domain_map_path,
    get_edes_dir,
    get_phases_dir,
    get_profile_path,
    get_umbral_dir,
)


def test_umbral_dir_name():
    """Verifica que el nombre del directorio es .umbral."""
    assert UMBRAL_DIR == ".umbral"


def test_get_umbral_dir():
    """Verifica que retorna la ruta correcta."""
    root = Path("/fake/project")
    assert get_umbral_dir(root) == root / ".umbral"


def test_get_config_path():
    """Verifica la ruta de umbral.yaml."""
    root = Path("/fake/project")
    assert get_config_path(root) == root / ".umbral" / "umbral.yaml"


def test_get_profile_path():
    """Verifica la ruta de profile.yaml."""
    root = Path("/fake/project")
    assert get_profile_path(root) == root / ".umbral" / "profile.yaml"


def test_get_domain_map_path():
    """Verifica la ruta de domain-map.yaml."""
    root = Path("/fake/project")
    assert get_domain_map_path(root) == root / ".umbral" / "domain-map.yaml"


def test_get_edes_dir():
    """Verifica la ruta del directorio de EDEs."""
    root = Path("/fake/project")
    assert get_edes_dir(root) == root / ".umbral" / "edes"


def test_get_phases_dir():
    """Verifica la ruta del directorio de fases."""
    root = Path("/fake/project")
    assert get_phases_dir(root) == root / ".umbral" / "phases"


def test_ensure_umbral_structure(tmp_path):
    """Verifica que se crean todos los directorios."""
    ensure_umbral_structure(tmp_path)
    assert (tmp_path / ".umbral").is_dir()
    assert (tmp_path / ".umbral" / "edes").is_dir()
    assert (tmp_path / ".umbral" / "phases").is_dir()


def test_ensure_umbral_structure_idempotent(tmp_path):
    """Verifica que se puede llamar múltiples veces sin error."""
    ensure_umbral_structure(tmp_path)
    ensure_umbral_structure(tmp_path)
    assert (tmp_path / ".umbral").is_dir()


def test_find_project_root_found(tmp_path):
    """Verifica que encuentra la raíz del proyecto."""
    umbral_dir = tmp_path / ".umbral"
    umbral_dir.mkdir()
    (umbral_dir / "umbral.yaml").write_text("project_name: test")
    assert find_project_root(tmp_path) == tmp_path


def test_find_project_root_from_subdirectory(tmp_path):
    """Verifica que encuentra la raíz desde un subdirectorio."""
    umbral_dir = tmp_path / ".umbral"
    umbral_dir.mkdir()
    (umbral_dir / "umbral.yaml").write_text("project_name: test")
    sub = tmp_path / "src" / "deep"
    sub.mkdir(parents=True)
    assert find_project_root(sub) == tmp_path


def test_find_project_root_not_found(tmp_path):
    """Verifica que retorna None si no hay proyecto."""
    assert find_project_root(tmp_path) is None
