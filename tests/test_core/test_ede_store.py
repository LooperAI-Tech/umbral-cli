"""Tests para storage/ede_store.py."""

import pytest

from umbral.core.ede import EDE, EDEMetadata, EDEStatus
from umbral.storage.ede_store import (
    delete_ede,
    list_edes,
    load_ede,
    save_ede,
)
from umbral.storage.paths import ensure_umbral_structure


def _make_ede(slug: str = "test-ede", level: int = 1, **kwargs) -> EDE:
    """Helper: crea una EDE para tests."""
    meta = EDEMetadata(slug=slug, title=f"Test {slug}", level=level)
    defaults = {
        "metadata": meta,
        "what_and_how": "Esto hace X usando Y.",
        "why": "Elegí esto porque Z.",
    }
    defaults.update(kwargs)
    return EDE(**defaults)


class TestEDEStore:
    """Tests para CRUD de EDEs en disco."""

    def test_save_and_load(self, tmp_path):
        """Verifica round-trip de guardar y cargar EDE."""
        ensure_umbral_structure(tmp_path)
        ede = _make_ede()
        save_ede(tmp_path, ede)
        loaded = load_ede(tmp_path, "test-ede")

        assert loaded.metadata.slug == "test-ede"
        assert loaded.metadata.title == "Test test-ede"
        assert loaded.metadata.level == 1
        assert loaded.what_and_how == "Esto hace X usando Y."
        assert loaded.why == "Elegí esto porque Z."

    def test_save_creates_md_file(self, tmp_path):
        """Verifica que se crea un archivo .md."""
        ensure_umbral_structure(tmp_path)
        ede = _make_ede(slug="my-feature")
        path = save_ede(tmp_path, ede)
        assert path.suffix == ".md"
        assert path.name == "my-feature.md"

    def test_save_contains_frontmatter(self, tmp_path):
        """Verifica que el archivo tiene frontmatter YAML."""
        ensure_umbral_structure(tmp_path)
        ede = _make_ede()
        path = save_ede(tmp_path, ede)
        content = path.read_text(encoding="utf-8")
        assert content.startswith("---")
        assert "slug: test-ede" in content
        assert "level: 1" in content
        assert "status: draft" in content

    def test_save_contains_components(self, tmp_path):
        """Verifica que el body contiene las secciones H2."""
        ensure_umbral_structure(tmp_path)
        ede = _make_ede()
        path = save_ede(tmp_path, ede)
        content = path.read_text(encoding="utf-8")
        assert "## Qué y Cómo" in content
        assert "## Por Qué" in content
        assert "Esto hace X usando Y." in content

    def test_load_not_found(self, tmp_path):
        """Verifica error al cargar EDE inexistente."""
        ensure_umbral_structure(tmp_path)
        with pytest.raises(FileNotFoundError):
            load_ede(tmp_path, "no-existe")

    def test_list_edes_empty(self, tmp_path):
        """Verifica lista vacía cuando no hay EDEs."""
        ensure_umbral_structure(tmp_path)
        assert list_edes(tmp_path) == []

    def test_list_edes_multiple(self, tmp_path):
        """Verifica lista con múltiples EDEs."""
        ensure_umbral_structure(tmp_path)
        save_ede(tmp_path, _make_ede(slug="alpha"))
        save_ede(tmp_path, _make_ede(slug="beta"))
        save_ede(tmp_path, _make_ede(slug="gamma"))

        edes = list_edes(tmp_path)
        slugs = [e.metadata.slug for e in edes]
        assert len(edes) == 3
        assert "alpha" in slugs
        assert "beta" in slugs
        assert "gamma" in slugs

    def test_delete_ede(self, tmp_path):
        """Verifica eliminación de EDE."""
        ensure_umbral_structure(tmp_path)
        save_ede(tmp_path, _make_ede(slug="to-delete"))
        assert delete_ede(tmp_path, "to-delete") is True
        assert list_edes(tmp_path) == []

    def test_delete_ede_not_found(self, tmp_path):
        """Verifica que eliminar EDE inexistente retorna False."""
        ensure_umbral_structure(tmp_path)
        assert delete_ede(tmp_path, "no-existe") is False

    def test_save_level_2_with_all_components(self, tmp_path):
        """Verifica round-trip de EDE nivel 2 completa."""
        ensure_umbral_structure(tmp_path)
        ede = _make_ede(
            slug="full-ede",
            level=2,
            what_not_to_do="No usar patrones X.",
            what_next="Implementar Y después.",
        )
        save_ede(tmp_path, ede)
        loaded = load_ede(tmp_path, "full-ede")

        assert loaded.metadata.level == 2
        assert loaded.what_not_to_do == "No usar patrones X."
        assert loaded.what_next == "Implementar Y después."

    def test_save_preserves_status(self, tmp_path):
        """Verifica que el status se preserva al guardar."""
        ensure_umbral_structure(tmp_path)
        ede = _make_ede()
        ede.metadata.status = EDEStatus.APPROVED
        save_ede(tmp_path, ede)
        loaded = load_ede(tmp_path, "test-ede")
        assert loaded.metadata.status == EDEStatus.APPROVED

    def test_overwrite_existing(self, tmp_path):
        """Verifica que guardar sobrescribe EDE existente."""
        ensure_umbral_structure(tmp_path)
        ede1 = _make_ede(why="Razón original")
        save_ede(tmp_path, ede1)

        ede2 = _make_ede(why="Razón actualizada")
        save_ede(tmp_path, ede2)

        loaded = load_ede(tmp_path, "test-ede")
        assert loaded.why == "Razón actualizada"
