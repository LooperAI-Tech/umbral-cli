"""Tests para storage/config_store.py y profile_store.py."""

import pytest

from umbral.core.config import ProjectConfig, Scale, Role, JudgeConfig, JudgeMode
from umbral.core.profile import CognitiveProfile, ConceptStatus
from umbral.storage.config_store import save_config, load_config
from umbral.storage.profile_store import save_profile, load_profile
from umbral.storage.paths import ensure_umbral_structure


class TestConfigStore:
    """Tests para persistencia de configuración."""

    def test_save_and_load_config(self, tmp_path):
        """Verifica round-trip de guardar y cargar config."""
        ensure_umbral_structure(tmp_path)
        config = ProjectConfig(
            project_name="test-project",
            domain="web",
            scale=Scale.STARTUP,
            role=Role.NAVIGATOR,
            judge=JudgeConfig(mode=JudgeMode.ONLINE),
        )
        save_config(tmp_path, config)
        loaded = load_config(tmp_path)

        assert loaded.project_name == "test-project"
        assert loaded.domain == "web"
        assert loaded.scale == Scale.STARTUP
        assert loaded.role == Role.NAVIGATOR
        assert loaded.judge.mode == JudgeMode.ONLINE

    def test_load_config_not_found(self, tmp_path):
        """Verifica error cuando no existe el archivo."""
        with pytest.raises(FileNotFoundError, match="umbral init"):
            load_config(tmp_path)

    def test_save_config_creates_yaml(self, tmp_path):
        """Verifica que el archivo creado es YAML válido."""
        ensure_umbral_structure(tmp_path)
        config = ProjectConfig(project_name="test")
        path = save_config(tmp_path, config)
        content = path.read_text(encoding="utf-8")
        assert "project_name: test" in content


class TestProfileStore:
    """Tests para persistencia del Perfil Cognitivo."""

    def test_save_and_load_profile(self, tmp_path):
        """Verifica round-trip de guardar y cargar perfil."""
        ensure_umbral_structure(tmp_path)
        profile = CognitiveProfile(
            domain_concepts=[
                ConceptStatus(name="overfitting", learned=True),
                ConceptStatus(name="regularization", learned=False),
            ],
            system_contexts=["ml-pipeline"],
        )
        save_profile(tmp_path, profile)
        loaded = load_profile(tmp_path)

        assert len(loaded.domain_concepts) == 2
        assert loaded.domain_concepts[0].name == "overfitting"
        assert loaded.domain_concepts[0].learned is True
        assert loaded.system_contexts == ["ml-pipeline"]

    def test_load_profile_not_found(self, tmp_path):
        """Verifica error cuando no existe el archivo."""
        with pytest.raises(FileNotFoundError, match="umbral init"):
            load_profile(tmp_path)
