# Pipeline — Scripts e Notebooks

Mapa completo dos scripts standalone, seus artefatos, e a relação com os notebooks Quarto. Todos os scripts requerem o pacote instalado (`pip install -e .`).

## Visão geral

```
scripts/
├── Transcrição
│   └── transcribe_media.py          → chamado pelo CLI (prepare transcribe)
│
├── Sentiment Analysis
│   ├── sentiment_twitter_roberta.py → chamado pelo CLI (process sentiment --model roberta)
│   ├── sentiment_distilbert.py      → chamado pelo CLI (process sentiment --model distilbert)
│   ├── sentiment_deberta.py         → chamado pelo CLI (process sentiment --model deberta)
│   └── sentiment_ensemble.py        → chamado pelo CLI (process sentiment --model ensemble)
│
├── Embeddings
│   ├── generate_embeddings.py       → chamado pelo CLI (process embeddings --model mpnet)
│   ├── generate_embeddings_minilm.py → chamado pelo CLI (process embeddings --model minilm)
│   └── generate_embeddings_distiluse.py → chamado pelo CLI (process embeddings --model distiluse)
│
├── Comparação de Modelos
│   ├── compare_embeddings_models.py → gera JSON consumido por 04i-embeddings-comparison.qmd
│   └── compare_embedding_dimensions.py → análise de redução de dimensionalidade
│
├── Visualização
│   └── generate_timeline_chart.py  → gera assets/images/timeline-ultimate.png
│
└── Dados
    └── generate_sample_data.py      → gera dataset sintético em data/raw/sample/
```

## Relação scripts → notebooks

| Script | Notebook que consome | O que produz |
|--------|---------------------|--------------|
| `sentiment_twitter_roberta.py` | `04a-sentiment-roberta.qmd` | Colunas `sentimento_roberta_*` no parquet |
| `sentiment_distilbert.py` | `04b-sentiment-distilbert.qmd` | Colunas `sentimento_distilbert_*` no parquet |
| `sentiment_deberta.py` | `04c-sentiment-deberta.qmd` | Colunas `sentimento_deberta_*` no parquet |
| `sentiment_ensemble.py` | `04e-sentiment-ensemble.qmd` | Colunas `sentimento_ensemble_*` no parquet |
| `generate_embeddings.py` | `04f-embeddings-mpnet.qmd` | `message_embeddings_mpnet.npy` |
| `generate_embeddings_minilm.py` | `04g-embeddings-minilm.qmd` | `message_embeddings_minilm.npy` |
| `generate_embeddings_distiluse.py` | `04h-embeddings-distiluse.qmd` | `message_embeddings_distiluse.npy` |
| `compare_embeddings_models.py` | `04i-embeddings-comparison.qmd` | `embeddings_comparison.json` |
| `transcribe_media.py` | `02-data-wrangling.qmd` | `transcriptions.csv` |
| `generate_timeline_chart.py` | `index.qmd` (imagem estática) | `assets/images/timeline-ultimate.png` |

> **Nota:** Em abril/2026, 3 pares de notebooks foram consolidados: `03-contexto-externo` (ex 02.2 + 03), `04-feature-engineering` (ex 03-FE + 05-FE), `05-eda-overview` (ex 04-eda + 05-eda). Os EDAs dimensionais foram renumerados de 04.x para 05.x. Originais em `notebooks/archive/`.

Os scripts de comparação (`compare_*`) são executados manualmente — não fazem parte do CLI. Os notebooks leem os artefatos que eles geram.

## Detalhes por script

### transcribe_media.py

Transcreve arquivos de áudio e vídeo do WhatsApp usando a API Groq Whisper.

```bash
python scripts/transcribe_media.py
# ou via CLI:
whatsapp-interaction prepare transcribe
```

**Requisitos:** `pip install groq`

**Configuração no `.env`:**
```properties
GROQ_API_KEY=sua_chave_aqui
```

**Comportamento:**
1. Primeira execução: processa todos os arquivos (~40 min para ~700 arquivos)
2. Interrupção: salva progresso a cada 10 arquivos em `transcriptions_progress.csv`
3. Retomada: continua de onde parou automaticamente
4. Completo: gera `transcriptions.csv` e deleta arquivo de progresso

### Scripts de Sentiment

Cada script aplica um modelo de sentiment analysis ao `messages_with_models.parquet`:

| Script | Modelo | Característica |
|--------|--------|---------------|
| `sentiment_twitter_roberta.py` | Twitter-XLM-RoBERTa | Equilibrado |
| `sentiment_distilbert.py` | DistilBERT | Polarizador |
| `sentiment_deberta.py` | RoBERTa Latest | Ultra conservador |
| `sentiment_ensemble.py` | Combinação dos 3 | Majority voting + weighted tiebreak |

**Requisitos:** `pip install torch transformers`

O ensemble deve ser executado após os 3 modelos individuais.

### Scripts de Embeddings

Cada script gera embeddings semânticos das mensagens:

| Script | Modelo | Dimensões |
|--------|--------|-----------|
| `generate_embeddings.py` | all-mpnet-base-v2 | 768 |
| `generate_embeddings_minilm.py` | all-MiniLM-L6-v2 | 384 |
| `generate_embeddings_distiluse.py` | distiluse-base-multilingual-cased-v2 | 512 |

**Requisitos:** `pip install sentence-transformers torch`

### Scripts de Comparação

| Script | O que faz | Output |
|--------|-----------|--------|
| `compare_embeddings_models.py` | Compara qualidade dos 3 modelos (similaridade, clustering, correlação) | `embeddings_comparison.json` |
| `compare_embedding_dimensions.py` | Testa redução de dimensionalidade via PCA (768 → 384/256/128) | `embeddings_dimensionality_comparison.json` |

Executados manualmente após gerar os embeddings. O notebook `04i-embeddings-comparison.qmd` lê os JSONs de saída.

### generate_sample_data.py

Gera dataset sintético de 200 mensagens para demo e testes.

```bash
python scripts/generate_sample_data.py
```

Output: `data/raw/sample/raw-data.txt` (seed=42, determinístico)
