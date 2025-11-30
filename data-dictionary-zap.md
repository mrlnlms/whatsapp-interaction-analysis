# Dicionário de Dados

Documentação das variáveis do dataset em cada etapa do pipeline.

---

## Informações Gerais

| Métrica | Valor |
|---------|-------|
| **Total de registros** | ~92.000 mensagens |
| **Período** | Out/2024 — Nov/2025 |
| **Participantes** | 2 (anonimizados como P1, P2) |

---

## 1. Dataset Base (Wrangling)

Colunas geradas pelo `02-data-wrangling.qmd`.

**Arquivo:** `data/processed/{DATA_FOLDER}/messages.csv` (ou `.parquet`)

### Versão Completa (17 colunas)

Arquivo: `messages_full.csv` — Para debug e auditoria.

| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `linha_original` | int | Número da linha no TXT original | `12345` |
| `data` | string | Data DD/MM/YY | `15/01/25` |
| `hora` | string | Hora HH:MM:SS | `14:30:22` |
| `timestamp` | datetime | Data e hora combinadas | `2025-01-15 14:30:22` |
| `remetente` | string | Identificador do participante | `P1`, `P2` |
| `conteudo` | string | Texto original da mensagem | `Oi, tudo bem?` |
| `tipo_mensagem` | string | Classificação da mensagem | Ver tabela abaixo |
| `arquivo` | string | Nome do arquivo de mídia | `00001-AUDIO-2025-01-15.opus` |
| `arquivo_existe` | bool | Arquivo físico existe? | `True`, `False` |
| `extensao` | string | Extensão do arquivo | `.opus`, `.mp4`, `.jpg` |
| `tipo_arquivo` | string | Tipo extraído do nome | `AUDIO`, `VIDEO`, `PHOTO` |
| `arquivo_path` | string | Caminho completo do arquivo | `/path/to/media/file.opus` |
| `tem_transcricao` | bool | Possui transcrição? | `True`, `False` |
| `transcricao` | string | Texto transcrito (se houver) | `Oi amor, tudo bem?` |
| `transcription_status` | string | Status da transcrição | `completed`, `error`, `pending` |
| `is_synthetic` | bool | Transcrição órfã? | `True`, `False` |
| `conteudo_enriquecido` | string | Conteúdo final (com transcrições) | Ver nota abaixo |

### Versão Core (8 colunas)

Arquivo: `messages.csv` / `messages.parquet` — **Use este para análises.**

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `timestamp` | datetime | Data e hora da mensagem |
| `remetente` | string | P1 ou P2 |
| `tipo_mensagem` | string | Classificação da mensagem |
| `conteudo_enriquecido` | string | Texto final (com transcrições) |
| `arquivo` | string | Nome do arquivo (se mídia) |
| `tem_transcricao` | bool | Possui transcrição? |
| `transcricao` | string | Texto transcrito |
| `is_synthetic` | bool | Transcrição órfã? |

---

### Tipos de Mensagem (`tipo_mensagem`)

| Categoria | Valores | Descrição |
|-----------|---------|-----------|
| **Texto** | `text_pure` | Texto sem emoji nem link |
| | `text_with_emoji` | Texto com emoji |
| | `text_with_link` | Texto com URL |
| **Mídia Omitida** | `audio_omitted` | Áudio não anexado no export |
| | `image_omitted` | Imagem não anexada |
| | `video_omitted` | Vídeo não anexado |
| | `video_note_omitted` | Nota de vídeo não anexada |
| | `sticker_omitted` | Sticker não anexado |
| | `gif_omitted` | GIF não anexado |
| | `document_omitted` | Documento não anexado |
| **Mídia Anexada** | `audio_attached` | Áudio presente no export |
| | `image_attached` | Imagem presente |
| | `video_attached` | Vídeo presente |
| | `sticker_attached` | Sticker presente |
| | `contact_attached` | Contato compartilhado |
| **Sistema** | `message_deleted` | Mensagem apagada |
| | `message_edited` | Mensagem editada |
| | `voice_call` | Chamada de voz |
| | `missed_call` | Chamada perdida |
| | `system_message` | Mensagem do sistema |

---

### Conteúdo Enriquecido (`conteudo_enriquecido`)

Para mensagens de mídia com transcrição, o formato é:

```
[AUDIO TRANSCRITO] Texto da transcrição aqui
[Arquivo: 00001-AUDIO-2025-01-15.opus]
```

Para transcrições órfãs (arquivo sem mensagem correspondente):

```
[AUDIO TRANSCRITO - ÓRFÃO] Texto da transcrição
[Arquivo: 00001-AUDIO-2025-01-15.opus]
```

---

## 2. Features Derivadas (Feature Engineering)

Colunas a serem geradas pelo `03-feature-engineering.qmd`.

> ⏳ **Status:** Estrutura definida, implementação pendente.

### Features Temporais

| Coluna | Tipo | Descrição | Critério |
|--------|------|-----------|----------|
| `ano` | int | Ano | Extraído de `timestamp` |
| `mes` | int | Mês (1-12) | Extraído de `timestamp` |
| `dia` | int | Dia do mês | Extraído de `timestamp` |
| `hora` | int | Hora (0-23) | Extraído de `timestamp` |
| `dia_semana` | int | Dia da semana (0=seg, 6=dom) | `timestamp.dayofweek` |
| `fim_de_semana` | bool | É sábado ou domingo? | `dia_semana >= 5` |
| `periodo_dia` | string | Período do dia | Madrugada/Manhã/Tarde/Noite |

### Features de Texto

| Coluna | Tipo | Descrição | Critério |
|--------|------|-----------|----------|
| `tamanho_caracteres` | int | Total de caracteres | `len(conteudo)` |
| `tamanho_palavras` | int | Total de palavras | `len(conteudo.split())` |
| `tem_emoji` | bool | Contém emoji? | `ord(char) > 0x1F600` |
| `qtd_emojis` | int | Quantidade de emojis | Contagem |
| `tem_link` | bool | Contém URL? | Regex `https?://` |

### Features de Conversação

| Coluna | Tipo | Descrição | Critério |
|--------|------|-----------|----------|
| `tempo_desde_ultima` | float | Segundos desde msg anterior | `timestamp.diff()` |
| `eh_inicio_conversa` | bool | Gap > 2 horas? | `tempo_desde_ultima > 7200` |
| `sequencia_mesmo_remetente` | int | Msgs seguidas do mesmo | Contador |

### Features de Sentimento

| Coluna | Tipo | Descrição | Critério |
|--------|------|-----------|----------|
| `sentimento` | string | Label do sentimento | BERT multilingual |
| `message_hash` | string | Hash único da msg | MD5 para cache |

> 💡 **Cache:** Sentimentos são cacheados em `sentiment_cache.csv` para evitar reprocessamento.

---

## 3. Features Contextuais (Futuro)

Colunas que dependem de dados externos (ex: datas de viagens).

> 🔮 **Status:** Planejado para implementação futura.

| Coluna | Tipo | Descrição | Fonte |
|--------|------|-----------|-------|
| `contexto_relacional` | string | Período do relacionamento | Planilha de datas |
| `is_juntos` | bool | Casal junto fisicamente? | Planilha de viagens |
| `viagem` | string | Nome da viagem (se aplicável) | Planilha de viagens |

---

## Arquivos de Corpus

Arquivos TXT para análises de NLP.

| Arquivo | Descrição |
|---------|-----------|
| `chat_complete.txt` | Todas mensagens com timestamp e remetente |
| `chat_p1.txt` | Só mensagens de P1 |
| `chat_p2.txt` | Só mensagens de P2 |
| `corpus_full.txt` | Só conteúdo (sem metadados) |
| `corpus_p1.txt` | Só conteúdo de P1 |
| `corpus_p2.txt` | Só conteúdo de P2 |

---

## Notas

### Correlações Esperadas

Features que podem ser redundantes dependendo da análise:

- `tamanho_caracteres` ↔ `tamanho_palavras`
- `tempo_desde_ultima` em segundos vs horas

### Cache de Processamentos Custosos

| Processo | Arquivo de Cache | Chave |
|----------|------------------|-------|
| Transcrição | `transcriptions.csv` | `filename` |
| Sentimento | `sentiment_cache.csv` | `message_hash` |

Ver [INCREMENTAL-GUIDE.md](./INCREMENTAL-GUIDE.md) para detalhes.

---

*Última atualização: Novembro 2025*



---

> #############################
> 
> B A C K U P
> 
> #############################


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
