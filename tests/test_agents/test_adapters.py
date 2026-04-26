"""Tests para agents/base_adapter.py y adapters concretos."""

from umbral.agents.base_adapter import BaseAdapter
from umbral.agents.adapters.claude_code import ClaudeCodeAdapter
from umbral.agents.adapters.cursor import CursorAdapter


class TestClaudeCodeAdapter:
    """Tests para el adapter de Claude Code."""

    def test_name(self):
        adapter = ClaudeCodeAdapter()
        assert adapter.name == "Claude Code"

    def test_target_dir(self):
        adapter = ClaudeCodeAdapter()
        assert adapter.target_dir == ".claude/commands"

    def test_deposit_prompt(self, tmp_path):
        adapter = ClaudeCodeAdapter()
        path = adapter.deposit_prompt(tmp_path, "test", "contenido")
        assert path.exists()
        assert path.name == "test.md"
        assert path.read_text(encoding="utf-8") == "contenido"

    def test_deposit_prompt_with_md_extension(self, tmp_path):
        adapter = ClaudeCodeAdapter()
        path = adapter.deposit_prompt(tmp_path, "test.md", "contenido")
        assert path.name == "test.md"

    def test_deposit_creates_directory(self, tmp_path):
        adapter = ClaudeCodeAdapter()
        adapter.deposit_prompt(tmp_path, "test", "contenido")
        assert (tmp_path / ".claude" / "commands").is_dir()

    def test_list_prompts_empty(self, tmp_path):
        adapter = ClaudeCodeAdapter()
        assert adapter.list_prompts(tmp_path) == []

    def test_list_prompts(self, tmp_path):
        adapter = ClaudeCodeAdapter()
        adapter.deposit_prompt(tmp_path, "alpha", "a")
        adapter.deposit_prompt(tmp_path, "beta", "b")
        prompts = adapter.list_prompts(tmp_path)
        assert len(prompts) == 2
        names = [p.stem for p in prompts]
        assert "alpha" in names
        assert "beta" in names

    def test_is_base_adapter(self):
        adapter = ClaudeCodeAdapter()
        assert isinstance(adapter, BaseAdapter)


class TestCursorAdapter:
    """Tests para el adapter de Cursor."""

    def test_name(self):
        adapter = CursorAdapter()
        assert adapter.name == "Cursor"

    def test_target_dir(self):
        adapter = CursorAdapter()
        assert adapter.target_dir == ".cursor/rules"

    def test_deposit_prompt(self, tmp_path):
        adapter = CursorAdapter()
        path = adapter.deposit_prompt(tmp_path, "test", "contenido")
        assert path.exists()
        assert path.name == "test.mdc"
        assert path.read_text(encoding="utf-8") == "contenido"

    def test_deposit_prompt_converts_extension(self, tmp_path):
        adapter = CursorAdapter()
        path = adapter.deposit_prompt(tmp_path, "test.md", "contenido")
        assert path.name == "test.mdc"

    def test_deposit_creates_directory(self, tmp_path):
        adapter = CursorAdapter()
        adapter.deposit_prompt(tmp_path, "test", "contenido")
        assert (tmp_path / ".cursor" / "rules").is_dir()

    def test_list_prompts(self, tmp_path):
        adapter = CursorAdapter()
        adapter.deposit_prompt(tmp_path, "rule1", "r1")
        prompts = adapter.list_prompts(tmp_path)
        assert len(prompts) == 1

    def test_is_base_adapter(self):
        adapter = CursorAdapter()
        assert isinstance(adapter, BaseAdapter)
