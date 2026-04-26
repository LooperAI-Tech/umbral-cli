"""Tests para core/config.py."""

import pytest

from umbral.core.config import (
    AgentType,
    JudgeConfig,
    JudgeMode,
    ProjectConfig,
    Role,
    Scale,
)


def test_scale_values():
    """Verifica los valores del enum Scale."""
    assert Scale.LEARNING == "learning"
    assert Scale.MVP == "mvp"
    assert Scale.STARTUP == "startup"


def test_role_values():
    """Verifica los valores del enum Role."""
    assert Role.EXPLORER == "explorer"
    assert Role.NAVIGATOR == "navigator"
    assert Role.ANCHOR == "anchor"


def test_agent_type_values():
    """Verifica los valores del enum AgentType."""
    assert AgentType.CLAUDE_CODE == "claude-code"
    assert AgentType.CURSOR == "cursor"


def test_judge_mode_values():
    """Verifica los valores del enum JudgeMode."""
    assert JudgeMode.ONLINE == "online"
    assert JudgeMode.OFFLINE == "offline"


def test_judge_config_defaults():
    """Verifica los valores por defecto de JudgeConfig."""
    config = JudgeConfig()
    assert config.mode == JudgeMode.OFFLINE
    assert config.provider == "anthropic"
    assert config.model == "claude-haiku-4-5"
    assert config.max_tokens == 800
    assert config.temperature == 0.2
    assert config.fallback_to_offline is True


def test_project_config_creation():
    """Verifica la creación de ProjectConfig con datos completos."""
    config = ProjectConfig(
        project_name="predictor-churn",
        domain="data-science",
        scale=Scale.MVP,
        role=Role.EXPLORER,
        agent=AgentType.CLAUDE_CODE,
    )
    assert config.project_name == "predictor-churn"
    assert config.domain == "data-science"
    assert config.current_phase == 0


def test_project_config_defaults():
    """Verifica los valores por defecto de ProjectConfig."""
    config = ProjectConfig(project_name="test")
    assert config.scale == Scale.MVP
    assert config.role == Role.EXPLORER
    assert config.agent == AgentType.CLAUDE_CODE
    assert config.current_phase == 0
    assert config.judge.mode == JudgeMode.OFFLINE


def test_project_config_serialization():
    """Verifica que se puede serializar y deserializar."""
    config = ProjectConfig(
        project_name="test",
        domain="web",
        scale=Scale.STARTUP,
        role=Role.ANCHOR,
    )
    data = config.model_dump(mode="json")
    restored = ProjectConfig(**data)
    assert restored.project_name == config.project_name
    assert restored.scale == config.scale
    assert restored.role == config.role


def test_judge_config_validation_max_tokens():
    """Verifica que max_tokens tiene validación de rango."""
    with pytest.raises(Exception):
        JudgeConfig(max_tokens=50)  # < 100


def test_judge_config_validation_temperature():
    """Verifica que temperature tiene validación de rango."""
    with pytest.raises(Exception):
        JudgeConfig(temperature=2.0)  # > 1.0
