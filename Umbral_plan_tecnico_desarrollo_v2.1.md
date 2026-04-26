# UMBRAL CLI — Plan de Desarrollo Técnico
## Documento de Planificación, Arquitectura y Especificación de Tareas

**Versión:** 2.1
**Stack:** Python 3.11+ · Typer · uv · Pydantic · Rich · Questionary · Anthropic SDK
**Adapters:** Claude Code · Cursor
**Modelo de validación:** Híbrido en dos capas (determinista + LLM juez)
**Cambio principal vs v2.0:** Se integra la especificación completa de la metodología del framework (flujo socrático, scaffolding adaptativo, Comprehension Gate, promoción de roles) como sección central del documento.

---

## Tabla de Contenidos

1. [Visión General de la Arquitectura](#1-visión-general-de-la-arquitectura)
2. [Metodología del Framework — Flujo por Fases](#2-metodología-del-framework--flujo-por-fases)
3. [Modelo de Validación Híbrida en Dos Capas](#3-modelo-de-validación-híbrida-en-dos-capas)
4. [Estructura del Proyecto](#4-estructura-del-proyecto)
5. [Sprint 0 — Setup y Fundamentos](#5-sprint-0--setup-y-fundamentos)
6. [Sprint 1 — Bootstrap del Proyecto (umbral init)](#6-sprint-1--bootstrap-del-proyecto)
7. [Sprint 2 — EDE Nivel 1 (Artefacto Central)](#7-sprint-2--ede-nivel-1)
8. [Sprint 3 — Adapters de Agentes (Claude Code + Cursor)](#8-sprint-3--adapters-de-agentes)
9. [Sprint 4 — Validación Híbrida y Comando `umbral next`](#9-sprint-4--validación-híbrida-y-umbral-next)
10. [Sprint 5 — Perfil Cognitivo y Governance Gradient](#10-sprint-5--perfil-cognitivo-y-governance-gradient)
11. [Sprint 6 — Métricas, CLI Status y Release v0.1.0](#11-sprint-6--métricas-cli-status-y-release)
12. [Apéndice A — Schemas Pydantic Completos](#12-apéndice-a--schemas-pydantic)
13. [Apéndice B — Templates de Prompts por Fase y Rol](#13-apéndice-b--templates-de-prompts-por-fase-y-rol)
14. [Apéndice C — Rúbricas del LLM Juez](#14-apéndice-c--rúbricas-del-llm-juez)
15. [Apéndice D — Convenciones y Estándares](#15-apéndice-d--convenciones-y-estándares)

---

## 1. Visión General de la Arquitectura

### 1.1 Principio arquitectónico central

Umbral CLI es un **orquestador de contexto y juez de transiciones**, no un generador de código. Su responsabilidad es:

1. Leer el estado del proyecto (EDEs, Perfil Cognitivo, fase activa)
2. Construir prompts contextualizados con ese estado
3. Depositar esos prompts donde el agente del usuario los lea
4. Validar los artefactos producidos en dos capas: determinista + semántica
5. Guiar al usuario sobre cuándo y cómo avanzar de fase
6. Calcular métricas de salud del framework

> **Distinción crítica:** El CLI **nunca genera código**. El agente del usuario (Claude Code/Cursor) construye. Umbral sólo evalúa si los artefactos producidos cumplen los criterios para avanzar. Esa separación de roles es lo que mantiene el framework liviano y predecible.

### 1.2 Capas de la arquitectura

```
┌─────────────────────────────────────────────────────┐
│  CLI Layer (Typer)                                  │
│  Parseo de comandos, argumentos, flags              │
│  Archivos: cli.py, commands/*.py                    │
├─────────────────────────────────────────────────────┤
│  UI Layer (Rich + Questionary)                      │
│  Output formateado, spinners, prompts interactivos  │
│  Archivos: ui/console.py, ui/prompts.py             │
├─────────────────────────────────────────────────────┤
│  Core Layer (Lógica de dominio)                     │
│  EDEs, Perfil Cognitivo, Roles, Métricas, Fases     │
│  Archivos: core/*.py                                │
├─────────────────────────────────────────────────────┤
│  Agent Layer (Orquestación + Adapters)              │
│  Construcción de prompts, inyección de contexto     │
│  Archivos: agents/orchestrator.py, agents/adapters/ │
├─────────────────────────────────────────────────────┤
│  Validation Layer (Capa 1 — Determinista)           │
│  Análisis estructural de artefactos                 │
│  Archivos: validation/*.py                          │
├─────────────────────────────────────────────────────┤
│  Judge Layer (Capa 2 — LLM Semántico)               │
│  Evalúa calidad y completitud de artefactos vía API │
│  Archivos: judge/*.py                               │
├─────────────────────────────────────────────────────┤
│  Storage Layer (Lectura/escritura de artefactos)    │
│  EDEs, Perfil, Configuración                        │
│  Archivos: storage/*.py                             │
└─────────────────────────────────────────────────────┘
```

### 1.3 Regla de dependencia

Las dependencias fluyen solo hacia abajo. La `Judge Layer` depende sólo de `Core` y `Storage`, nunca de `CLI` ni `UI`.

```
CLI → UI → Core → Storage
CLI → Agent → Core → Storage
CLI → Validation → Core → Storage
CLI → Judge → Validation → Core → Storage
```

---

## 2. Metodología del Framework — Flujo por Fases

Esta sección documenta el comportamiento esperado de cada fase del framework: qué preguntas se hacen, cómo se adaptan al rol, qué artefactos se producen, y qué criterios determinan la transición a la siguiente fase. Es la especificación funcional que los prompts, adapters y validadores deben implementar.

### 2.1 Fase 0 — Descubrimiento: de idea vaga a problema validado

**Comando:** `umbral discover`
**Entrada:** El usuario llega con una idea en lenguaje natural.
**Salida:** Problema validado + Escala definida + Mapa de Dominio + Perfil Cognitivo inicializado + Rol asignado.

#### 2.1.1 Diálogo de validación de la problemática

El Agente Mentor Socrático inicia un diálogo cuyo objetivo es que el usuario pueda describir su problema sin mencionar tecnología. Las preguntas de problemática son:

- "¿Qué problema real resuelve esto?"
- "¿Cómo se resuelve hoy sin tecnología?"
- "¿Para quién es? ¿Quién lo usaría?"
- "¿Qué datos tienes disponibles?"
- "¿Cómo sabrías si funciona?"

Si el usuario no puede explicar el problema sin mencionar tecnología, el agente reformula y vuelve a preguntar. Este loop se repite hasta que la descripción sea concreta y sin jerga técnica.

#### 2.1.2 Evaluación de escala

Una vez validada la problemática, el agente evalúa la escala del proyecto según el objetivo del usuario:

| Objetivo | Escala | Entorno | Foco |
|---|---|---|---|
| Aprender haciendo | 🧪 `learning` | Jupyter + datos locales, sin deploy | Entender conceptos |
| Validar una idea | 🚀 `mvp` | Stack mínimo viable, deploy simple | Validar con usuarios |
| Producto escalable | 🏗️ `startup` | Arquitectura desacoplada, pipeline + API + frontend | Mantenibilidad |

#### 2.1.3 Generación del Mapa de Dominio

El agente genera un Mapa de Dominio: la lista de conceptos técnicos que el usuario necesitará aprender para construir su proyecto. Los conceptos se calibran por escala:

- `learning`: 3-5 conceptos básicos del dominio.
- `mvp`: 5-8 conceptos accionables incluyendo deployment.
- `startup`: 8-12 conceptos incluyendo no-funcionales (observabilidad, testing, CI/CD).

El mapa se persiste en `.umbral/domain-map.yaml` con cada concepto marcado como `✅` (ya lo domina) o `⬜` (lo aprenderá construyendo).

#### 2.1.4 Inicialización del Perfil Cognitivo y asignación de rol

El Perfil Cognitivo se inicializa con dos dimensiones: dominio técnico y sistema. Según el nivel de experiencia declarado por el usuario, se asigna un rol:

| Nivel | Rol | EDE desbloqueada | Modo de scaffolding default |
|---|---|---|---|
| Principiante | 🔰 Explorer | EDE Nivel 1 | Modo Desbloqueo (solución completa + enseñanza) |
| Intermedio | 🧭 Navigator | EDE Nivel 2 | Modo Andamio (código con huecos) |
| Avanzado | ⚓ Anchor | EDE Nivel 3 | Modo Guía (hints mínimos) |

**Artefactos producidos:** `.umbral/domain-map.yaml`, `.umbral/phases/discovery-notes.md`, `.umbral/profile.yaml` (inicializado).

**Criterio de transición:** El usuario puede explicar el problema sin mencionar tecnología. El Mapa de Dominio tiene al menos la cantidad mínima de conceptos para la escala elegida. Se evalúa con `umbral next`.

---

### 2.2 Fase 1 — Articulación: co-creación de la spec

**Comando:** `umbral articulate`
**Entrada:** Problema validado de Fase 0.
**Salida:** Spec Co-Creada con casos borde, modos de falla, alcance y datos definidos.

#### 2.2.1 Preguntas adaptadas por rol

El Agente Mentor adapta la profundidad de las preguntas al rol del usuario:

**🔰 Explorer — Preguntas simples orientadas al usuario final:**
- "¿Qué debería mostrar la app al usuario final?"
- "¿Qué pasa si los datos están incompletos?"
- "¿Cómo sabría el usuario si la predicción es confiable?"

Cuando un concepto del dominio es necesario para responder, el agente lo enseña en contexto antes de preguntar. Ejemplo: "Antes de decidir eso, necesitas entender qué es overfitting. Es cuando..."

**🧭 Navigator — Preguntas estándar orientadas al sistema:**
- "¿Cuáles son los invariantes del sistema?"
- "¿Qué modos de falla existen?"
- "¿Cómo interactúa con servicios upstream?"

**⚓ Anchor — Preguntas avanzadas orientadas a la arquitectura:**
- "¿Qué trade-offs arquitectónicos estamos aceptando?"
- "¿Cómo afecta esto a la deuda técnica existente?"
- "¿Qué governance constraints aplican?"

#### 2.2.2 Carga de EDEs relacionadas

Si ya existen EDEs en el Registry para bounded contexts relacionados, el agente las carga como contexto para evitar contradicciones y aprovechar decisiones previas.

#### 2.2.3 Loop de articulación

El diálogo socrático se repite hasta que el usuario pueda explicar todos los casos borde por sí solo, sin ayuda del agente. Este es el gate de salida de la Fase 1.

**Artefactos producidos:** `.umbral/phases/spec-{nombre}.md` con secciones obligatorias: casos borde, modos de falla, alcance, datos de entrada.

**Criterio de transición:** La spec contiene las secciones requeridas. Los casos borde son específicos del dominio (no genéricos). El juez LLM valida que no hay ambigüedades sin resolver. Se evalúa con `umbral next`.

---

### 2.3 Fase 2 — Diseño: EDE antes de código

**Comando:** `umbral design --level {1|2|3}`
**Entrada:** Spec Co-Creada de Fase 1.
**Salida:** EDE aprobada en el Registry.

#### 2.3.1 Niveles de EDE por rol

El usuario redacta la EDE según su nivel. La complejidad escala progresivamente:

**🔰 EDE Nivel 1 (Explorer) — 2 componentes:**
1. **Qué y Cómo:** "Qué construí y cómo funciona", en las propias palabras del usuario.
2. **Por Qué básico:** "Por qué elegí esto y no otra cosa". Solo la decisión principal.

**🧭 EDE Nivel 2 (Navigator) — 4 componentes:**
1. Qué y Cómo
2. Por Qué con ADR completo (alternativas evaluadas y descartadas)
3. Qué No Hacer + anti-patrones identificados
4. Qué Sigue + continuaciones y dependencias

**⚓ EDE Nivel 3 (Anchor) — 4+ componentes:**
1. Qué y Cómo + tool bindings explícitos
2. Por Qué + ADR formal con contexto, decisión, consecuencias
3. Qué No Hacer + blast radius del cambio
4. Qué Sigue + governance constraints + validators automáticos

#### 2.3.2 Verificación de consistencia

El Agente Verificador chequea la EDE nueva contra EDEs existentes en el Registry:

- Si detecta contradicciones, el usuario debe resolver el conflicto y actualizar el ADR afectado.
- Para Explorers, el agente explica la contradicción en lenguaje simple y guía la resolución.
- Si no hay contradicciones, se procede a la recomendación de stack.

#### 2.3.3 Scale-Aware Guidance

El agente recomienda el stack tecnológico según la escala definida en Fase 0:

- 🧪 Aprendizaje → Jupyter + datos locales
- 🚀 MVP → Streamlit + SQLite (o equivalente mínimo)
- 🏗️ Startup → API + base de datos + frontend desacoplado

#### 2.3.4 Aprobación de la EDE

La EDE se guarda inicialmente como `draft`. El usuario la aprueba explícitamente antes de avanzar. Solo una EDE con `status: approved` permite pasar a la Fase 3.

**Artefactos producidos:** `.umbral/edes/{slug}.md` con frontmatter YAML y body en Markdown.

**Criterio de transición:** Al menos una EDE con status `approved`. Los componentes mínimos para el nivel están presentes. Sin contradicciones con EDEs previas. Se evalúa con `umbral next`.

---

### 2.4 Fase 3 — Construcción: scaffolding adaptativo por dominio

**Comando:** `umbral build --context {slug}`
**Entrada:** EDE aprobada + Perfil Cognitivo.
**Salida:** Código implementado + Perfil Cognitivo actualizado con conceptos aprendidos.

#### 2.4.1 Selección de modo de scaffolding

El Agente Constructor lee la EDE y el Perfil Cognitivo para determinar el nivel de dominio del usuario en este bounded context específico:

**🟢 Modo Guía (dominio ≥ 80%):**
- El agente da hints mínimos.
- El usuario escribe todo el código.
- Para Anchors y Navigators avanzados en áreas que ya dominan.

**🟡 Modo Andamio (dominio 40-79%):**
- El agente entrega código con huecos domain-specific.
- Cada hueco es un concepto del dominio que el usuario debe completar.
- Los huecos se calibran por dominio:
  - Data Science: "¿Qué modelo usas para clasificación binaria?"
  - Web: "¿Qué método HTTP corresponde a una lectura?"
  - Mobile: "¿En qué lifecycle hook cargas datos asíncronos?"

**🔴 Modo Desbloqueo (dominio < 40%):**
- El agente entrega la solución completa.
- Acompañada de enseñanza en contexto: cada bloque de código tiene una explicación del concepto.
- **Requiere explicación obligatoria antes de avanzar** (ver sección 2.4.2).

#### 2.4.2 Loop de comprensión en Modo Desbloqueo

Cuando el agente entrega código completo, el usuario debe explicar qué hace antes de poder continuar:

1. El agente pregunta: "Explícame con tus palabras: ¿por qué esta estructura? ¿Qué hace cada parte? ¿Qué pasaría si cambias X?"
2. Si la explicación es insatisfactoria, el agente escala a una pregunta socrática sobre el concepto específico: "Tu modelo tiene 99% accuracy en training pero 60% en test. ¿Por qué crees que pasa?"
3. El loop se repite hasta que el usuario demuestre comprensión.
4. Al pasar, el concepto se marca como `✅` en el Perfil Cognitivo.

#### 2.4.3 Commits incrementales y descomposición forzada

Los commits deben ser incrementales y alineados a la EDE:

- Si un cambio supera 200 líneas o toca múltiples módulos, se activa la **Descomposición Forzada**: el cambio se divide en tareas atómicas, cada una con su propia mini-EDE si es necesario.
- El loop vuelve al inicio de la Fase 3 para cada tarea descompuesta.

**Artefactos producidos:** Código implementado, Perfil Cognitivo actualizado (conceptos marcados como ✅).

**Criterio de transición:** El PR está listo. Los cambios están alineados con la EDE. Los conceptos del Modo Desbloqueo fueron explicados satisfactoriamente. Se evalúa con `umbral next`.

---

### 2.5 Fase 4 — Verificación: Comprehension Gate adaptativo

**Comando:** `umbral verify --bounded-context {slug}`
**Entrada:** PR listo + Perfil Cognitivo.
**Salida:** Merge aprobado (con o sin deuda) + Perfil Cognitivo actualizado.

#### 2.5.1 Generación de preguntas por rol

El Agente Verificador analiza el diff del PR y el Perfil Cognitivo para generar preguntas de comprensión calibradas al rol:

**🔰 Explorer — 2-3 preguntas:**
- Conceptuales del dominio: "¿Por qué dividimos en train y test?"
- Prácticas del código: "¿Qué pasa si llegan datos con valores vacíos?"

**🧭 Navigator — 3-5 preguntas:**
- Arquitectónicas: "¿Por qué exponencial y no lineal en el retry?"
- De diseño: "¿Qué trade-off aceptamos con esta estructura?"

**⚓ Anchor — 3-5 preguntas:**
- Sistémicas: "¿Cómo afecta este cambio al blast radius del servicio?"
- De gobernanza: "¿Qué validators faltan para operar sin supervisión?"

Las preguntas se generan determinísticamente a partir de: conceptos tocados por el cambio, conceptos aún no verificados en el Perfil, y el nivel del rol. Solo se preguntan conceptos que el usuario no haya demostrado dominar previamente.

#### 2.5.2 Evaluación de comprensión y resultado

El usuario responde las preguntas y se autoevalúa. Según el nivel de comprensión demostrada:

**Comprensión alta → Merge sin deuda:**
- Todos los conceptos involucrados se marcan como `✅` en el Perfil Cognitivo.
- El merge procede limpio.

**Comprensión parcial → Merge con Comprehension Debt:**
- El merge es permitido, pero se registra deuda explícita.
- El concepto específico que no se comprendió queda marcado como gap.
- La métrica CDR (Comprehension Debt Ratio) se incrementa.

**Comprensión baja → Retorno a Fase 3 en Modo Desbloqueo:**
- No se permite el merge.
- El usuario regresa a la Fase 3 con los conceptos específicos que faltan, activando el Modo Desbloqueo para esos conceptos.

#### 2.5.3 Registro del Comprehension Checkpoint

Cada ejecución del gate se persiste en `.umbral/phases/checkpoint-{ede-slug}.yaml` con: preguntas formuladas, categoría de cada pregunta, concepto evaluado, autoevaluación del usuario, y flag de deuda.

**Artefactos producidos:** `checkpoint-{slug}.yaml`, Perfil Cognitivo actualizado, métricas CDR y DKC actualizadas.

**Criterio de transición:** El checkpoint existe. Las respuestas no son vacías. La autoevaluación es coherente con el contenido. Se evalúa con `umbral next`.

---

### 2.6 Fase 5 — Consolidación: memoria institucional y progresión

**Comando:** `umbral consolidate`
**Entrada:** Merge completado + EDE + Perfil Cognitivo.
**Salida:** EDE actualizada + Perfil consolidado + Evaluación de promoción de rol.

#### 2.6.1 Detección de drift EDE vs código

El Agente Verificador compara la EDE pre-implementación contra el código final. Tres resultados posibles:

**Sin drift:** La EDE y el código son coherentes. Se procede directamente a la consolidación del Perfil.

**Drift menor:** Ajustes pequeños (ej: el threshold cambió de 0.65 a 0.60 tras evaluación empírica). El usuario actualiza la EDE con los valores reales.

**Drift significativo:** El código divergió sustancialmente de lo planificado. El usuario documenta un nuevo ADR respondiendo: "¿Por qué divergió? ¿Qué aprendimos? ¿Qué cambiamos para la próxima vez?" Para Explorers, el agente guía este proceso con preguntas.

#### 2.6.2 Consolidación del Perfil Cognitivo

El Perfil Cognitivo se consolida con un resumen de:

- Conceptos del dominio marcados como ✅ (verificados en el Comprehension Gate).
- Conceptos pendientes ⬜ (candidatos para el próximo feature).
- Comprensión del sistema (bounded contexts cubiertos).
- Comprehension debt acumulada.
- EDEs escritas por nivel.

#### 2.6.3 Evaluación de promoción de rol

Al consolidar, el framework evalúa si el usuario cumple criterios para subir de rol:

**🔰 Explorer → 🧭 Navigator:**
- Tiene ≥ 3 EDEs Nivel 1 exitosas.
- DKC (Domain Knowledge Coverage) ≥ 50%.
- Al promocionarse desbloquea: EDE Nivel 2, Modo Andamio como default, preguntas de Comprehension Gate más profundas.

**🧭 Navigator → ⚓ Anchor:**
- Tiene EDEs Nivel 2 escritas y validadas.
- Es Anchor de al menos 1 bounded context (alta comprensión demostrada).
- Al promocionarse desbloquea: EDE Nivel 3, Modo Guía como default, puede validar Comprehension Gates de otros usuarios.

**⚓ Anchor — Ya es nivel máximo:**
- Consolida: revisa drift de EDEs, valida Comprehension Gates de Navigators y Explorers, expande el Governance Gradient del área.

Si no cumple criterios, el usuario continúa en su rol actual con un mensaje indicando cuánto le falta.

#### 2.6.4 Loop de features

Al terminar la consolidación, el framework evalúa si el siguiente feature es en un área conocida o nueva:

- **Área conocida (no requiere Fase 0):** Se salta directamente a la Fase 1 (Articulación).
- **Área o dominio nuevo:** Se regresa a la Fase 0 (Descubrimiento) para validar la nueva problemática.

**Artefactos producidos:** EDE actualizada (si hubo drift), Perfil Cognitivo consolidado, `.umbral/umbral.yaml` actualizado con rol nuevo si hubo promoción.

**Criterio de transición:** EDE Registry sincronizado. Drift documentado (o ausente). Perfil Cognitivo consolidado. Se evalúa con `umbral next`.

---

### 2.7 Governance Gradient — Autonomía adaptativa

El Governance Gradient controla cuánta autonomía tiene el agente según la cobertura de EDEs en un bounded context:

| Estado de EDE | Modo de operación | Comportamiento | Rol típico |
|---|---|---|---|
| Sin EDE | Supervisado | Todo requiere revisión humana completa + comprehension check | 🔰 Explorer en área nueva |
| EDE parcial (Nivel 1-2) | Híbrido | Gates selectivos solo en cambios de alto impacto | 🧭 Navigator |
| EDE completa (Nivel 3) | Autónomo | Agente opera dentro de la EDE con verificación automática | ⚓ Anchor |

El gradient puede retroceder: si se detecta drift significativo o degradación en un bounded context, el nivel baja de Autónomo a Híbrido hasta que la EDE se actualice.

---

### 2.8 Perfil Cognitivo — Doble dimensión

El Perfil Cognitivo tiene dos dimensiones que se actualizan independientemente:

**Dimensión 1 — Dominio Técnico:** Conceptos del dominio específico del proyecto (ej: overfitting, feature engineering, precision/recall para Data Science; HTTP methods, middleware, ORM para Web). Se inicializa en Fase 0 con el Mapa de Dominio y se actualiza en Fases 3 y 4 al verificar comprensión.

**Dimensión 2 — Sistema:** Conocimiento sobre el sistema que se está construyendo (ej: pipeline de datos, modelo de entrenamiento, API de predicción). Se actualiza al escribir EDEs y al completar Comprehension Gates.

---

### 2.9 Observabilidad — 13 métricas de salud

**Comprensión:**
- **CC (Comprehension Coverage):** % del codebase cubierto por al menos una EDE activa.
- **CDR (Comprehension Debt Ratio):** PRs con deuda / total de PRs.
- **ARI (Anchor Redundancy Index):** Anchors por bounded context.

**Progresión:**
- **NAV (Navigator to Anchor Velocity):** Semanas promedio de progresión de Navigator a Anchor.
- **DKC (Domain Knowledge Coverage):** % de conceptos del dominio marcados como ✅.
- **LBB (Learning by Building Ratio):** Conceptos aprendidos construyendo / total.

**Calidad técnica:**
- **CRF (Context Rot Frequency):** Ciclos guess-fail del agente por semana (indica EDEs desactualizadas).
- **EDS (EDE Drift Score):** Divergencia medida entre EDE y código real.

**Velocidad:**
- **ET (Effective Throughput):** Features que sobreviven 30 días sin rewrite.
- **ETP (Explorer to Product Time):** Semanas desde idea hasta MVP funcional.

**Juez (nuevas en v2.0):**
- **JIR (Judge Invocation Rate):** Llamadas al juez por feature.
- **JCR (Judge Concurrence Rate):** % de veredictos `complete` vs total.
- **JFR (Judge Fallback Rate):** % de invocaciones que cayeron a modo offline.

---

## 3. Modelo de Validación Híbrida en Dos Capas

### 3.1 El problema que resuelve

Sin el comando `umbral next`, el usuario debía saber qué comando ejecutar al terminar cada fase. El modelo A+B (determinista + LLM juez) automatiza esa decisión.

### 3.2 Dos capas, dos costos, dos garantías

`umbral next` ejecuta validación en cascada. Si la Capa 1 falla, no se invoca la Capa 2.

**Capa 1 — Validación determinista (siempre se ejecuta):**
Lee artefactos del disco y verifica presencia, estructura y formato. Sin red, sin costo, sin latencia.

**Capa 2 — LLM juez (sólo si Capa 1 pasa):**
Llama a la API con un modelo barato y una rúbrica predefinida por fase. El modelo lee los artefactos y emite un veredicto JSON.

Lo que el juez evalúa por fase:

- **Fase 0:** ¿La descripción es concreta o vaga? ¿El Mapa de Dominio cubre los conceptos esenciales?
- **Fase 1:** ¿Los casos borde son realistas o superficiales? ¿Hay ambigüedades sin resolver?
- **Fase 2:** ¿La EDE describe decisiones reales o es declarativa sin justificación?
- **Fase 3:** ¿El código es coherente con la EDE? ¿Hay scope creep?
- **Fase 4:** ¿Las respuestas del Comprehension Gate demuestran comprensión real o son repeticiones?

Lo que el juez **nunca** hace: generar código, reescribir artefactos, inventar contenido, reemplazar al agente.

### 3.3 Flujo del comando `umbral next`

```
$ umbral next
      │
      ▼
Lee fase activa de .umbral/umbral.yaml
      │
      ▼
Capa 1 — PhaseValidator (determinista)
      │
  ┌───┴───┐
  ▼       ▼
¿Falló?  ¿Pasó?
  │       │
  ▼       ▼
Gaps    Capa 2 — PhaseJudge (LLM)
estruc-       │
turales  ┌────┴────┐
  │      ▼         ▼
  │  incomplete  complete
  │      │         │
  │      ▼         ▼
  │   Gaps      Avanza fase
  │   semánticos   en yaml
  │   + acción     + siguiente
  │   sugerida     comando
  └──────┴─────────┘
```

### 3.4 Configuración del LLM juez

```yaml
# .umbral/umbral.yaml
judge:
  mode: online              # online | offline
  provider: anthropic        # anthropic | gemini | openai | deepseek | openrouter
  model: claude-haiku-4-5    # el modelo específico del proveedor
  max_tokens: 800
  temperature: 0.2
  fallback_to_offline: true
```

**Modo `online`:** Capa 1 + Capa 2. Validación semántica activa.
**Modo `offline`:** Solo Capa 1. Aviso de que la validación es solo estructural.

### 3.5 Costos esperados

Con claude-haiku como juez (~1500 tokens entrada + ~400 salida), un feature completo (6 fases, ~10 llamadas) cuesta centavos de USD.

---

## 4. Estructura del Proyecto

### 4.1 Árbol completo del repositorio

```
umbral/
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
├── .gitignore
│
├── src/
│   └── umbral/
│       ├── __init__.py
│       ├── cli.py                         # Entry point de Typer
│       │
│       ├── commands/
│       │   ├── __init__.py
│       │   ├── init_cmd.py                # umbral init
│       │   ├── next_cmd.py                # umbral next
│       │   ├── discover.py                # umbral discover (Fase 0)
│       │   ├── articulate.py              # umbral articulate (Fase 1)
│       │   ├── design.py                  # umbral design (Fase 2)
│       │   ├── build.py                   # umbral build (Fase 3)
│       │   ├── verify.py                  # umbral verify (Fase 4)
│       │   ├── consolidate.py             # umbral consolidate (Fase 5)
│       │   ├── status.py                  # umbral status
│       │   ├── metrics.py                 # umbral metrics
│       │   ├── ede_cmd.py                 # umbral ede [list|show|validate]
│       │   └── profile_cmd.py             # umbral profile [show|update]
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── ede.py                     # Modelo EDE (Pydantic)
│       │   ├── profile.py                 # Modelo Perfil Cognitivo
│       │   ├── role.py                    # Lógica Explorer/Navigator/Anchor
│       │   ├── phase.py                   # Estado de fases
│       │   ├── governance.py              # Governance Gradient
│       │   ├── metrics.py                 # Cálculo de 13 métricas
│       │   ├── domain_map.py              # Mapa de Dominio
│       │   └── config.py                  # Configuración del proyecto
│       │
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── orchestrator.py            # Construye prompts contextualizados
│       │   ├── context_builder.py         # Inyecta EDEs y perfil en prompts
│       │   ├── base_adapter.py            # Interfaz abstracta de adapter
│       │   └── adapters/
│       │       ├── __init__.py
│       │       ├── claude_code.py
│       │       └── cursor.py
│       │
│       ├── validation/                    # Capa 1: determinista
│       │   ├── __init__.py
│       │   ├── phase_validator.py
│       │   ├── ede_consistency.py
│       │   ├── comprehension_gate.py
│       │   └── drift_detector.py
│       │
│       ├── judge/                         # Capa 2: LLM juez
│       │   ├── __init__.py
│       │   ├── phase_judge.py
│       │   ├── base_client.py             # Interfaz abstracta (ABC)
│       │   ├── clients/
│       │   │   ├── __init__.py
│       │   │   ├── anthropic_client.py
│       │   │   ├── gemini_client.py
│       │   │   └── openrouter_client.py
│       │   ├── client_factory.py
│       │   ├── verdict.py
│       │   ├── prompt_builder.py
│       │   └── rubrics/
│       │       ├── discovery.md
│       │       ├── articulation.md
│       │       ├── design.md
│       │       ├── construction.md
│       │       └── verification.md
│       │
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── ede_store.py
│       │   ├── profile_store.py
│       │   ├── phase_store.py
│       │   └── paths.py
│       │
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── console.py
│       │   ├── prompts.py
│       │   ├── tables.py
│       │   └── verdict_display.py
│       │
│       └── prompts/                       # Templates de prompts
│           ├── phases/
│           │   ├── discovery.md
│           │   ├── articulation.md
│           │   ├── design.md
│           │   ├── construction.md
│           │   └── verification.md
│           ├── socratic/
│           │   ├── explorer_questions.md
│           │   ├── navigator_questions.md
│           │   └── anchor_questions.md
│           └── scaffolding/
│               ├── ds_scaffolds.md
│               ├── web_scaffolds.md
│               └── mobile_scaffolds.md
│
├── templates/
│   ├── ede-level-1.md
│   ├── ede-level-2.md
│   ├── ede-level-3.md
│   ├── profile.yaml
│   ├── domain-map.yaml
│   └── umbral.yaml
│
├── tests/
│   ├── conftest.py
│   ├── test_core/
│   ├── test_validation/
│   ├── test_judge/
│   ├── test_agents/
│   └── test_commands/
│
└── docs/
    ├── getting-started.md
    ├── architecture.md
    ├── methodology.md                     # Documenta la sección 2
    ├── judge-rubrics.md
    ├── contributing.md
    └── adapters.md
```

### 4.2 Dependencias en `pyproject.toml`

```toml
[project]
name = "umbral-cli"
version = "0.1.0"
description = "Framework de desarrollo con comprensión sostenible"
requires-python = ">=3.11"
dependencies = [
    "typer>=0.12.0",
    "pydantic>=2.7.0",
    "pyyaml>=6.0.1",
    "rich>=13.7.0",
    "questionary>=2.0.1",
    "jinja2>=3.1.4",
    "anthropic>=0.40.0",
    "tenacity>=8.2.0",
]

[project.scripts]
umbral = "umbral.cli:app"
```

---

## 5. Sprint 0 — Setup y Fundamentos

**Duración:** Semanas 1-2
**Objetivo:** Entorno funcional con `umbral version` ejecutable y test pasando.

Se instala uv, se inicializa el paquete, se configura pyproject.toml, y se construye un primer entry point con Typer.

**Criterio de éxito:** `uv run umbral version` muestra `umbral v0.1.0`. `uv run pytest` pasa 1 test verde.

---

## 6. Sprint 1 — Bootstrap del Proyecto

**Duración:** Semanas 3-5
**Objetivo:** `umbral init mi-proyecto` crea toda la estructura necesaria, incluyendo configuración del juez.

Este sprint implementa: resolución de rutas (`paths.py`), modelo de configuración (`config.py` con Pydantic), el comando `umbral init` con prompts interactivos (agente, escala, dominio, rol, modo del juez), setup de adapters para Claude Code y Cursor, inicialización del Perfil Cognitivo, y el comando `umbral status`.

Incluye la detección de `ANTHROPIC_API_KEY` para configurar el modo del juez (online vs offline). El `umbral status` siempre sugiere `umbral next` como siguiente paso.

**Criterio de éxito:** `umbral init predictor-churn` crea `.umbral/` con todos los subdirectorios, `umbral.yaml`, `profile.yaml`, y archivos de adapter para Claude Code. Tests pasan.

---

## 7. Sprint 2 — EDE Nivel 1

**Duración:** Semanas 6-8
**Objetivo:** Modelado y persistencia de EDEs Nivel 1 con validación estructural.

Este sprint implementa: el schema Pydantic de la EDE con validadores por nivel, el `EDEStore` para CRUD en disco, y los comandos `umbral design --level 1`, `umbral ede list`, `umbral ede show`, `umbral ede validate`.

El comando `umbral design` sigue la metodología de la sección 2.3: presenta al usuario los componentes requeridos para su nivel, valida contra el Registry, y aplica Scale-Aware Guidance.

**Criterio de éxito:** `umbral design --level 1` crea una EDE válida. `umbral ede validate` detecta componentes faltantes. Tests pasan.

---

## 8. Sprint 3 — Adapters de Agentes

**Duración:** Semanas 9-11
**Objetivo:** Orquestación de prompts contextualizados para Claude Code y Cursor.

Este sprint implementa: la interfaz abstracta `BaseAdapter`, los adapters para Claude Code (deposita en `.claude/commands/`) y Cursor (deposita en `.cursor/rules/`), y el `Orchestrator` que construye prompts con todo el contexto del proyecto.

Los prompts depositados implementan la metodología de la sección 2: incluyen las preguntas socráticas adaptadas por rol, las instrucciones de scaffolding por dominio, las reglas de Umbral (no generar código sin EDE, método socrático, commits < 200 líneas), y la instrucción de ejecutar `umbral next` al terminar.

Los templates de prompts viven en `src/umbral/prompts/` y se renderizan con Jinja2 inyectando: nombre del proyecto, dominio, escala, rol, fase activa, EDEs existentes, Perfil Cognitivo, y próximo concepto a enseñar.

**Criterio de éxito:** `umbral discover` deposita un prompt contextualizado en `.claude/commands/discover.md`. El prompt contiene las preguntas de problemática adaptadas al rol. Tests de adapters pasan.

---

## 9. Sprint 4 — Validación Híbrida y `umbral next`

**Duración:** Semanas 12-14
**Objetivo:** Implementar las dos capas de validación, el Comprehension Gate, y el comando guía.

### 9.1 PhaseValidator (Capa 1 — determinista)

Valida presencia y estructura de artefactos por fase. Sin red, sin costo. Ver sección 3.2 para detalle de qué chequea por fase.

### 9.2 BaseJudgeClient y clients

Interfaz abstracta `BaseJudgeClient` con un único método `complete(system, user, max_tokens, temperature) -> str | None`. Implementaciones para Anthropic, Gemini, y OpenRouter. `ClientFactory` selecciona el cliente según `judge.provider` en `umbral.yaml`.

### 9.3 JudgeVerdict (schema Pydantic)

```python
class VerdictStatus(str, Enum):
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    NEEDS_REVISION = "needs_revision"

class Gap(BaseModel):
    category: str    # 'edge_case', 'rationale', 'scope', etc.
    description: str
    severity: str    # 'high' | 'medium' | 'low'

class JudgeVerdict(BaseModel):
    phase: str
    status: VerdictStatus
    confidence: float  # 0.0 a 1.0
    summary: str
    gaps: list[Gap]
    next_action: str
    artifacts_reviewed: list[str]
```

### 9.4 PhaseJudge (Capa 2 — LLM)

Recolecta artefactos relevantes por fase, carga la rúbrica correspondiente, construye el prompt, llama al cliente, y parsea el veredicto JSON. Si la API falla, devuelve None y el comando degrada a modo offline.

### 9.5 ComprehensionGate

Genera preguntas deterministas basadas en: conceptos tocados por el cambio, rol del usuario, y conceptos aún no verificados. Sigue la especificación de la sección 2.5 para la cantidad y tipo de preguntas por rol.

### 9.6 Comando `umbral next`

Ejecuta la cascada Capa 1 → Capa 2. Avanza la fase automáticamente si el veredicto es `complete`. Muestra gaps específicos si es `incomplete` o `needs_revision`. Degrada a modo offline si no hay API key o la API falla.

### 9.7 Comando `umbral verify`

Ejecuta el Comprehension Gate según la sección 2.5. Genera preguntas calibradas al rol, el usuario responde, se autoevalúa, y el Perfil Cognitivo se actualiza. Persiste el checkpoint en disco.

**Criterio de éxito:** `umbral next` ejecuta cascada correctamente. `umbral verify` genera preguntas calibradas al rol. Tests cubren ambas capas con mocks.

---

## 10. Sprint 5 — Perfil Cognitivo y Governance Gradient

**Duración:** Semanas 15-17
**Objetivo:** Tracking de comprensión por bounded context, lógica de promoción de roles, Governance Gradient funcional.

Este sprint implementa: el modelo Pydantic del Perfil Cognitivo con doble dimensión (sección 2.8), la lógica de evaluación de criterios de promoción según la sección 2.6.3 (Explorer→Navigator→Anchor), el cálculo del Governance Gradient por bounded context (sección 2.7), y los comandos `umbral profile show`, `umbral profile update`, `umbral build`.

El comando `umbral build` implementa la selección de modo de scaffolding de la sección 2.4.1: lee el Perfil Cognitivo, determina el nivel de dominio, y deposita el prompt con las instrucciones de Modo Guía, Andamio o Desbloqueo según corresponda.

El comando `umbral consolidate` implementa la detección de drift (sección 2.6.1), la consolidación del Perfil (sección 2.6.2), y la evaluación de promoción (sección 2.6.3).

Diferido a v0.2.0: historial temporal del perfil, degradación de conocimiento por inactividad, Knowledge Topology como grafo navegable.

---

## 11. Sprint 6 — Métricas, CLI Status y Release

**Duración:** Semanas 18-20
**Objetivo:** 13 métricas calculables, dashboard de status, documentación, release pública.

Este sprint implementa: cálculo de las 13 métricas (sección 2.9), el comando `umbral metrics` con dashboard visual en Rich, documentación completa (incluyendo `docs/methodology.md` basado en la sección 2), CI/CD con GitHub Actions, y publicación via `uv tool install`.

**Criterio de éxito:** `umbral metrics` muestra dashboard con al menos las métricas que tienen datos. Documentación publicada. Release v0.1.0 disponible.

---

## 12. Apéndice A — Schemas Pydantic

Los schemas completos se encuentran en los sprints: EDE (Sprint 2), Perfil Cognitivo (Sprint 5), Config (Sprint 1), JudgeVerdict (Sprint 4).

---

## 13. Apéndice B — Templates de Prompts por Fase y Rol

### B.1 Template de Fase 0 (Discovery)

```markdown
# Umbral — Fase 0: Descubrimiento

## Contexto del Proyecto
- Proyecto: {{ project_name }}
- Dominio: {{ domain }}
- Escala: {{ scale }}
- Rol: {{ role }}

## Tu rol como Agente Mentor Socrático

Estás guiando a un usuario en la Fase 0. Tu objetivo es convertir una idea
vaga en un problema validado.

### Reglas estrictas:
1. NUNCA des la respuesta directa. Siempre haz preguntas.
2. Preguntas de problemática:
   - "¿Qué problema real resuelve esto?"
   - "¿Cómo se resuelve hoy sin tecnología?"
   - "¿Para quién es? ¿Quién lo usaría?"
   - "¿Qué datos tienes disponibles?"
   - "¿Cómo sabrías si funciona?"
3. No avances hasta que el usuario pueda explicar el problema sin
   mencionar tecnología.
4. Una vez validada la problemática, genera un Mapa de Dominio.

{% if role == "explorer" %}
### Adaptación para Explorer:
- Usa lenguaje simple y accesible
- Cuando un concepto técnico sea necesario, explícalo en contexto
- No asumas conocimiento previo del dominio
{% endif %}

## Output esperado:
1. Descripción del problema en .umbral/phases/discovery-notes.md
2. Mapa de Dominio en .umbral/domain-map.yaml

## Cuando termines:
Indica al usuario: `umbral next`
```

### B.2 Template de Fase 1 (Articulación)

```markdown
# Umbral — Fase 1: Articulación

## Contexto
- Proyecto: {{ project_name }}
- Dominio: {{ domain }}
- Escala: {{ scale }}
- Rol: {{ role }}
- Mapa de Dominio: {{ domain_map_summary }}

{% if role == "explorer" %}
## Preguntas adaptadas para Explorer:
Usa preguntas simples orientadas al usuario final:
- "¿Qué debería mostrar la app al usuario final?"
- "¿Qué pasa si los datos están incompletos?"
- "¿Cómo sabría el usuario si la predicción es confiable?"

Cuando un concepto del dominio sea necesario para responder, enseña
el concepto ANTES de continuar con la pregunta.
{% elif role == "navigator" %}
## Preguntas para Navigator:
- "¿Cuáles son los invariantes del sistema?"
- "¿Qué modos de falla existen?"
- "¿Cómo interactúa con servicios upstream?"
{% elif role == "anchor" %}
## Preguntas para Anchor:
- "¿Qué trade-offs arquitectónicos estamos aceptando?"
- "¿Cómo afecta esto a la deuda técnica existente?"
- "¿Qué governance constraints aplican?"
{% endif %}

{% if related_edes %}
## EDEs relacionadas (cargadas como contexto):
{% for ede in related_edes %}
- [{{ ede.slug }}] {{ ede.title }} (Nivel {{ ede.level }})
{% endfor %}
{% endif %}

## Output esperado:
Spec Co-Creada en .umbral/phases/spec-{{ project_slug }}.md con:
- Casos borde (al menos 2 específicos)
- Modos de falla (con consecuencia)
- Alcance (qué SÍ y qué NO)
- Datos de entrada identificados

## Gate de salida:
El usuario puede explicar todos los casos borde sin tu ayuda.
Si no puede, reformula y profundiza.

## Cuando termines:
Indica al usuario: `umbral next`
```

### B.3 Template de Fase 3 (Construcción)

```markdown
# Umbral — Fase 3: Construcción

## Contexto
- Proyecto: {{ project_name }}
- Bounded context: {{ bounded_context }}
- EDE activa: {{ ede_slug }} (Nivel {{ ede_level }})
- Rol: {{ role }}
- Dominio del usuario en este context: {{ domain_level }}%

## EDE a implementar:
{{ ede_content }}

{% if domain_level >= 80 %}
## Modo: 🟢 GUÍA
Da hints mínimos. El usuario escribe el código.
No entregues soluciones completas.
{% elif domain_level >= 40 %}
## Modo: 🟡 ANDAMIO
Entrega código con huecos domain-specific. Cada hueco = un concepto.
{% if domain == "data-science" %}
Ejemplos de huecos: "¿Qué modelo para clasificación binaria?"
"¿Por qué test_size=0.2 y no 0.5?"
{% elif domain == "web" %}
Ejemplos de huecos: "¿Qué método HTTP para lectura?"
"¿Por qué middleware antes del handler?"
{% endif %}
{% else %}
## Modo: 🔴 DESBLOQUEO
Entrega la solución completa con enseñanza en contexto.
Cada bloque de código debe tener una explicación del concepto.

IMPORTANTE: Antes de continuar, pide al usuario que explique
el código que recibió:
- "¿Por qué esta estructura?"
- "¿Qué hace cada parte?"
- "¿Qué pasaría si cambias X?"

Si no puede explicar, haz preguntas socráticas sobre el concepto
específico que falta.
{% endif %}

## Próximo concepto a enseñar:
{{ next_concept }}

## Reglas de commits:
- Máximo 200 líneas por cambio
- Si el cambio es multi-módulo, descomponer en tareas atómicas
- Cada commit alineado a la EDE

## Cuando termines:
Indica al usuario: `umbral next`
```

---

## 14. Apéndice C — Rúbricas del LLM Juez

Cada rúbrica es un Markdown en `src/umbral/judge/rubrics/` que define criterios para `complete`, `incomplete` y `needs_revision`. Las rúbricas se calibran al rol del usuario.

### C.1 Rúbrica de Fase 0 — Discovery

Evalúa: `discovery-notes.md` + `domain-map.yaml`. Criterios: problema sin jerga técnica, usuario objetivo identificado, Mapa de Dominio coherente con la escala (learning: 3-5 conceptos, mvp: 5-8, startup: 8-12), estado actual descrito.

### C.2 Rúbrica de Fase 1 — Articulación

Evalúa: `spec-*.md`. Criterios: ≥2 casos borde específicos, modos de falla con consecuencia, alcance delimitado, datos de entrada identificados. Calibración por rol: Explorer solo necesita casos prácticos; Navigator invariantes; Anchor trade-offs.

### C.3 Rúbrica de Fase 2 — Diseño

Evalúa: `.umbral/edes/*.md`. Criterios por nivel: EDE N1 requiere 2 componentes con contenido concreto; EDE N2 requiere 4 componentes con ADR y alternativa descartada; EDE N3 requiere tool bindings, ADR formal, blast radius y governance.

### C.4 Rúbrica de Fase 3 — Construcción

Evalúa: coherencia EDE vs código. Criterios: nombres y conceptos de la EDE reflejados en el código, sin scope creep, restricciones del "Qué No Hacer" respetadas. Nota: en v0.1.0 sin integración Git, evaluación liviana.

### C.5 Rúbrica de Fase 4 — Verificación

Evalúa: `checkpoint-*.yaml`. Criterios: checkpoint presente, respuestas con contenido real (no monosílabos ni repeticiones), autoevaluación coherente.

---

## 15. Apéndice D — Convenciones y Estándares

### Convención de nombres de archivos
- EDEs: `slug-en-kebab-case.md`
- Fases: `{fase}-{descriptor}.{ext}`
- Checkpoints: `checkpoint-{ede-slug}.yaml`
- Rúbricas: `{phase_name}.md`
- Templates de prompts: organizados por `phases/`, `socratic/`, `scaffolding/`

### Formato de EDEs
- Frontmatter: YAML entre `---`
- Body: Markdown con H2 por componente

### Versionamiento
- SemVer estricto: `MAJOR.MINOR.PATCH`

### Branching
- `main`: estable publicada
- `develop`: integración
- `feature/{nombre}`: por feature
- `release/v{version}`: preparación

### Manejo de API keys
- Nunca commitear `.env` con keys
- El CLI nunca persiste keys en `umbral.yaml`
- En CI, usar secretos del repositorio

---

## Resumen del Roadmap (v2.1)

| Sprint | Semanas | Entregable | Comandos nuevos |
|---|---|---|---|
| 0 | 1-2 | Entorno + hello world | `umbral version` |
| 1 | 3-5 | Bootstrap + status | `umbral init`, `umbral status` |
| 2 | 6-8 | EDE funcional | `umbral design`, `umbral ede [list\|show\|validate]` |
| 3 | 9-11 | Orquestación de prompts | `umbral discover`, `umbral articulate` |
| 4 | 12-14 | Validación híbrida + LLM juez + Comprehension Gate | `umbral next`, `umbral verify` |
| 5 | 15-17 | Perfil Cognitivo + Roles + Governance + Consolidación | `umbral profile`, `umbral build`, `umbral consolidate` |
| 6 | 18-20 | Métricas + Release | `umbral metrics` |

**Total estimado:** 20 semanas a 10-15 horas semanales.

**Release v0.1.0** incluye:

- Fases 0-5 con flujo guiado vía `umbral next`.
- Metodología socrática completa: preguntas adaptadas por rol, scaffolding por dominio, Comprehension Gate adaptativo, detección de drift, y promoción de roles.
- 2 adapters (Claude Code + Cursor).
- Validación híbrida en dos capas: determinista + LLM juez (multi-proveedor).
- 13 métricas calculables.
- Modo offline para usuarios sin API key.
- Documentación completa incluyendo `docs/methodology.md`.

**Diferido a v0.2.0:**

- Knowledge Topology (grafo navegable de EDEs).
- Historial temporal del Perfil Cognitivo.
- Degradación de conocimiento por inactividad.
- Integración directa con Git para análisis de diffs en Fase 3.
- Adapters adicionales (Copilot, Codex).
- Multi-modelo configurable para el juez.

---

## Cambios respecto de v2.0

| Área | v2.0 | v2.1 |
|---|---|---|
| Metodología | No documentada — vivía solo en el diagrama de flujo | Sección 2 completa: especificación funcional de cada fase, preguntas por rol, modos de scaffolding, criterios de transición |
| Preguntas socráticas | Implícitas en los templates de prompts | Documentadas explícitamente por fase y rol (secciones 2.1-2.6) |
| Scaffolding adaptativo | Mencionado pero no especificado | 3 modos detallados con ejemplos por dominio (sección 2.4) |
| Comprehension Gate | Solo el código del gate | Especificación de cantidad y tipo de preguntas por rol (sección 2.5) |
| Drift y consolidación | No documentado | Especificación de 3 tipos de drift y sus resoluciones (sección 2.6) |
| Promoción de roles | Criterios no documentados | Criterios explícitos con qué desbloquea cada promoción (sección 2.6.3) |
| Governance Gradient | Mencionado | Tabla de 3 estados con comportamiento y degradación (sección 2.7) |
| Perfil Cognitivo | Schema Pydantic referenciado | Doble dimensión especificada con ejemplos (sección 2.8) |
| Métricas | 13 listadas sin contexto | 13 métricas agrupadas por categoría con descripción (sección 2.9) |
| Templates de prompts | Solo template de Fase 0 | Templates para Fase 0, 1 y 3 con lógica condicional por rol (Apéndice B) |
| Juez multi-proveedor | Solo Anthropic | `base_client.py` + `clients/` con factory pattern (sección 4.1 + 9.2) |