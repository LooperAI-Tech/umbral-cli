"""Setup de archivos de adapter según el agente elegido.

Claude Code: deposita en .claude/commands/
Cursor: deposita en .cursor/rules/
"""

from __future__ import annotations

from pathlib import Path

from umbral.core.config import AgentType


CLAUDE_CODE_INSTRUCTIONS = """\
# Umbral Framework — Instrucciones para Claude Code

Este proyecto usa el framework Umbral para desarrollo con comprensión sostenible.

## Reglas estrictas:
1. **NUNCA generes código sin una EDE aprobada.** Primero diseña, luego construye.
2. Usa el **método socrático**: haz preguntas en vez de dar respuestas directas.
3. Los commits deben ser **< 200 líneas**. Si el cambio es mayor, descompón.
4. Al terminar cada fase, indica al usuario: `umbral next`
5. Respeta el rol del usuario (Explorer/Navigator/Anchor) y adapta tu comunicación.

## Fase activa:
Consulta el estado actual con `umbral status`.
"""

CURSOR_RULES = """\
# Umbral Framework — Rules para Cursor

Este proyecto usa el framework Umbral para desarrollo con comprensión sostenible.

## Rules:
1. NUNCA generes código sin una EDE aprobada. Primero diseña, luego construye.
2. Usa el método socrático: haz preguntas en vez de dar respuestas directas.
3. Los commits deben ser < 200 líneas. Si el cambio es mayor, descompón.
4. Al terminar cada fase, indica al usuario: `umbral next`
5. Respeta el rol del usuario (Explorer/Navigator/Anchor) y adapta tu comunicación.

## Fase activa:
Consulta el estado actual con `umbral status`.
"""


def setup_adapter(project_root: Path, agent: AgentType) -> Path:
    """Crea los archivos del adapter según el agente.

    Args:
        project_root: Raíz del proyecto.
        agent: Tipo de agente (claude-code o cursor).

    Returns:
        Path al archivo creado.
    """
    if agent == AgentType.CLAUDE_CODE:
        return _setup_claude_code(project_root)
    elif agent == AgentType.CURSOR:
        return _setup_cursor(project_root)
    else:
        raise ValueError(f"Agente no soportado: {agent}")


def _setup_claude_code(project_root: Path) -> Path:
    """Crea .claude/commands/umbral.md con instrucciones."""
    commands_dir = project_root / ".claude" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)
    path = commands_dir / "umbral.md"
    path.write_text(CLAUDE_CODE_INSTRUCTIONS, encoding="utf-8")
    return path


def _setup_cursor(project_root: Path) -> Path:
    """Crea .cursor/rules/umbral.mdc con rules."""
    rules_dir = project_root / ".cursor" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    path = rules_dir / "umbral.mdc"
    path.write_text(CURSOR_RULES, encoding="utf-8")
    return path
