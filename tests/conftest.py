"""Fixtures compartilhadas para testes do pipeline WhatsApp."""

import os
import pytest
from pathlib import Path

# Define variaveis de ambiente para que whatsapp.pipeline.config carregue sem .env
os.environ.setdefault("PROJECT_ROOT", str(Path(__file__).parent.parent))
os.environ.setdefault("DATA_FOLDER", "sample")


@pytest.fixture
def tmp_file(tmp_path):
    """Cria um arquivo temporario com conteudo e retorna (input_path, output_path)."""
    def _create(content: str):
        input_file = tmp_path / "input.txt"
        output_file = tmp_path / "output.txt"
        input_file.write_text(content, encoding="utf-8")
        return input_file, output_file
    return _create


@pytest.fixture
def sample_chat_clean():
    """Chat limpo no formato pos-cleaning (sem colchetes, com segundos)."""
    return (
        "24/11/24 15:30:05 P1: Oi, tudo bem?\n"
        "24/11/24 15:30:10 P2: Tudo sim! E voce?\n"
        "24/11/24 15:31:00 P1: Bem tambem\n"
        "Continuacao da mensagem anterior\n"
        "24/11/24 15:32:00 P2: audio omitted\n"
        "24/11/24 15:33:00 P1: <attached: IMG-20241124-WA0001.jpg>\n"
        "24/11/24 15:34:00 P2: This message was deleted\n"
        "24/11/24 15:35:00 P1: Olha esse link https://example.com\n"
        "24/11/24 15:36:00 P2: Voice call\n"
    )
