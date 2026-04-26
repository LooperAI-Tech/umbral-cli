"""Interfaz abstracta para adapters de agentes (sección 8 del plan).

Cada adapter sabe cómo depositar un prompt contextualizado
donde el agente del usuario lo pueda leer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class BaseAdapter(ABC):
    """Interfaz abstracta que todos los adapters deben implementar.

    Un adapter deposita archivos de prompt en la ubicación que
    el agente específico espera leer.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre legible del adapter."""
        ...

    @property
    @abstractmethod
    def target_dir(self) -> str:
        """Directorio relativo donde depositar archivos (desde project root)."""
        ...

    @abstractmethod
    def deposit_prompt(
        self,
        project_root: Path,
        filename: str,
        content: str,
    ) -> Path:
        """Deposita un prompt renderizado en la ubicación del agente.

        Args:
            project_root: Raíz del proyecto.
            filename: Nombre del archivo a crear.
            content: Contenido del prompt renderizado.

        Returns:
            Path al archivo depositado.
        """
        ...

    @abstractmethod
    def list_prompts(self, project_root: Path) -> list[Path]:
        """Lista todos los prompts depositados.

        Args:
            project_root: Raíz del proyecto.

        Returns:
            Lista de paths a los prompts depositados.
        """
        ...
