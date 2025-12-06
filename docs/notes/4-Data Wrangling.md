# Data Wrangling

Parsing, classificação, mídia e enriquecimento


📁 Projeto: whatsapp-ds-analytics

## Data Wrangling

Com o arquivo limpo gerado no [Data Cleaning](http://localhost:7860/notebooks/01-data-cleaning.html), esta etapa transforma o TXT em um DataFrame estruturado, vincula arquivos de mídia, integra transcrições e exporta os dados enriquecidos.

## Objetivo

- ✅ Parsing: TXT → DataFrame
- ✅ Classificação: Identificar tipos de mensagem
- ✅ Mídia: Vincular arquivos físicos
- ✅ Transcrição: Integrar transcrições existentes
- ✅ Enriquecimento: Substituir mídias por transcrições
- ✅ Exportação: CSV + TXTs de corpus

---

## Configuração do Pipeline

| Entrada | `raw-data_cln7.txt` | ~/whatsapp-ds-analytics/data/interim/export\_2024-10\_2025-10 |
| --- | --- | --- |
| Saída | `export_2024-10_2025-10` | ~/whatsapp-ds-analytics/data/processed/export\_2024-10\_2025-10 |
| Mídia | `media` | ~/whatsapp-ds-analytics/data/raw/export\_2024-10\_2025-10/media |
| Transcrições | `transcriptions.csv` | ~/whatsapp-ds-analytics/data/processed/export\_2024-10\_2025-10 |

---

## Execução do Pipeline

| 1 | Parse | 91,924 mensagens |
| --- | --- | --- |
| 2 | Classificação | 21 tipos identificados |
| 3 | Mídia | 1,254 arquivos vinculados |
| 4 | Transcrições | 695 transcrições integradas |
| 4.1 | Enriquecimento | 695 mensagens enriquecidas |
| 5 | Exportação | 3 arquivos gerados |

```
✅ Pipeline concluído com sucesso!
```

---

## Pipeline de Transformação

### Etapa 1: Parsing

Converte TXT em DataFrame, agregando mensagens multilinha.

| Mensagens parseadas | 91,924 |
| --- | --- |
| Linhas no TXT | 96,138 |
| Razão linhas/mensagem | 1.05 |

### Etapa 2: Classificação

Classifica cada mensagem por tipo (21 tipos possíveis) e agrupa em categorias.

| `text_pure` | `TEXT` | 62,885 | 68.4% |
| --- | --- | --- | --- |
| `video_note_omitted` | `VID` | 9,168 | 10.0% |
| `audio_omitted` | `AUDIO` | 8,040 | 8.7% |
| `text_with_emoji` | `TEXT` | 3,858 | 4.2% |
| `image_omitted` | `IMG` | 3,287 | 3.6% |
| `sticker_omitted` | `STICKER` | 1,869 | 2.0% |
| `message_edited` | `SYSTEM` | 658 | 0.7% |
| `text_with_link` | `TEXT` | 554 | 0.6% |
| `audio_attached` | `AUDIO` | 512 | 0.6% |
| `image_attached` | `IMG` | 298 | 0.3% |
| `video_omitted` | `VID` | 248 | 0.3% |
| `sticker_attached` | `STICKER` | 248 | 0.3% |
| `video_attached` | `VID` | 186 | 0.2% |
| `document_omitted` | `DOC` | 38 | 0.0% |
| `gif_omitted` | `GIF` | 28 | 0.0% |
| `message_deleted` | `SYSTEM` | 22 | 0.0% |
| `missed_call` | `CALL` | 11 | 0.0% |
| `contact_attached` | `CONTACT` | 9 | 0.0% |
| `system_message` | `SYSTEM` | 2 | 0.0% |
| `voice_call` | `CALL` | 2 | 0.0% |
| `file_attached` | `FILE` | 1 | 0.0% |

| `TEXT` | 67,297 | 73.2% | text\_pure, text\_with\_emoji, text\_with\_link |
| --- | --- | --- | --- |
| `VID` | 9,602 | 10.4% | video\_attached, video\_note\_omitted, video\_omitted |
| `AUDIO` | 8,552 | 9.3% | audio\_attached, audio\_omitted |
| `IMG` | 3,585 | 3.9% | image\_attached, image\_omitted |
| `STICKER` | 2,117 | 2.3% | sticker\_attached, sticker\_omitted |
| `SYSTEM` | 682 | 0.7% | message\_deleted, message\_edited, system\_message |
| `DOC` | 38 | 0.0% | document\_omitted |
| `GIF` | 28 | 0.0% | gif\_omitted |
| `CALL` | 13 | 0.0% | missed\_call, voice\_call |
| `CONTACT` | 9 | 0.0% | contact\_attached |
| `FILE` | 1 | 0.0% | file\_attached |

### Etapa 3: Mídia

Vincula arquivos físicos de mídia ao DataFrame, criando metadados (`arquivo_existe`, `arquivo_path`) que serão usados nas etapas seguintes para merge com transcrições.

| `AUDIO` | 512 | 512 |
| --- | --- | --- |
| `VID` | 186 | 186 |
| `IMG` | 298 | 298 |
| `STICKER` | 248 | 248 |
| `GIF` | 0 | 0 |
| `DOC` | 0 | 0 |
| `FILE` | 1 | 1 |
| `CONTACT` | 9 | 8 |
| `TEXT` | — | — |
| `SYSTEM` | — | — |
| `CALL` | — | — |

*Esta etapa prepara o DataFrame para receber transcrições (Etapa 4) que serão vinculadas pelo nome do arquivo.*

### Etapa 4: Transcrições

Integra transcrições de áudio/vídeo (geradas pelo script `transcribe_media.py`) ao DataFrame através de merge pela coluna `arquivo`.

| Arquivos no CSV | 695 |
| --- | --- |
| Transcrições OK | 694 |
| ↳ Áudios | 510 |
| ↳ Vídeos | 184 |

```
✅ Carregado de: transcriptions.csv
```

*Transcrições são vinculadas às mensagens pelo nome do arquivo (`arquivo` column).*

### Etapa 4.1: Enriquecimento de Conteúdo

Substitui tags de mídia (`<attached: arquivo>`) pelo texto da transcrição na coluna `conteudo`.

| Mensagens de texto originais | 67,297 |
| --- | --- |
| Áudios/vídeos transcritos | 695 |
| \*\*Total de mensagens textuais\*\* | \*\*67,992\*\* |
| \*\*Aumento de conteúdo\*\* | \*\*+1.0%\*\* |

| Caracteres em texto original | 1,673,199 |
| --- | --- |
| Caracteres em transcrições | 155,078 |
| \*\*Total de caracteres\*\* | \*\*1,828,277\*\* |

**Exemplo de transformação:**

|  |
| --- |
|  |
|  |

*Formato original no arquivo TXT exportado do WhatsApp (antes do wrangling).*

| Ai, puta que pariu Parece que eu sim consigo sentir seu pau na minha buceta, sabia? Apertar seu pau assim Bem gostoso Te... |
| --- |
| Não é que a gente está conversando agora, na verdade minha ideia nem era conversar agora, mas aí o papo fluiu para isso.... |
| Ah, tá tudo certo. Tá tudo certo. Estamos... Estamos alinhados. Acho que eu vou enrolar brigadeiro agora. |

*Conteúdo após substituição pela transcrição via API Groq Whisper.*

*Mensagens sem transcrição (ex: `image omitted`) permanecem inalteradas.*

### Etapa 5: Exportação

Exporta datasets em múltiplos formatos (CSV, Parquet, TXT).

#### 📦 Arquivos Gerados

**Datasets estruturados:**

| `messages` | CSV\_CORE | 6.64 MB | 91,924 | 8 | Alternativa ao Parquet |
| --- | --- | --- | --- | --- | --- |
| `messages` | PARQUET | 2.15 MB | 91,924 | 8 | Recomendado (tipos otimizados) |

**Colunas do dataset (8):**

| `timestamp` | datetime | Data e hora da mensagem |
| --- | --- | --- |
| `remetente` | category | Participante (P1 ou P2) |
| `tipo_mensagem` | category | Tipo específico - 21 possíveis (text\_pure, audio\_omitted, video\_attached, etc.) |
| `grupo_mensagem` | category | Categoria agrupada: TEXT, AUDIO, VID, IMG, STICKER, GIF, DOC, CONTACT, FILE, SYSTEM, CALL |
| `conteudo` | text | Conteúdo enriquecido: transcrição (se mídia transcrita) ou texto original. Renomeado de conteudo\_enriquecido |
| `arquivo` | text | Nome do arquivo de mídia anexado (ex: 00001-AUDIO-2024-10-21.opus), se aplicável |
| `transcricao` | bool | Indica se a mensagem possui transcrição de áudio/vídeo. O texto da transcrição fica em conteudo. Renomeado de tem\_transcricao |
| `date_match` | bool | Indica se é mensagem órfã/sintética (transcrição sem match de timestamp). Renomeado de is\_synthetic |

**Como usar:**

```python
# Recomendado: Parquet (rápido, tipos corretos)
df = pd.read_parquet('data/processed/messages.parquet')

# Alternativa: CSV
df = pd.read_csv('data/processed/messages.csv')
```

**Exemplos de filtros:**

```python
# Apenas mensagens de texto
df_text = df[df['grupo_mensagem'] == 'TEXT']

# Mensagens com transcrição
df_transcribed = df[df['transcricao'] == True]

# Mensagens de P1 no mês de outubro
df_p1_oct = df[(df['remetente'] == 'P1') & (df['timestamp'].dt.month == 10)]
```

**Arquivos de texto puro para análises de linguagem natural:**

| `chat_complete.txt` | 3.95 MB | 96,138 | Chat completo. Formato: DD/MM/YY HH:MM:SS Remetente: Conteúdo |
| --- | --- | --- | --- |
| `corpus_full.txt` | 2.02 MB | 96,138 | Corpus completo (apenas texto). Word clouds, vocabulário. |
| `chat_p1.txt` | 2.03 MB | 49,058 | Chat de P1 com timestamps. Análise temporal. |
| `chat_p2.txt` | 1.92 MB | 47,080 | Chat de P2 com timestamps. Análise temporal. |
| `corpus_p1.txt` | 1.05 MB | 49,058 | Corpus de P1 (apenas texto). Comparação de estilos. |
| `corpus_p2.txt` | 0.98 MB | 47,080 | Corpus de P2 (apenas texto). Comparação de estilos. |

**Como usar:**

```python
# Corpus completo (apenas texto, sem metadados)
with open('data/processed/corpus_full.txt', 'r', encoding='utf-8') as f:
    texto = f.read()

# Análise de vocabulário
palavras = texto.split()
vocab_size = len(set(palavras))
```

**Por participante:**

```python
# Corpus de P1 (apenas texto)
with open('data/processed/corpus_p1.txt', 'r', encoding='utf-8') as f:
    texto_p1 = f.read()

# Corpus de P2 (apenas texto)
with open('data/processed/corpus_p2.txt', 'r', encoding='utf-8') as f:
    texto_p2 = f.read()
```

**Chat com timestamps:**

```python
# Lê chat completo
with open('data/processed/chat_complete.txt', 'r', encoding='utf-8') as f:
    chat_lines = f.readlines()

# Parsing manual (se necessário)
import re
pattern = r'^(\d{2}/\d{2}/\d{2}) (\d{2}:\d{2}:\d{2}) (.+?): (.*)$'
for line in chat_lines:
    match = re.match(pattern, line)
    if match:
        data, hora, remetente, conteudo = match.groups()
```

**Arquivo completo:**

| `messages_full.csv` | 12.21 MB | 91,924 | 17 | Todas as colunas (debug) |
| --- | --- | --- | --- | --- |

**Colunas extras (debug):**

| `linha_original` | Referência ao TXT original |
| --- | --- |
| `data` | Redundante (já tem timestamp) |
| `hora` | Redundante (já tem timestamp) |
| `conteudo` | Conteúdo original (antes do enriquecimento) |
| `arquivo_existe` | Bool de verificação |
| `extensao` | Derivável de 'arquivo' |
| `tipo_arquivo` | Derivável de 'arquivo' |
| `arquivo_path` | Path completo do arquivo |
| `transcricao` | Redundante - já tem coluna transcricao (bool) no dataset principal |
| `transcription_status` | Status da API de transcrição (completed/error) |

**Exportação manual (opcional):**

```python
# Re-exportar só texto (sem tags de mídia)
from wrangling import export_corpus_files

df_text = df[df['grupo_mensagem'] == 'TEXT']
export_corpus_files(df_text, OUTPUT_DIR / 'text_only', use_enriched=False)
```

```python
# Exportar CSV com colunas específicas
from wrangling import export_to_csv

cols = ['timestamp', 'remetente', 'conteudo', 'tipo_mensagem']
export_to_csv(df, OUTPUT_DIR / 'messages_minimal.csv', columns=cols)
```

**Pode deletar após verificação:** - `messages_full.csv` (só precisa se for debugar pipeline)

**Arquivo de input:**

| `transcriptions.csv` | CSV | 0.23 MB | 695 | Transcrições de áudio/vídeo (input da Etapa 4) |
| --- | --- | --- | --- | --- |

**Sobre este arquivo:**

Gerado por `scripts/transcribe_media.py`, contém:

- Nome do arquivo de áudio/vídeo
- Transcrição do conteúdo
- Status da API (success/error)
- Timestamp de processamento

**Como regenerar:**

```bash
python scripts/transcribe_media.py
```

*Nota: Requer configuração da API Groq no arquivo `.env`*

---

## Próximos Passos

1. [**Feature Engineering**](http://localhost:7860/notebooks/03-feature-engineering.html) — Criação de variáveis derivadas