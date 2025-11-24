# Dicionário de Dados

Documentação completa de todas as variáveis do dataset final.

---

## Informações Gerais

| Métrica | Valor |
|---------|-------|
| **Total de registros** | ~92.000 mensagens |
| **Total de features** | 35 colunas |
| **Período** | Out/2024 — Out/2025 |
| **Participantes** | 2 (anonimizados como P1, P2) |

---

## Colunas Base (estruturais)

| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `timestamp` | datetime | Data e hora da mensagem | `2025-01-15 14:30:22` |
| `remetente` | string | Identificador do participante | `P1`, `P2` |
| `tipo_midia` | string | Tipo de conteúdo da mensagem | `text`, `audio`, `video`, `image`, `sticker` |
| `status_midia` | string | Status do arquivo de mídia | `-`, `omitted`, `attached`, `transcribed` |
| `conteudo` | string | Texto da mensagem (ou transcrição) | `Oi, tudo bem?` |
| `arquivo_midia` | string | Nome do arquivo anexado (se houver) | `00001-AUDIO-2025-01-15.opus` |
| `linha_original` | int | Número da linha no arquivo raw | `12345` |
| `data` | string | Data no formato DD/MM/YY | `15/01/25` |
| `hora` | string | Hora no formato HH:MM:SS | `14:30:22` |

---

## Features de Conteúdo

| Coluna | Tipo | Descrição | Critério |
|--------|------|-----------|----------|
| `has_link` | bool | Contém URL? | Regex: `https?://` |
| `has_emoji` | bool | Contém emoji? | `ord(char) > 127` |
| `word_count` | int | Contagem de palavras | `len(text.split())` |

---

## Features Temporais

| Coluna | Tipo | Descrição | Valores possíveis |
|--------|------|-----------|-------------------|
| `dia_semana` | string | Nome do dia | Segunda, Terça, ..., Domingo |
| `periodo_dia` | string | Período do dia | Madrugada (0-6h), Manhã (6-12h), Tarde (12-18h), Noite (18-24h) |
| `mes` | string | Nome do mês | Janeiro, ..., Dezembro |
| `ano` | int | Ano | 2024, 2025 |
| `is_weekend` | bool | É fim de semana? | Sábado ou Domingo |
| `hora_numerica` | int | Hora (0-23) | 0, 1, ..., 23 |

---

## Métricas de Texto

| Coluna | Tipo | Descrição | Critério |
|--------|------|-----------|----------|
| `char_count` | int | Total de caracteres | `len(conteudo)` |
| `avg_word_length` | float | Média de chars por palavra | `sum(len(word)) / len(words)` |
| `has_question` | bool | Contém pergunta? | Presença de `?` |
| `has_exclamation` | bool | Contém exclamação? | Presença de `!` |
| `is_all_caps` | bool | Texto todo em maiúsculas? | `text.isupper()` (mín. 3 letras) |
| `line_breaks` | int | Quebras de linha | Contagem de `\n` |

---

## Padrões Conversacionais

| Coluna | Tipo | Descrição | Critério |
|--------|------|-----------|----------|
| `tempo_resposta_segundos` | float | Tempo desde msg anterior | `timestamp.diff().total_seconds()` |
| `is_first_of_day` | bool | Primeira msg do dia? | Data diferente da msg anterior |
| `msgs_seguidas` | int | Msgs consecutivas do mesmo remetente | Contador resetado quando remetente muda |
| `is_reply_quick` | bool | Resposta rápida? | **< 300 segundos (5 minutos)** |
| `gap_horas` | float | Gap em horas | `tempo_resposta_segundos / 3600` |
| `is_conversation_start` | bool | Início de nova conversa? | **gap > 2 horas OU is_first_of_day** |

---

## Features Derivadas

| Coluna | Tipo | Descrição | Critério |
|--------|------|-----------|----------|
| `msg_size_category` | string | Categoria de tamanho | Vazia (0), Curta (1-10), Média (11-30), Longa (31-100), Muito Longa (100+) |

---

## Features de Sentimento (a documentar)

| Coluna | Tipo | Descrição | Critério |
|--------|------|-----------|----------|
| `sentiment_score` | float | Score de sentimento | Range: -2 a 2. **⚠️ Modelo/lib não documentado** |
| `sentiment_label` | string | Label de sentimento | 1 star, 2 stars, ..., 5 stars. **⚠️ Critério não documentado** |

---

## Features Contextuais (a documentar)

| Coluna | Tipo | Descrição | Critério |
|--------|------|-----------|----------|
| `contexto_relacional` | string | Contexto do período | rotina, pre_viagem, pos_viagem, juntos. **⚠️ Critério não documentado** |
| `is_juntos` | bool | Casal estava junto fisicamente? | **⚠️ Base de datas externa não documentada** |

---

## Notas

### Features que precisam revisão

1. **`sentiment_score` e `sentiment_label`**: Documentar qual modelo/biblioteca foi usado e o critério de classificação.

2. **`contexto_relacional`**: Documentar como os períodos foram definidos (datas de viagens?).

3. **`is_juntos`**: Documentar a base de datas externa usada para cruzamento.

### Correlações conhecidas

As seguintes features têm alta correlação e podem ser redundantes dependendo da análise:

- `char_count` ↔ `word_count` ↔ `avg_word_length`
- `tempo_resposta_segundos` ↔ `gap_horas`
- `is_first_of_day` ↔ `is_conversation_start` (parcial)

---

*Última atualização: Novembro 2025*
