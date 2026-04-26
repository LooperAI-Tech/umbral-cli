"""Tests para commands/init_cmd.py — modo no interactivo."""

import os

from typer.testing import CliRunner

from umbral.cli import app

runner = CliRunner()


def test_init_non_interactive(tmp_path):
    """Verifica init en modo no interactivo."""
    result = runner.invoke(
        app, ["init", "test-project", "--dir", str(tmp_path), "--yes"]
    )
    assert result.exit_code == 0
    assert (tmp_path / ".umbral").is_dir()
    assert (tmp_path / ".umbral" / "umbral.yaml").exists()
    assert (tmp_path / ".umbral" / "profile.yaml").exists()
    assert (tmp_path / ".umbral" / "edes").is_dir()
    assert (tmp_path / ".umbral" / "phases").is_dir()


def test_init_creates_adapter(tmp_path):
    """Verifica que init crea archivos de adapter."""
    result = runner.invoke(
        app, ["init", "test-project", "--dir", str(tmp_path), "--yes"]
    )
    assert result.exit_code == 0
    # Por defecto usa claude-code
    assert (tmp_path / ".claude" / "commands" / "umbral.md").exists()


def test_init_output_messages(tmp_path):
    """Verifica que init muestra los mensajes esperados."""
    result = runner.invoke(
        app, ["init", "test-project", "--dir", str(tmp_path), "--yes"]
    )
    assert "test-project" in result.output
    assert "umbral.yaml" in result.output
    assert "profile.yaml" in result.output or "Perfil" in result.output


def test_init_detects_api_key(tmp_path, monkeypatch):
    """Verifica que detecta ANTHROPIC_API_KEY en modo no interactivo."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-key")
    result = runner.invoke(
        app, ["init", "test-project", "--dir", str(tmp_path), "--yes"]
    )
    assert result.exit_code == 0
    # Con API key, judge mode debería ser online
    config_content = (tmp_path / ".umbral" / "umbral.yaml").read_text()
    assert "online" in config_content


def test_init_no_api_key_uses_offline(tmp_path, monkeypatch):
    """Verifica que sin API key usa modo offline."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    result = runner.invoke(
        app, ["init", "test-project", "--dir", str(tmp_path), "--yes"]
    )
    assert result.exit_code == 0
    config_content = (tmp_path / ".umbral" / "umbral.yaml").read_text()
    assert "offline" in config_content


def test_init_creates_named_subfolder_by_default(tmp_path, monkeypatch):
    """Sin --dir, crea <nombre> bajo el directorio actual."""
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init", "proyecto-test", "--yes"])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "proyecto-test" / ".umbral" / "umbral.yaml").is_file()
    assert "proyecto-test" in (tmp_path / "proyecto-test" / ".umbral" / "umbral.yaml").read_text(
        encoding="utf-8"
    )


def test_init_dir_dot_uses_cwd_not_subfolder(tmp_path, monkeypatch):
    """Con -d . inicializa en el cwd sin subcarpeta por nombre."""
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init", "mi-app", "-d", ".", "--yes"])
    assert result.exit_code == 0, result.output
    assert (tmp_path / ".umbral" / "umbral.yaml").is_file()
    assert not (tmp_path / "mi-app").is_dir()
