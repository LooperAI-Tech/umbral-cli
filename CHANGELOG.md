# Changelog

Todos los cambios notables de este proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

## [0.1.0] - 2026-04-26

Primera release pública alineada con el plan técnico (sprints 0–6). Umbral orquesta contexto para agentes: deposita prompts y valida artefactos; no genera código de aplicación.

### Agregado

- **CLI (Typer):** `umbral version`, `init`, `status`, `discover`, `articulate`, `design`, `ede` (list/show/validate/approve), `next`, `verify`, `build`, `profile` (show/update), `consolidate`, `metrics`.
- **Bootstrap:** estructura `.umbral/`, `umbral.yaml` (fase, juez, dominio, rol, escala), detección de `ANTHROPIC_API_KEY` para modo juez online/offline; adapters iniciales (Claude Code, Cursor).
- **EDE:** modelado Pydantic, persistencia, validación estructural por nivel.
- **Orquestación:** Jinja2 + templates bajo `src/umbral/prompts/`, orquestador y `PromptContext` (fase, perfil, EDEs).
- **Validación híbrida:** capa 1 determinista (`PhaseValidator`); capa 2 juez LLM (`PhaseJudge`, rúbricas, Anthropic / Gemini / OpenRouter, `ClientFactory`); esquema `JudgeVerdict`.
- **Comprehension Gate:** `umbral verify` con checkpoint YAML (preguntas, categorías, autoevaluación) y ajuste de perfil.
- **Sprint 5 — Perfil y governance:** `context_mastery`, promoción de roles (Explorer/Navigator/Anchor), `GovernanceMode` por bounded context, `assess_drift` heurístico, consolidación.
- **Sprint 6 — Métricas:** 13 métricas calculables donde hay datos; `umbral metrics` (Rich); telemetría del juez en `.umbral/telemetry.yaml`; documentación en `docs/methodology.md`.
- **CI:** GitHub Actions con `uv sync` y `pytest` (`.github/workflows/ci.yml`).
- **Documentación:** `README` con flujo por fases, instalación vía `uv tool install` / `pipx` y URL del repo [LooperAI-Tech/umbral-cli](https://github.com/LooperAI-Tech/umbral-cli).

### Notas

- Instalación recomendada desde Git etiquetada, p. ej. `uv tool install umbral-cli --from git+https://github.com/LooperAI-Tech/umbral-cli.git@v0.1.0`.
- Publicación en PyPI no forma parte de esta release; el paquete se consume desde el repositorio o wheel local.

[Unreleased]: https://github.com/LooperAI-Tech/umbral-cli/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/LooperAI-Tech/umbral-cli/releases/tag/v0.1.0
