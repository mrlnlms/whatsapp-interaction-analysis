"""Comandos de preparação: clean, wrangle, transcribe."""

import time
import typer
from typing import Optional
from rich.console import Console

console = Console()

prepare_app = typer.Typer(
    name="prepare",
    help="Preparação de dados: limpeza, parsing, transcrição.",
    invoke_without_command=True,
)


@prepare_app.callback()
def prepare_all(ctx: typer.Context):
    """Roda pipeline completo: clean → wrangle → transcribe (se API key existir)."""
    if ctx.invoked_subcommand is not None:
        return

    from whatsapp.cli.helpers import require_config
    PATHS, _ = require_config()

    start = time.time()

    console.print("\n[bold blue]1/3 — Limpeza[/bold blue]")
    _run_clean(PATHS, steps=None)

    console.print("\n[bold blue]2/3 — Wrangling[/bold blue]")
    _run_wrangle(PATHS, steps=None)

    import os
    if os.getenv("GROQ_API_KEY"):
        console.print("\n[bold blue]3/3 — Transcrição[/bold blue]")
        _run_transcribe(PATHS)
    else:
        console.print("\n[yellow]3/3 — Transcrição pulada (GROQ_API_KEY não encontrada)[/yellow]")

    elapsed = time.time() - start
    console.print(f"\n[bold green]Preparação concluída em {elapsed:.1f}s[/bold green]")


@prepare_app.command()
def clean(
    steps: Optional[str] = typer.Option(
        None, "--steps", "-s",
        help="Etapas separadas por vírgula. Default: todas."
    ),
):
    """Pipeline de limpeza (7 etapas)."""
    from whatsapp.cli.helpers import require_config
    PATHS, _ = require_config()
    _run_clean(PATHS, steps)


@prepare_app.command()
def wrangle(
    steps: Optional[str] = typer.Option(
        None, "--steps", "-s",
        help="Etapas separadas por vírgula. Default: todas."
    ),
):
    """Parsing, classificação, mídia, transcrição, enriquecimento, export."""
    from whatsapp.cli.helpers import require_config
    PATHS, _ = require_config()
    _run_wrangle(PATHS, steps)


@prepare_app.command()
def transcribe():
    """Transcrição de áudios/vídeos via Groq/Whisper."""
    from whatsapp.cli.helpers import require_config
    PATHS, _ = require_config()
    _run_transcribe(PATHS)


def _run_clean(PATHS: dict, steps: Optional[str]):
    """Executa pipeline de limpeza."""
    from whatsapp.cli.helpers import require_file, validate_steps
    from whatsapp.pipeline.cleaning import run_pipeline, CLEANING_STEPS

    default_order = [
        "u200e", "anonymize", "timestamps", "indentation",
        "empty_lines", "whitespace", "empty_timestamps"
    ]
    order = validate_steps(steps or "", default_order)

    raw_file = PATHS["raw"]
    require_file(raw_file, "Arquivo raw do WhatsApp", "Coloque o export em data/raw/{DATA_FOLDER}/raw-data.txt")

    result = run_pipeline(order=order, raw_file=raw_file, output_dir=PATHS["interim"])
    console.print(f"[green]Limpeza concluída:[/green] redução de {result['totals']['total_percent']:.1f}%")


def _run_wrangle(PATHS: dict, steps: Optional[str]):
    """Executa pipeline de wrangling."""
    from whatsapp.cli.helpers import require_file, validate_steps

    default_order = ["parse", "classify", "media", "transcriptions", "enrich", "export"]
    order = validate_steps(steps or "", default_order)

    input_file = PATHS["interim"] / "raw-data_cln7.txt"
    require_file(input_file, "Arquivo limpo (cln7)", "Rode primeiro: whatsapp-interaction prepare clean")

    from whatsapp.pipeline.wrangling import run_wrangling_pipeline

    result = run_wrangling_pipeline(
        order=order,
        input_file=input_file,
        output_dir=PATHS["processed"],
        media_dir=PATHS["media"],
        transcription_file=PATHS["processed"] / "transcriptions.csv",
    )
    console.print(f"[green]Wrangling concluído:[/green] {len(result['df'])} mensagens processadas")


def _run_transcribe(PATHS: dict):
    """Executa transcrição de mídia."""
    import os
    import importlib.util

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        console.print("[red]GROQ_API_KEY não encontrada no .env[/red]")
        console.print("[yellow]Adicione: GROQ_API_KEY=sua_chave_aqui ao arquivo .env[/yellow]")
        raise typer.Exit(1)

    from whatsapp.cli.helpers import require_config
    _, PROJECT_ROOT = require_config()

    script_path = PROJECT_ROOT / "scripts" / "transcribe_media.py"
    spec = importlib.util.spec_from_file_location("transcribe_media", script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.main()

    console.print("[green]Transcrição concluída[/green]")
