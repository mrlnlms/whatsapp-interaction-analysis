"""Helpers compartilhados do CLI."""

import os
import sys
import typer
from rich.console import Console
from pathlib import Path

console = Console()

# Garante que src/ está no path
_src_dir = str(Path(__file__).parent.parent / "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)


def load_config():
    """
    Carrega configuração do projeto.
    Retorna (PATHS, PROJECT_ROOT) ou None se falhar.
    """
    try:
        from config import PATHS, PROJECT_ROOT
        return PATHS, PROJECT_ROOT
    except EnvironmentError as e:
        console.print(f"[red]Erro de configuração:[/red] {e}")
        return None


def require_config():
    """
    Carrega config ou aborta com mensagem clara.
    Uso: PATHS, PROJECT_ROOT = require_config()
    """
    result = load_config()
    if result is None:
        raise typer.Exit(1)
    return result


def require_file(path: Path, description: str, hint: str = ""):
    """Valida que um arquivo existe ou aborta com mensagem."""
    if not path.exists():
        console.print(f"[red]Arquivo não encontrado:[/red] {description}")
        console.print(f"  Path: {path}")
        if hint:
            console.print(f"  [yellow]Dica:[/yellow] {hint}")
        raise typer.Exit(1)


def validate_steps(steps_str: str, valid_steps: list) -> list:
    """
    Valida e parseia string de steps separados por vírgula.
    Retorna lista de steps válidos ou aborta.
    """
    if not steps_str:
        return valid_steps

    requested = [s.strip() for s in steps_str.split(",")]
    invalid = [s for s in requested if s not in valid_steps]

    if invalid:
        console.print(f"[red]Etapas inválidas:[/red] {', '.join(invalid)}")
        console.print(f"[yellow]Etapas disponíveis:[/yellow] {', '.join(valid_steps)}")
        raise typer.Exit(1)

    return requested
