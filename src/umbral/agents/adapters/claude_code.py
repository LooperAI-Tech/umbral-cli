"""Adapter para Claude Code — deposita prompts en .claude/commands/."""

from __future__ import annotations

from pathlib import Path

from umbral.agents.base_adapter import BaseAdapter


class ClaudeCodeAdapter(BaseAdapter):
    """Adapter que deposita prompts en .claude/commands/.

    Claude Code lee archivos .md de este directorio como comandos
    que el usuario puede invocar.
    """

    @property
    def name(self) -> str:
        return "Claude Code"

    @property
    def target_dir(self) -> str:
        return ".claude/commands"

    def deposit_prompt(
        self,
        project_root: Path,
        filename: str,
        content: str,
    ) -> Path:
        """Deposita un prompt en .claude/commands/{filename}."""
        target = project_root / self.target_dir
        target.mkdir(parents=True, exist_ok=True)

        # Asegurar extensión .md
        if not filename.endswith(".md"):
            filename = f"{filename}.md"

        path = target / filename
        path.write_text(content, encoding="utf-8")
        return path

    def list_prompts(self, project_root: Path) -> list[Path]:
        """Lista los prompts depositados en .claude/commands/."""
        target = project_root / self.target_dir
        if not target.exists():
            return []
        return sorted(target.glob("*.md"))
