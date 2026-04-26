# Umbral CLI

**Framework de desarrollo con comprensión sostenible.**

Umbral es un CLI en Python que orquesta contexto para agentes de IA. No genera código: deposita prompts contextualizados y valida artefactos.

## Stack

- Python 3.11+
- Typer · Pydantic · Rich · Questionary · Jinja2
- uv como gestor de paquetes

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/umbral-cli.git
cd umbral-cli

# Instalar con uv
uv sync
```

## Uso

```bash
# Verificar la instalación
uv run umbral version
```

## Desarrollo

```bash
# Instalar dependencias de desarrollo
uv sync --group dev

# Ejecutar tests
uv run pytest
```

## Licencia

MIT
