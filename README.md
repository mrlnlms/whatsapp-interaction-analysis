# WhatsApp Interaction Analysis

> End-to-end data science pipeline for WhatsApp conversation analysis — profiling, cleaning, sentiment analysis, embeddings, clustering.

## About

Pipeline completo de Data Science para analise de conversas do WhatsApp. O caso de estudo e um export com ~92.000 mensagens ao longo de 1 ano.

O projeto foi desenvolvido para ser **reprodutivel** — permite rodar o pipeline com novos exports e integrar os resultados a base existente.

## Pipeline

![](./assets/images/ds-pipeline-to-insight.png)

| Fase | Etapa | Descricao |
|------|-------|-----------|
| **Preparation** | Data Discovery | Exploracao inicial do arquivo bruto |
| | Data Profiling | Investigacao sistematica de padroes |
| | Data Cleaning | Remocao de caracteres invisiveis, normalizacao |
| | Data Wrangling | Parsing, vinculacao de midia, transcricao |
| | Feature Engineering | Criacao de 35+ variaveis derivadas |
| | Model Features | Sentiment analysis multi-modelo, embeddings |
| **Analysis** | EDA | Analise exploratoria por dimensao (temporal, interacao, conteudo) |
| | Advanced Analysis | Clustering semantico, PCA, MCA, N-Grams, TF-IDF |

## Structure

```
whatsapp-interaction-analysis/
│
├── index.qmd                         # Documento principal (overview)
├── .env.example                       # Template de configuracao
├── requirements.txt                   # Dependencias Python
├── _quarto.yml                        # Config Quarto principal
│
├── src/                               # Modulos Python
│   ├── config.py                      # Configuracoes (le do .env)
│   ├── profiling.py                   # Funcoes de investigacao
│   ├── cleaning.py                    # Pipeline de limpeza (7 etapas)
│   ├── wrangling.py                   # Pipeline de wrangling (6 etapas)
│   ├── features.py                    # Feature engineering
│   └── utils/
│       ├── audit.py                   # Sistema de auditoria
│       ├── dataframe_helpers.py       # Helpers para DataFrames
│       ├── file_helpers.py            # Helpers para arquivos
│       └── text_helpers.py            # Helpers para texto
│
├── scripts/                           # Scripts standalone
│   ├── transcribe_media.py            # Transcricao via Groq/Whisper
│   ├── sentiment_*.py                 # Sentiment analysis (RoBERTa, DistilBERT, DeBERTa, ensemble)
│   ├── generate_embeddings*.py        # Geracao de embeddings (mpnet, minilm, distiluse)
│   ├── compare_embeddings_models.py   # Comparacao entre modelos de embeddings
│   ├── migrate_sentiment_columns.py   # Migracao de colunas de sentimento
│   └── remove_alias_columns.py        # Limpeza de colunas alias
│
├── notebooks/                         # Documentos Quarto (ver tabela abaixo)
│
├── data/                              # Nao versionado (dados pessoais)
│   ├── raw/                           # Exports brutos por periodo
│   ├── interim/                       # Arquivos intermediarios
│   ├── processed/                     # DataFrames por execucao
│   ├── external/                      # Dados de contexto externo
│   └── integrated/                    # Base consolidada
│
├── docs/
│   ├── SETUP-GUIDE.md                 # Guia de instalacao
│   ├── INCREMENTAL-GUIDE.md           # Guia para novos exports
│   └── data-dictionary.md             # Dicionario de dados
│
└── analysis/                          # Nao versionado (outputs)
```

## Notebooks

### Preparation

| # | Notebook | Descricao |
|---|---------|-----------|
| 00 | [Data Discovery](notebooks/00-data-discovery.qmd) | Exploracao inicial do arquivo |
| 00 | [Data Profiling](notebooks/00-data-profiling.qmd) | Investigacao sistematica |
| 01 | [Data Cleaning](notebooks/01-data-cleaning.qmd) | Limpeza e normalizacao |
| 02 | [Data Wrangling](notebooks/02-data-wrangling.qmd) | Parsing, midia, transcricao |
| 03 | [Feature Engineering](notebooks/03-feature-engineering.qmd) | Criacao de 35+ variaveis |

### Model Features (opcional)

| # | Notebook | Descricao |
|---|---------|-----------|
| 04 | [Model Features](notebooks/04-model-features.qmd) | Overview das features de ML |
| 04a | [Sentiment — RoBERTa](notebooks/04a-sentiment-roberta.qmd) | Twitter-RoBERTa sentiment |
| 04b | [Sentiment — DistilBERT](notebooks/04b-sentiment-distilbert.qmd) | DistilBERT sentiment |
| 04c | [Sentiment — DeBERTa](notebooks/04c-sentiment-deberta.qmd) | DeBERTa sentiment |
| 04d | [Sentiment — Comparison](notebooks/04d-sentiment-comparison.qmd) | Comparacao entre modelos |
| 04e | [Sentiment — Ensemble](notebooks/04e-sentiment-ensemble.qmd) | Ensemble dos 3 modelos |
| 04f | [Embeddings — mpnet](notebooks/04f-embeddings-mpnet.qmd) | all-mpnet-base-v2 |
| 04g | [Embeddings — MiniLM](notebooks/04g-embeddings-minilm.qmd) | all-MiniLM-L6-v2 |
| 04h | [Embeddings — DistilUSE](notebooks/04h-embeddings-distiluse.qmd) | distiluse-base-multilingual |
| 04i | [Embeddings — Comparison](notebooks/04i-embeddings-comparison.qmd) | Comparacao entre modelos |

### Analysis

| # | Notebook | Descricao |
|---|---------|-----------|
| 02.1 | [EDA — Data Wrangling](notebooks/02.1-EDA-data-wrangling.qmd) | EDA pos-wrangling |
| 02.2 | [Contexto Externo](notebooks/02.2-adicionar-contexto-externo.qmd) | Integracao de dados externos |
| 02.3 | [EDA — Conteudo e Interacao](notebooks/02.3-EDA-conteudo-interacao.qmd) | Analise de conteudo |
| 03 | [Contexto Externo](notebooks/03-contexto-externo.qmd) | Pipeline de contexto |
| 04 | [EDA — Overview](notebooks/04-eda-overview.qmd) | Visao geral da EDA |
| 04.1 | [EDA — Temporal](notebooks/04.1-eda-temporal.qmd) | Padroes temporais |
| 04.2 | [EDA — Interacao](notebooks/04.2-eda-interacao.qmd) | Dinamicas de interacao |
| 04.3 | [EDA — Conteudo](notebooks/04.3-eda-conteudo.qmd) | Analise de conteudo |
| 05 | [EDA](notebooks/05-eda.qmd) | Analise exploratoria geral |
| 05 | [Feature Engineering](notebooks/05-feature-engineering.qmd) | Feature engineering final |
| 06 | [Advanced Analysis](notebooks/06-advanced-analysis.qmd) | Clustering semantico, N-Grams, TF-IDF |

## Quick Start

```bash
git clone https://github.com/mrlnlms/whatsapp-interaction-analysis.git
cd whatsapp-interaction-analysis

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edite o .env com seus paths

quarto preview
```

Ver [Guia de Setup](docs/SETUP-GUIDE.md) completo.

### Transcricao de audios (opcional)

```bash
# Adicione sua API key no .env
echo "GROQ_API_KEY=sua_chave_aqui" >> .env

# Execute o script de transcricao (~40 min para ~700 arquivos)
python scripts/transcribe_media.py

# Re-rode o wrangling
quarto render notebooks/02-data-wrangling.qmd
```

O script detecta automaticamente arquivos ja transcritos e continua de onde parou.

## Tech Stack

**Core**: Python 3.11+, Quarto

**Data**: Pandas, NumPy, PyArrow

**Visualization**: Matplotlib, Seaborn, Plotly, WordCloud

**ML/Statistics**: Scikit-learn, Prince (MCA), SciPy

**NLP**: Transformers/PyTorch (sentiment — RoBERTa, DistilBERT, DeBERTa), Sentence-Transformers (embeddings — mpnet, MiniLM, DistilUSE), Groq API/Whisper (transcricao)

## Outputs

O pipeline gera os seguintes arquivos em `data/processed/{export}/`:

| Arquivo | Colunas | Descricao |
|---------|---------|-----------|
| `messages.csv` | 8 | Dataset principal para analise |
| `messages.parquet` | 8 | Mesmo conteudo, ~3x menor |
| `messages_full.csv` | 17 | Versao completa para debug |
| `chat_complete.txt` | — | Chat com transcricoes |
| `corpus_*.txt` | — | Textos para NLP |

## Documentation

- [Guia de Setup](docs/SETUP-GUIDE.md) — Instalacao e configuracao
- [Guia Incremental](docs/INCREMENTAL-GUIDE.md) — Como rodar com novos exports
- [Dicionario de Dados](docs/data-dictionary.md) — Descricao das variaveis
- [Scripts](scripts/README.md) — Documentacao dos scripts utilitarios

## Privacy

Os dados (`data/` e `analysis/`) nao sao versionados por conterem informacoes pessoais.

---

*Desenvolvido por [@mrlnlms](https://github.com/mrlnlms)*
