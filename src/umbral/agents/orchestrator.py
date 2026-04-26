"""Orquestador de prompts contextualizados (sección 8 del plan).

Renderiza templates Jinja2 con el contexto del proyecto
y los deposita vía el adapter correspondiente.
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from umbral.agents.base_adapter import BaseAdapter
from umbral.agents.adapters.claude_code import ClaudeCodeAdapter
from umbral.agents.adapters.cursor import CursorAdapter
from umbral.agents.context_builder import PromptContext, build_context
from umbral.core.config import AgentType
from umbral.storage.config_store import load_config


# Directorio de templates de prompts
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def get_adapter(agent_type: AgentType) -> BaseAdapter:
    """Factory: retorna el adapter según el tipo de agente.

    Args:
        agent_type: Tipo de agente configurado.

    Returns:
        Instancia del adapter correspondiente.
    """
    adapters: dict[AgentType, type[BaseAdapter]] = {
        AgentType.CLAUDE_CODE: ClaudeCodeAdapter,
        AgentType.CURSOR: CursorAdapter,
    }
    adapter_cls = adapters.get(agent_type)
    if adapter_cls is None:
        raise ValueError(f"Agente no soportado: {agent_type}")
    return adapter_cls()


def render_prompt(template_name: str, context: PromptContext) -> str:
    """Renderiza un template Jinja2 con el contexto del proyecto.

    Args:
        template_name: Nombre del template (ej: 'phases/discovery.md').
        context: Contexto del proyecto.

    Returns:
        Prompt renderizado como string.
    """
    env = Environment(
        loader=FileSystemLoader(str(PROMPTS_DIR)),
        autoescape=select_autoescape([]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(template_name)
    return template.render(**asdict(context))


def deposit_phase_prompt(
    project_root: Path,
    template_name: str,
    output_filename: str,
) -> Path:
    """Orquesta el flujo completo: contexto → render → depositar.

    Args:
        project_root: Raíz del proyecto.
        template_name: Template Jinja2 a usar.
        output_filename: Nombre del archivo a depositar.

    Returns:
        Path al archivo depositado.
    """
    config = load_config(project_root)
    adapter = get_adapter(config.agent)
    context = build_context(project_root)
    content = render_prompt(template_name, context)
    return adapter.deposit_prompt(project_root, output_filename, content)
