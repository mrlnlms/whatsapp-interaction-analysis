"""CLI whatsapp-interaction — pipeline de análise de conversas WhatsApp."""

import time
import os
import typer
from rich.console import Console

console = Console()

app = typer.Typer(
    name="whatsapp-interaction",
    help="Pipeline de análise de conversas WhatsApp.",
    no_args_is_help=True,
)

# Registra grupos
from cli.prepare import prepare_app
from cli.process import process_app
from cli._status import run_status

app.add_typer(prepare_app)
app.add_typer(process_app)


@app.command()
def status():
    """Mostra o estado atual dos dados processados."""
    run_status()


@app.command()
def run(
    skip_transcribe: bool = typer.Option(False, "--skip-transcribe", help="Pular transcrição."),
    skip_process: bool = typer.Option(False, "--skip-process", help="Pular sentiment/embeddings."),
):
    """Pipeline completo: prepare + process."""
    from cli.helpers import require_config
    from cli.prepare import _run_clean, _run_wrangle, _run_transcribe
    from cli.process import _load_and_run_script, SENTIMENT_SCRIPTS, EMBEDDINGS_SCRIPTS

    PATHS, _ = require_config()
    start = time.time()

    # Prepare
    console.print("\n[bold]═══ PREPARAÇÃO ═══[/bold]")
    console.print("\n[bold blue]Limpeza[/bold blue]")
    _run_clean(PATHS, steps=None)

    console.print("\n[bold blue]Wrangling[/bold blue]")
    _run_wrangle(PATHS, steps=None)

    if not skip_transcribe and os.getenv("GROQ_API_KEY"):
        console.print("\n[bold blue]Transcrição[/bold blue]")
        _run_transcribe(PATHS)
    elif not skip_transcribe:
        console.print("\n[yellow]Transcrição pulada (GROQ_API_KEY não encontrada)[/yellow]")

    # Process
    if not skip_process:
        console.print("\n[bold]═══ PROCESSAMENTO ═══[/bold]")

        console.print("\n[bold blue]Sentiment (ensemble)[/bold blue]")
        _load_and_run_script(SENTIMENT_SCRIPTS["ensemble"])

        console.print("\n[bold blue]Embeddings (mpnet)[/bold blue]")
        _load_and_run_script(EMBEDDINGS_SCRIPTS["mpnet"])

    elapsed = time.time() - start
    console.print(f"\n[bold green]Pipeline concluído em {elapsed:.1f}s[/bold green]")
