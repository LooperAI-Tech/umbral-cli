"""Mensajes amigables para fallos al escribir en disco (p. ej. sin espacio)."""

from __future__ import annotations

import errno
from pathlib import Path

from umbral.ui.console import print_error


def is_no_space_on_device(exc: BaseException) -> bool:
    """``True`` si el error indica almacenamiento lleno (ENOSPC / 28)."""
    if not isinstance(exc, OSError):
        return False
    # errno 28: ENOSPC en la mayoría de plataformas (incl. muchos entornos Windows)
    if exc.errno == errno.ENOSPC:
        return True
    if exc.errno == 28:  # explícito por si el mapa de errno difiere
        return True
    return False


def report_no_space_error(project_root: Path, target_hint: str = "") -> None:
    """Imprime aviso: disco lleno; no re-lanza la excepción."""
    root = str(project_root.resolve())
    extra = f" Ruta: {target_hint}" if target_hint else ""
    print_error(
        "No hay espacio en disco (almacenamiento lleno en la unidad del "
        f"proyecto). Libera espacio en el disco donde está el proyecto "
        f"([bold]{root}[/bold]) y vuelve a intentarlo.{extra}"
    )


def handle_write_error(exc: BaseException, project_root: Path) -> bool:
    """Si es error de sin espacio, informa y retorna True (el caller debe salir)."""
    if is_no_space_on_device(exc):
        report_no_space_error(project_root)
        return True
    return False
