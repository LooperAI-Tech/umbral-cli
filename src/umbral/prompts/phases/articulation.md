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
Spec Co-Creada en .umbral/phases/spec-{{ project_name }}.md con:
- Casos borde (al menos 2 específicos)
- Modos de falla (con consecuencia)
- Alcance (qué SÍ y qué NO)
- Datos de entrada identificados

## Gate de salida:
El usuario puede explicar todos los casos borde sin tu ayuda.
Si no puede, reformula y profundiza.

## Cuando termines:
Indica al usuario: `umbral next`
