# Metodología Umbral (resumen)

Este documento resume el flujo por fases del framework descrito en el plan técnico. Umbral CLI **no genera código**: orquesta contexto, deposita prompts y valida artefactos.

## Principio

1. Leer estado (EDEs, perfil, fase activa).
2. Construir y depositar prompts contextualizados para el agente del usuario.
3. Validar en **dos capas**: validación determinista (estructura) y, si aplica, juez LLM (semántica).
4. Guiar el avance con `umbral next` y métricas de salud.

## Fases 0 a 5 (visión rápida)

| Fase | Comando típico | Objetivo |
|------|----------------|----------|
| 0 Descubrimiento | `umbral discover` | Problema validado, escala, mapa de dominio, rol. |
| 1 Articulación | `umbral articulate` | Spec con casos borde, fallas, alcance, datos. |
| 2 Diseño | `umbral design` | EDE con componentes según nivel (1/2/3). |
| 3 Construcción | `umbral build -c <contexto>` | Scaffolding según dominio (Guía / Andamio / Desbloqueo). |
| 4 Verificación | `umbral verify` | Comprehension Gate; checkpoint en disco. |
| 5 Consolidación | `umbral consolidate` | Drift EDE–código, perfil, promoción de rol, governance. |

## Validación híbrida

- **Capa 1:** siempre, sin red (`PhaseValidator`).
- **Capa 2:** juez LLM solo si la capa 1 pasa; modo `offline` en `umbral.yaml` limita a capa 1.

## Perfil cognitivo y roles

- Dimensiones: **dominio técnico** (conceptos) y **sistema** (bounded contexts).
- Roles: Explorer → Navigator → Anchor con criterios de promoción en consolidación.

## Governance gradient

Según madurez de la EDE en un contexto: supervisado → híbrido → autónomo (N1–2 vs N3).

## Métricas (v0.1.0)

Trece métricas definidas en la sección 2.9 del plan; varias requieren historial o integraciones futuras. El comando `umbral metrics` muestra las calculables con los datos locales (perfil, EDEs, código, telemetría del juez).

---

Referencia completa: plan de desarrollo técnico del repositorio y código en `src/umbral/`.
