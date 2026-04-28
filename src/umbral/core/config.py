"""Modelo de configuración Pydantic para umbral.yaml."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class AgentType(str, Enum):
    """Tipos de agente soportados."""

    CLAUDE_CODE = "claude-code"
    CURSOR = "cursor"


class Scale(str, Enum):
    """Escala del proyecto (sección 2.1.2 del plan)."""

    LEARNING = "learning"
    MVP = "mvp"
    STARTUP = "startup"


class Role(str, Enum):
    """Roles del usuario (sección 2.1.4 del plan)."""

    EXPLORER = "explorer"
    NAVIGATOR = "navigator"
    ANCHOR = "anchor"


class LLMProvider(str, Enum):
    """Proveedores de LLM soportados."""

    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    OPENAI = "openai"
    OPENROUTER = "openrouter"


PROVIDER_ENV_KEYS: dict[str, str] = {
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}

PROVIDER_DEFAULT_MODELS: dict[str, str] = {
    "anthropic": "claude-haiku-4-5",
    "gemini": "gemini-2.0-flash",
    "openai": "gpt-4o-mini",
    "openrouter": "anthropic/claude-haiku-4-5",
}


class JudgeMode(str, Enum):
    """Modo del LLM juez."""

    ONLINE = "online"
    OFFLINE = "offline"


class JudgeConfig(BaseModel):
    """Configuración del LLM juez (sección 3.4 del plan)."""

    mode: JudgeMode = JudgeMode.OFFLINE
    provider: str = "anthropic"
    model: str = "claude-haiku-4-5"
    max_tokens: int = Field(default=800, ge=100, le=4096)
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    fallback_to_offline: bool = True


class ProjectConfig(BaseModel):
    """Configuración principal del proyecto Umbral.

    Persistida en .umbral/umbral.yaml.
    """

    project_name: str
    domain: str = ""
    scale: Scale = Scale.MVP
    role: Role = Role.EXPLORER
    agent: AgentType = AgentType.CLAUDE_CODE
    current_phase: int = Field(default=0, ge=0, le=5)
    judge: JudgeConfig = Field(default_factory=JudgeConfig)
