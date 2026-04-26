"""Tests para agents/adapter_setup.py."""

from umbral.agents.adapter_setup import setup_adapter
from umbral.core.config import AgentType


def test_setup_claude_code(tmp_path):
    """Verifica que se crea el archivo de adapter para Claude Code."""
    path = setup_adapter(tmp_path, AgentType.CLAUDE_CODE)
    assert path.exists()
    assert path.name == "umbral.md"
    assert ".claude" in str(path)
    content = path.read_text(encoding="utf-8")
    assert "Umbral Framework" in content
    assert "umbral next" in content
    assert "EDE" in content


def test_setup_cursor(tmp_path):
    """Verifica que se crea el archivo de adapter para Cursor."""
    path = setup_adapter(tmp_path, AgentType.CURSOR)
    assert path.exists()
    assert path.name == "umbral.mdc"
    assert ".cursor" in str(path)
    content = path.read_text(encoding="utf-8")
    assert "Umbral Framework" in content
    assert "umbral next" in content


def test_setup_adapter_creates_directories(tmp_path):
    """Verifica que se crean los directorios intermedios."""
    setup_adapter(tmp_path, AgentType.CLAUDE_CODE)
    assert (tmp_path / ".claude" / "commands").is_dir()


def test_setup_adapter_idempotent(tmp_path):
    """Verifica que se puede llamar múltiples veces."""
    setup_adapter(tmp_path, AgentType.CLAUDE_CODE)
    setup_adapter(tmp_path, AgentType.CLAUDE_CODE)
    assert (tmp_path / ".claude" / "commands" / "umbral.md").exists()
