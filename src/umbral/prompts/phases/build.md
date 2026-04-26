# Umbral — Fase 3: Construcción (`build` — contexto: {{ bounded_context or focus_ede_slug }})

## Contexto
- Proyecto: {{ project_name }}
- Dominio: {{ domain }}
- Escala: {{ scale }}
- Rol: {{ role }}
- Bounded context: {{ bounded_context or focus_ede_slug }}
- Mastery en contexto: {{ mastery_in_context | round(1) }} % (DKC global: {{ dkc | round(1) }} %)

## Modo de scaffolding: **{{ scaffolding_mode }}**
{% if scaffolding_mode == "guia" %}
### Modo: Guía
Hints mínimos. El usuario escribe el código. No entregues soluciones completas.
{% elif scaffolding_mode == "andamio" %}
### Modo: Andamio
Código con huecos **domain-specific**. Cada hueco = un concepto del dominio que el usuario debe completar.
{% if domain == "data-science" %}
Ejemplos: «¿Qué modelo para clasificación binaria?», «¿Cómo evitas el sobreajuste?»
{% elif domain == "web" %}
Ejemplos: «¿Qué verbo HTTP para lectura?», «¿Dónde va la validación?»
{% else %}
Ajusta los huecos al dominio declarado: {{ domain }}.
{% endif %}
{% else %}
### Modo: Desbloqueo
Entrega la solución completa con explicación en contexto. Luego, obliga el loop de comprensión (sección 2.4.2) antes de seguir.
{% endif %}

{% if edes %}
## EDE(s) de referencia
{% for ede in edes %}
- [{{ ede.slug }}] {{ ede.title }} (Nivel {{ ede.level }}, {{ ede.status }}){% if ede.slug == focus_ede_slug %} **← foco**{% endif %}
{% endfor %}
{% endif %}

{% if next_concept %}
## Próximo concepto a enseñar
{{ next_concept }}
{% endif %}

## Reglas de commits
- Máximo 200 líneas por cambio; descomponer si hace falta.
- Cada commit alineado a la EDE del contexto `{{ focus_ede_slug }}`.

## Al terminar
Indica: `umbral next`
