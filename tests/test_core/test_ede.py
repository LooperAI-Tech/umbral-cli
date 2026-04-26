"""Tests para core/ede.py."""

import pytest

from umbral.core.ede import (
    COMPONENT_NAMES,
    REQUIRED_COMPONENTS,
    EDE,
    EDELevel,
    EDEMetadata,
    EDEStatus,
)


class TestEDEMetadata:
    """Tests para metadatos de la EDE."""

    def test_metadata_creation(self):
        """Verifica creación básica de metadatos."""
        meta = EDEMetadata(slug="auth-login", title="Login de usuario", level=1)
        assert meta.slug == "auth-login"
        assert meta.title == "Login de usuario"
        assert meta.level == 1
        assert meta.status == EDEStatus.DRAFT

    def test_metadata_default_status(self):
        """Verifica que el status por defecto es draft."""
        meta = EDEMetadata(slug="test", title="Test", level=1)
        assert meta.status == EDEStatus.DRAFT

    def test_metadata_timestamps(self):
        """Verifica que se generan timestamps automáticos."""
        meta = EDEMetadata(slug="test", title="Test", level=1)
        assert meta.created_at is not None
        assert meta.updated_at is not None

    def test_level_validation(self):
        """Verifica que nivel fuera de rango falla."""
        with pytest.raises(Exception):
            EDEMetadata(slug="test", title="Test", level=0)
        with pytest.raises(Exception):
            EDEMetadata(slug="test", title="Test", level=4)


class TestEDEStatus:
    """Tests para el enum de status."""

    def test_status_values(self):
        assert EDEStatus.DRAFT == "draft"
        assert EDEStatus.APPROVED == "approved"


class TestEDELevel:
    """Tests para los niveles de EDE."""

    def test_level_values(self):
        assert EDELevel.LEVEL_1 == 1
        assert EDELevel.LEVEL_2 == 2
        assert EDELevel.LEVEL_3 == 3


class TestRequiredComponents:
    """Tests para componentes requeridos por nivel."""

    def test_level_1_requires_2_components(self):
        assert len(REQUIRED_COMPONENTS[1]) == 2
        assert "what_and_how" in REQUIRED_COMPONENTS[1]
        assert "why" in REQUIRED_COMPONENTS[1]

    def test_level_2_requires_4_components(self):
        assert len(REQUIRED_COMPONENTS[2]) == 4

    def test_level_3_requires_4_components(self):
        assert len(REQUIRED_COMPONENTS[3]) == 4


class TestEDE:
    """Tests para el modelo EDE completo."""

    def _make_ede(self, level: int = 1, **kwargs) -> EDE:
        meta = EDEMetadata(slug="test-ede", title="Test EDE", level=level)
        defaults = {
            "metadata": meta,
            "what_and_how": "Descripción de qué y cómo",
            "why": "Razón de la decisión",
        }
        defaults.update(kwargs)
        return EDE(**defaults)

    def test_ede_creation(self):
        ede = self._make_ede()
        assert ede.metadata.slug == "test-ede"
        assert ede.what_and_how == "Descripción de qué y cómo"

    def test_get_component(self):
        ede = self._make_ede()
        assert ede.get_component("what_and_how") == "Descripción de qué y cómo"
        assert ede.get_component("why") == "Razón de la decisión"

    def test_set_component(self):
        ede = self._make_ede()
        ede.set_component("why", "Nueva razón")
        assert ede.why == "Nueva razón"

    def test_required_components_level_1(self):
        ede = self._make_ede(level=1)
        assert ede.required_components == ["what_and_how", "why"]

    def test_required_components_level_2(self):
        ede = self._make_ede(level=2)
        assert len(ede.required_components) == 4

    def test_validate_level_1_complete(self):
        """EDE nivel 1 con ambos componentes: sin faltantes."""
        ede = self._make_ede(level=1)
        assert ede.validate_components() == []
        assert ede.is_valid is True

    def test_validate_level_1_missing_why(self):
        """EDE nivel 1 sin 'why': detecta faltante."""
        ede = self._make_ede(level=1, why="")
        missing = ede.validate_components()
        assert "why" in missing
        assert ede.is_valid is False

    def test_validate_level_2_incomplete(self):
        """EDE nivel 2 solo con 2 componentes: detecta faltantes."""
        ede = self._make_ede(level=2)
        missing = ede.validate_components()
        assert "what_not_to_do" in missing
        assert "what_next" in missing

    def test_validate_level_2_complete(self):
        """EDE nivel 2 con todos los componentes."""
        ede = self._make_ede(
            level=2,
            what_not_to_do="No hacer esto",
            what_next="Siguiente paso",
        )
        assert ede.validate_components() == []
        assert ede.is_valid is True

    def test_component_names_exist(self):
        """Verifica que todos los componentes tienen nombre legible."""
        for level_comps in REQUIRED_COMPONENTS.values():
            for comp in level_comps:
                assert comp in COMPONENT_NAMES
