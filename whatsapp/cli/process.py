"""Comandos de processamento: sentiment, embeddings."""

import time
import typer
from enum import Enum
from rich.console import Console
import importlib.util

console = Console()


class SentimentModel(str, Enum):
    distilbert = "distilbert"
    deberta = "deberta"
    roberta = "roberta"
    ensemble = "ensemble"


class EmbeddingsModel(str, Enum):
    mpnet = "mpnet"
    minilm = "minilm"
    distiluse = "distiluse"


SENTIMENT_SCRIPTS = {
    "distilbert": "sentiment_distilbert.py",
    "deberta": "sentiment_deberta.py",
    "roberta": "sentiment_twitter_roberta.py",
    "ensemble": "sentiment_ensemble.py",
}

EMBEDDINGS_SCRIPTS = {
    "mpnet": "generate_embeddings.py",
    "minilm": "generate_embeddings_minilm.py",
    "distiluse": "generate_embeddings_distiluse.py",
}


process_app = typer.Typer(
    name="process",
    help="Processamento ML: sentiment analysis, embeddings.",
    invoke_without_command=True,
)


def _load_and_run_script(script_name: str):
    """Importa um script de scripts/ e chama main()."""
    from whatsapp.cli.helpers import require_config
    _, PROJECT_ROOT = require_config()

    script_path = PROJECT_ROOT / "scripts" / script_name
    if not script_path.exists():
        console.print(f"[red]Script não encontrado:[/red] {script_path}")
        raise typer.Exit(1)

    spec = importlib.util.spec_from_file_location(script_path.stem, script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.main()


def _require_processed_data():
    """Valida que messages.parquet existe."""
    from whatsapp.cli.helpers import require_config, require_file
    PATHS, _ = require_config()
    parquet = PATHS["processed"] / "messages.parquet"
    require_file(parquet, "Dados processados (messages.parquet)", "Rode primeiro: whatsapp-interaction prepare")
    return PATHS


@process_app.callback()
def process_all(ctx: typer.Context):
    """Roda sentiment (ensemble) + embeddings (mpnet)."""
    if ctx.invoked_subcommand is not None:
        return

    _require_processed_data()
    start = time.time()

    console.print("\n[bold blue]1/2 — Sentiment analysis (ensemble)[/bold blue]")
    _load_and_run_script(SENTIMENT_SCRIPTS["ensemble"])

    console.print("\n[bold blue]2/2 — Embeddings (mpnet)[/bold blue]")
    _load_and_run_script(EMBEDDINGS_SCRIPTS["mpnet"])

    elapsed = time.time() - start
    console.print(f"\n[bold green]Processamento concluído em {elapsed:.1f}s[/bold green]")


@process_app.command()
def sentiment(
    model: SentimentModel = typer.Option(
        SentimentModel.ensemble, "--model", "-m",
        help="Modelo de sentiment analysis."
    ),
):
    """Análise de sentimento."""
    _require_processed_data()
    console.print(f"[bold blue]Sentiment analysis ({model.value})[/bold blue]")
    _load_and_run_script(SENTIMENT_SCRIPTS[model.value])
    console.print(f"[green]Sentiment ({model.value}) concluído[/green]")


@process_app.command()
def embeddings(
    model: EmbeddingsModel = typer.Option(
        EmbeddingsModel.mpnet, "--model", "-m",
        help="Modelo de embeddings."
    ),
):
    """Geração de embeddings semânticos."""
    _require_processed_data()
    console.print(f"[bold blue]Embeddings ({model.value})[/bold blue]")
    _load_and_run_script(EMBEDDINGS_SCRIPTS[model.value])
    console.print(f"[green]Embeddings ({model.value}) concluído[/green]")
