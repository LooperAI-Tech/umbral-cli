"""Adapter para Cursor — deposita prompts en .cursor/rules/."""

from __future__ import annotations

from pathlib import Path

from umbral.agents.base_adapter import BaseAdapter


class CursorAdapter(BaseAdapter):
    """Adapter que deposita prompts en .cursor/rules/.

    Cursor lee archivos .mdc de este directorio como rules
    de contexto para el agente.
    """

    @property
    def name(self) -> str:
        return "Cursor"

    @property
    def target_dir(self) -> str:
        return ".cursor/rules"

    def deposit_prompt(
        self,
        project_root: Path,
        filename: str,
        content: str,
    ) -> Path:
        """Deposita un prompt en .cursor/rules/{filename}."""
        target = project_root / self.target_dir
        target.mkdir(parents=True, exist_ok=True)

        # Cursor usa .mdc
        if not filename.endswith(".mdc"):
            # Reemplazar extensión si tiene una
            base = filename.rsplit(".", 1)[0] if "." in filename else filename
            filename = f"{base}.mdc"

        path = target / filename
        path.write_text(content, encoding="utf-8")
        return path

    def list_prompts(self, project_root: Path) -> list[Path]:
        """Lista los prompts depositados en .cursor/rules/."""
        target = project_root / self.target_dir
        if not target.exists():
            return []
        return sorted(target.glob("*.mdc"))
