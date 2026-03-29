"""Comando status — mostra estado dos dados processados."""

from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()


def run_status():
    """Mostra o estado atual dos dados processados."""
    from whatsapp.cli.helpers import load_config

    result = load_config()
    if result is None:
        console.print("[yellow]Sem .env configurado. Mostrando paths relativos.[/yellow]\n")
        base = Path.cwd()
        interim = base / "data" / "interim"
        processed = base / "data" / "processed"
    else:
        PATHS, _ = result
        interim = PATHS["interim"]
        processed = PATHS["processed"]

    table = Table(title="Status do Pipeline")
    table.add_column("Etapa", style="bold")
    table.add_column("Status")
    table.add_column("Detalhes")

    # Cleaning
    cln_files = sorted(interim.glob("raw-data_cln*.txt")) if interim.exists() else []
    if cln_files:
        table.add_row("Cleaning", f"[green]{len(cln_files)}/7 etapas[/green]", cln_files[-1].name)
    else:
        table.add_row("Cleaning", "[red]Não executado[/red]", "")

    # Wrangling
    parquet = processed / "messages.parquet"
    csv = processed / "messages.csv"
    if parquet.exists():
        size_mb = parquet.stat().st_size / (1024 * 1024)
        table.add_row("Wrangling", "[green]Completo[/green]", f"messages.parquet ({size_mb:.1f} MB)")
    elif csv.exists():
        table.add_row("Wrangling", "[green]Completo[/green]", "messages.csv")
    else:
        table.add_row("Wrangling", "[red]Não executado[/red]", "")

    # Transcrição
    transcriptions = processed / "transcriptions.csv"
    if transcriptions.exists():
        table.add_row("Transcrição", "[green]Encontrado[/green]", "transcriptions.csv")
    else:
        table.add_row("Transcrição", "[yellow]Não encontrado[/yellow]", "")

    # Sentiment
    sentiment_models = []
    for name in ["roberta", "distilbert", "deberta", "ensemble"]:
        meta = processed / f"sentiment_{name}_metadata.json"
        if meta.exists():
            sentiment_models.append(name)
    if sentiment_models:
        table.add_row("Sentiment", f"[green]{len(sentiment_models)} modelo(s)[/green]", ", ".join(sentiment_models))
    else:
        table.add_row("Sentiment", "[yellow]Não executado[/yellow]", "")

    # Embeddings
    embedding_models = []
    for name, file in [("mpnet", "message_embeddings_mpnet.npy"), ("minilm", "message_embeddings_minilm.npy"), ("distiluse", "message_embeddings_distiluse.npy")]:
        if (processed / file).exists():
            embedding_models.append(name)
    if embedding_models:
        table.add_row("Embeddings", f"[green]{len(embedding_models)} modelo(s)[/green]", ", ".join(embedding_models))
    else:
        table.add_row("Embeddings", "[yellow]Não executado[/yellow]", "")

    console.print(table)
