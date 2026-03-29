"""
Gerador de dados sintéticos de chat WhatsApp.

Cria um arquivo de exportação fake no formato WhatsApp para uso como
dataset de demonstração. Permite que qualquer pessoa clone o repo e
rode o pipeline sem dados pessoais reais.

Uso:
    python scripts/generate_sample_data.py

Saída:
    data/raw/sample/raw-data.txt
    data/raw/sample/media/          (diretório vazio)
    data/processed/sample/transcriptions.csv
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

SEED = 42
NUM_MESSAGES = 200
START_DATE = datetime(2025, 1, 20, 8, 0, 0)  # Segunda-feira
END_DATE = datetime(2025, 1, 26, 23, 59, 0)  # Domingo

PARTICIPANTS = ["Marlon", "Lê 🖤"]

# Caractere invisível inserido pelo WhatsApp na exportação
U200E = "\u200e"

# =============================================================================
# BANCOS DE CONTEÚDO (PT-BR, casual, genérico)
# =============================================================================

TEXT_PURE = [
    "Bom dia",
    "Boa noite",
    "Oi",
    "Tudo bem?",
    "Tudo certo",
    "Beleza",
    "Ok",
    "Sim",
    "Não",
    "Pode ser",
    "Vou ver",
    "Depois falo",
    "To chegando",
    "Já saí",
    "Cheguei",
    "Vou almoçar",
    "Já almocei",
    "To no trabalho",
    "Saí do trabalho",
    "Vou dormir",
    "Boa noite, descansa",
    "Amanhã a gente vê",
    "Tranquilo",
    "Perfeito",
    "Entendi",
    "Combinado",
    "Faz sentido",
    "Vou pensar",
    "Acho que sim",
    "Acho que não",
    "Depende",
    "Talvez",
    "Verdade",
    "Com certeza",
    "Exato",
    "Isso mesmo",
    "Não sei ainda",
    "Deixa eu ver",
    "Calma",
    "Relaxa",
    "Tá bom",
    "Blz",
    "Opa",
    "Eae",
    "Fala",
    "Diz",
    "Pode falar",
    "To aqui",
    "Voltei",
    "Vou sair daqui a pouco",
    "Que horas vc sai?",
    "Vai demorar?",
    "Quanto tempo mais ou menos?",
    "To no caminho",
    "Chego em 20 min",
    "Acabei de acordar",
    "Nem vi a hora passar",
    "Que dia corrido",
    "Hoje foi puxado",
    "Amanhã vai ser melhor",
    "Espero que sim",
    "Vamos ver",
    "Vc tá onde?",
    "Em casa",
    "No mercado",
    "Na padaria",
    "Vc quer alguma coisa?",
    "Não precisa",
    "Obrigado",
    "De nada",
    "Valeu",
    "Tô cansado",
    "Eu também",
    "Que frio hoje",
    "Tá calor demais",
    "Choveu o dia todo",
    "Parece que vai chover",
    "Já passou a chuva?",
    "Ainda tá chovendo",
    "Que sol forte",
    "Acabou a luz aqui",
    "Voltou a luz",
    "Net caiu",
    "Agora voltou",
    "Pior que é",
    "Nem me fale",
    "Sério?",
    "Jura?",
    "Nossa",
    "Caramba",
    "Que loucura",
    "Pois é",
    "Enfim",
    "Bom",
    "Então tá",
    "Fechou",
    "Feito",
    "Pronto",
    "Mandei",
    "Recebi",
    "Vi agora",
    "Vou ver depois",
    "Agora não dá",
    "Mais tarde falo",
    "Lembra de comprar café",
    "Preciso ir no banco amanhã",
    "Vc viu a conta de luz?",
    "Chegou correspondência",
    "Paguei o boleto",
    "Reservei a mesa pro jantar",
    "Confirmaram a entrega pra amanhã",
    "O carro tá na oficina",
    "Busco às 18h",
    "Pode ser mais tarde?",
    "Só consigo depois das 19h",
    "Então fica pra sexta",
    "Sexta tá ótimo",
    "A gente resolve amanhã",
    "Sem pressa",
    "Quando puder",
    "Fico te devendo essa",
    "Imagina",
    "Que nada",
]

TEXT_EMOJI = [
    "Bom dia ☀️",
    "Boa noite 🌙",
    "😂😂😂",
    "Que fofo 🥰",
    "Tô rindo muito 😂",
    "❤️",
    "👍",
    "Saudade 💜",
    "Parabéns 🎉",
    "Que lindo 😍",
    "Tô com fome 🍕",
    "Finalmente 🙏",
    "Não acredito 😱",
    "Calor demais 🥵",
    "Tô morrendo de sono 😴",
    "Vamos 🚀",
    "Que delícia 😋",
    "Obrigado 🙏",
    "Show 🤙",
    "Top 💯",
]

TEXT_LINKS = [
    "Olha isso: https://example.com/receita-bolo-chocolate",
    "Vi esse vídeo https://example.com/watch?v=abc123",
    "Achei esse artigo interessante https://example.com/artigo-sobre-cafe",
    "https://example.com/mapa-rota",
    "Vê esse restaurante https://example.com/restaurante-italiano",
    "O evento é esse aqui https://example.com/evento-cultural",
    "Tá com desconto https://example.com/promo-livros",
    "Olha o cardápio https://example.com/menu-sushi",
    "Link do voo https://example.com/voo-sp-bsb",
    "Esse filme parece bom https://example.com/filme-novo-2025",
]

MULTILINE_MESSAGES = [
    "Então, sobre o jantar de sexta:\n- Reservei no italiano\n- Mesa pra 20h",
    "Lista do mercado:\n- Café\n- Leite\n- Pão\n- Queijo",
    "Resumo do dia:\nReunião de manhã foi bem\nAlmocei fora\nTarde tranquila",
    "Opções pro fim de semana:\n1. Cinema\n2. Parque\n3. Ficar em casa",
    "Sobre o trabalho:\nHoje foi corrido mas produtivo\nAmanhã deve ser mais tranquilo",
    "Vou precisar de:\nDocumento do carro\nComprovante de endereço\nRG",
]

DELETED_MSG = "This message was deleted"
EDITED_SUFFIX = " <This message was edited>"

CALL_MESSAGES = [
    "Voice call, 2 min 15 sec",
    "Missed voice call",
    "Voice call, 45 sec",
    "Missed voice call",
]

# Contadores para nomes de arquivos de mídia
_media_counters = {
    "AUD": 0,
    "IMG": 0,
    "VID": 0,
    "STK": 0,
    "DOC": 0,
    "GIF": 0,
}


def _media_filename(prefix: str, date: datetime, ext: str) -> str:
    """Gera nome de arquivo de mídia no padrão WhatsApp."""
    _media_counters[prefix] += 1
    date_str = date.strftime("%Y%m%d")
    return f"{prefix}-{date_str}-WA{_media_counters[prefix]:04d}.{ext}"


# =============================================================================
# DISTRIBUIÇÃO TEMPORAL
# =============================================================================


def generate_timestamps(n: int, start: datetime, end: datetime, rng: random.Random) -> list:
    """
    Gera timestamps com distribuição realista ao longo do dia.

    Pesos por faixa horária:
    - 0-6h:   peso 1  (madrugada, poucas mensagens)
    - 7-11h:  peso 3  (manhã)
    - 12-14h: peso 4  (almoço)
    - 15-17h: peso 3  (tarde)
    - 18-23h: peso 8  (noite, pico)
    """
    hour_weights = {}
    for h in range(0, 7):
        hour_weights[h] = 1
    for h in range(7, 12):
        hour_weights[h] = 3
    for h in range(12, 15):
        hour_weights[h] = 4
    for h in range(15, 18):
        hour_weights[h] = 3
    for h in range(18, 24):
        hour_weights[h] = 8

    total_days = (end - start).days + 1
    timestamps = []

    for _ in range(n):
        # Escolhe dia
        day_offset = rng.randint(0, total_days - 1)
        day = start + timedelta(days=day_offset)

        # Escolhe hora com peso
        hours = list(range(24))
        weights = [hour_weights[h] for h in hours]
        hour = rng.choices(hours, weights=weights, k=1)[0]

        minute = rng.randint(0, 59)
        second = rng.randint(0, 59)

        ts = day.replace(hour=hour, minute=minute, second=second)
        timestamps.append(ts)

    timestamps.sort()
    return timestamps


# =============================================================================
# GERADOR PRINCIPAL
# =============================================================================


def generate_messages(rng: random.Random) -> list:
    """
    Gera lista de mensagens no formato (timestamp, sender, content).

    Distribuição de tipos:
    - 60% text_pure
    - 10% text_emoji
    -  5% text_links
    -  8% audio omitted
    -  5% image omitted/attached
    -  3% video omitted
    -  2% sticker omitted
    -  2% deleted
    -  2% voice call
    -  1% edited
    -  1% document omitted
    -  1% GIF omitted
    """
    timestamps = generate_timestamps(NUM_MESSAGES, START_DATE, END_DATE, rng)
    messages = []

    # Tipos com pesos (total = 100)
    types = [
        ("text_pure", 60),
        ("text_emoji", 10),
        ("text_link", 5),
        ("audio", 8),
        ("image", 5),
        ("video", 3),
        ("sticker", 2),
        ("deleted", 2),
        ("call", 2),
        ("edited", 1),
        ("document", 1),
        ("gif", 1),
    ]
    type_names = [t[0] for t in types]
    type_weights = [t[1] for t in types]

    # Pré-sorteia todos os tipos
    assigned_types = rng.choices(type_names, weights=type_weights, k=NUM_MESSAGES)

    # Intercalar participantes com leve tendência de "blocos" de conversa
    current_sender = rng.choice(PARTICIPANTS)
    for i, (ts, msg_type) in enumerate(zip(timestamps, assigned_types)):
        # 30% chance de trocar de sender (simula turnos de conversa)
        if rng.random() < 0.30:
            current_sender = PARTICIPANTS[0] if current_sender == PARTICIPANTS[1] else PARTICIPANTS[1]

        sender = current_sender
        content = _generate_content(msg_type, ts, rng)

        messages.append((ts, sender, content))

    return messages


def _generate_content(msg_type: str, ts: datetime, rng: random.Random) -> str:
    """Gera conteúdo de mensagem baseado no tipo."""
    if msg_type == "text_pure":
        # Alguns viram multiline
        if rng.random() < 0.05:
            return rng.choice(MULTILINE_MESSAGES)
        return rng.choice(TEXT_PURE)

    elif msg_type == "text_emoji":
        return rng.choice(TEXT_EMOJI)

    elif msg_type == "text_link":
        return rng.choice(TEXT_LINKS)

    elif msg_type == "audio":
        return "audio omitted"

    elif msg_type == "image":
        fname = _media_filename("IMG", ts, "jpg")
        if rng.random() < 0.5:
            return "image omitted"
        return f"<attached: {fname}>"

    elif msg_type == "video":
        return "video omitted"

    elif msg_type == "sticker":
        return "sticker omitted"

    elif msg_type == "deleted":
        return DELETED_MSG

    elif msg_type == "call":
        return rng.choice(CALL_MESSAGES)

    elif msg_type == "edited":
        base = rng.choice(TEXT_PURE[:20])
        return base + EDITED_SUFFIX

    elif msg_type == "document":
        return "document omitted"

    elif msg_type == "gif":
        return "GIF omitted"

    return rng.choice(TEXT_PURE)


# =============================================================================
# FORMATAÇÃO PARA ARQUIVO DE EXPORTAÇÃO
# =============================================================================


def format_whatsapp_line(ts: datetime, sender: str, content: str, rng: random.Random) -> str:
    """
    Formata uma mensagem no formato de exportação do WhatsApp.

    Formato: [DD/MM/YY, HH:MM:SS] Sender: content
    Com ~50% de chance de ter U+200E no início.
    """
    date_str = ts.strftime("%d/%m/%y")
    time_str = ts.strftime("%H:%M:%S")

    prefix = U200E if rng.random() < 0.5 else ""

    # Mensagens multiline: as linhas de continuação não têm timestamp
    lines = content.split("\n")
    first_line = f"{prefix}[{date_str}, {time_str}] {sender}: {lines[0]}"

    if len(lines) > 1:
        result = first_line + "\n"
        for continuation in lines[1:]:
            # Linhas de continuação com indentação (como no WhatsApp real)
            cont_prefix = U200E if rng.random() < 0.3 else ""
            result += f"{cont_prefix}    {continuation}\n"
        return result.rstrip("\n")

    return first_line


def generate_raw_file(messages: list, rng: random.Random) -> str:
    """
    Gera o conteúdo completo do arquivo raw-data.txt.

    Adiciona linhas vazias ocasionais entre mensagens (como no export real).
    """
    output_lines = []

    for i, (ts, sender, content) in enumerate(messages):
        line = format_whatsapp_line(ts, sender, content, rng)
        output_lines.append(line)

        # ~10% chance de linha vazia entre mensagens
        if rng.random() < 0.10:
            output_lines.append("")

    return "\n".join(output_lines) + "\n"


# =============================================================================
# TRANSCRIÇÕES FAKE
# =============================================================================

FAKE_TRANSCRIPTIONS = [
    "Oi tudo bem? Acabei de chegar",
    "Vou sair daqui a pouco, te aviso quando tiver saindo",
    "Então, sobre aquele assunto que a gente conversou ontem, acho que a melhor opção é esperar",
    "Bom dia, tô indo pro trabalho agora",
    "Esqueci de falar, amanhã não vou poder ir",
    "Tá bom, combinado então, a gente se fala depois",
    "Comprei aquelas coisas que você pediu, tô voltando pra casa",
    "Acabou a reunião, foi bem, depois te conto os detalhes",
]


def generate_transcriptions(messages: list) -> list:
    """
    Gera transcrições fake para mensagens de áudio.

    Retorna lista de dicts compatível com transcriptions.csv.
    """
    audio_messages = [
        (ts, sender, content)
        for ts, sender, content in messages
        if content == "audio omitted"
    ]

    transcriptions = []
    for i, (ts, sender, content) in enumerate(audio_messages):
        date_str = ts.strftime("%Y%m%d")
        filename = f"AUD-{date_str}-WA{i + 1:04d}.opus"
        file_path = f"data/raw/sample/media/{filename}"

        transcription_text = FAKE_TRANSCRIPTIONS[i % len(FAKE_TRANSCRIPTIONS)]

        transcriptions.append({
            "file_path": file_path,
            "transcription": transcription_text,
            "transcription_status": "completed",
            "is_synthetic": "False",
        })

    return transcriptions


# =============================================================================
# MAIN
# =============================================================================


def main():
    project_root = Path(__file__).resolve().parent.parent

    # Diretórios de saída
    raw_dir = project_root / "data" / "raw" / "sample"
    media_dir = raw_dir / "media"
    processed_dir = project_root / "data" / "processed" / "sample"

    raw_dir.mkdir(parents=True, exist_ok=True)
    media_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Geração determinística
    rng = random.Random(SEED)

    print(f"Gerando {NUM_MESSAGES} mensagens sintéticas...")
    messages = generate_messages(rng)

    # raw-data.txt
    raw_content = generate_raw_file(messages, rng)
    raw_file = raw_dir / "raw-data.txt"
    raw_file.write_text(raw_content, encoding="utf-8")
    print(f"  -> {raw_file.relative_to(project_root)} ({len(raw_content)} bytes)")

    # transcriptions.csv
    transcriptions = generate_transcriptions(messages)
    csv_file = processed_dir / "transcriptions.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["file_path", "transcription", "transcription_status", "is_synthetic"]
        )
        writer.writeheader()
        writer.writerows(transcriptions)
    print(f"  -> {csv_file.relative_to(project_root)} ({len(transcriptions)} transcrições)")

    # Resumo
    type_counts = {}
    for ts, sender, content in messages:
        if content == "audio omitted":
            t = "audio"
        elif content == "video omitted":
            t = "video"
        elif content == "sticker omitted":
            t = "sticker"
        elif content == "document omitted":
            t = "document"
        elif content == "GIF omitted":
            t = "gif"
        elif content == "image omitted" or content.startswith("<attached:"):
            t = "image"
        elif content == DELETED_MSG:
            t = "deleted"
        elif content.startswith("Voice call") or content.startswith("Missed voice"):
            t = "call"
        elif EDITED_SUFFIX in content:
            t = "edited"
        elif "https://" in content:
            t = "link"
        elif any(
            c in content
            for c in ["😂", "🥰", "❤️", "👍", "💜", "🎉", "😍", "🍕", "🙏", "😱", "🥵", "😴", "🚀", "😋", "🤙", "💯", "☀️", "🌙"]
        ):
            t = "emoji"
        else:
            t = "text"
        type_counts[t] = type_counts.get(t, 0) + 1

    print(f"\nDistribuição de tipos:")
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {t:>10}: {c:>3} ({c / NUM_MESSAGES * 100:.0f}%)")

    print(f"\nDiretório media/ criado (vazio): {media_dir.relative_to(project_root)}")
    print("Geração concluída com sucesso.")


if __name__ == "__main__":
    main()
