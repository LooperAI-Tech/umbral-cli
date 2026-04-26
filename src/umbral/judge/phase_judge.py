"""PhaseJudge — Capa 2: juez LLM semántico (sección 9.4 del plan).

Recolecta artefactos, carga rúbrica, construye prompt, llama al cliente,
y parsea el veredicto JSON. Si la API falla, devuelve None.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from umbral.core.config import ProjectConfig
from umbral.judge.base_client import BaseJudgeClient
from umbral.judge.client_factory import create_judge_client
from umbral.judge.prompt_builder import build_judge_system_prompt, collect_artifacts
from umbral.judge.verdict import Gap, JudgeVerdict, VerdictStatus

logger = logging.getLogger(__name__)


def judge_phase(
    project_root: Path,
    config: ProjectConfig,
) -> JudgeVerdict | None:
    """Ejecuta la evaluación LLM de la fase actual.

    Args:
        project_root: Raíz del proyecto.
        config: Configuración del proyecto.

    Returns:
        JudgeVerdict si la evaluación fue exitosa, None si falló.
    """
    # Crear cliente
    try:
        client = create_judge_client(
            provider=config.judge.provider,
            model=config.judge.model,
        )
    except ValueError as e:
        logger.error(f"Error creando cliente del juez: {e}")
        return None

    # Construir prompts
    system_prompt = build_judge_system_prompt(config.current_phase, config)
    user_prompt = collect_artifacts(project_root, config)

    # Llamar al LLM
    response = client.complete(
        system=system_prompt,
        user=user_prompt,
        max_tokens=config.judge.max_tokens,
        temperature=config.judge.temperature,
    )

    if response is None:
        logger.warning("El juez LLM no respondió. Modo offline activado.")
        return None

    # Parsear veredicto JSON
    return _parse_verdict(response, config.current_phase)


def _parse_verdict(response: str, phase: int) -> JudgeVerdict | None:
    """Parsea la respuesta del LLM a un JudgeVerdict.

    Intenta extraer JSON de la respuesta, tolerando texto extra
    alrededor del JSON.
    """
    try:
        # Intentar parsear directamente
        data = json.loads(response)
        return _build_verdict(data, phase)
    except json.JSONDecodeError:
        pass

    # Intentar extraer JSON del texto
    try:
        start = response.index("{")
        end = response.rindex("}") + 1
        data = json.loads(response[start:end])
        return _build_verdict(data, phase)
    except (ValueError, json.JSONDecodeError) as e:
        logger.error(f"No se pudo parsear el veredicto del juez: {e}")
        return None


def _build_verdict(data: dict, phase: int) -> JudgeVerdict:
    """Construye un JudgeVerdict desde un dict parseado."""
    gaps = [
        Gap(
            category=g.get("category", "unknown"),
            description=g.get("description", ""),
            severity=g.get("severity", "medium"),
        )
        for g in data.get("gaps", [])
    ]

    return JudgeVerdict(
        phase=str(data.get("phase", phase)),
        status=VerdictStatus(data.get("status", "incomplete")),
        confidence=float(data.get("confidence", 0.5)),
        summary=data.get("summary", ""),
        gaps=gaps,
        next_action=data.get("next_action", ""),
        artifacts_reviewed=data.get("artifacts_reviewed", []),
    )
