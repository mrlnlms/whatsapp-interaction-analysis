# WhatsApp Interaction Analysis

> End-to-end data science pipeline for WhatsApp conversation analysis — profiling, cleaning, sentiment analysis, embeddings, clustering.

## About

Pipeline completo de Data Science para análise de conversas do WhatsApp. O caso de estudo é um export com ~92.000 mensagens ao longo de 1 ano.

O projeto foi desenvolvido para ser **reprodutível** — permite rodar o pipeline com novos exports e integrar os resultados à base existente.

## Pipeline

![](./assets/images/ds-pipeline-to-insight.png)

| Fase | Etapa | Descrição |
|------|-------|-----------|
| **Preparation** | Data Discovery | Exploração inicial do arquivo bruto |
| | Data Profiling | Investigação sistemática de padrões |
| | Data Cleaning | Remoção de caracteres invisíveis, normalização |
| | Data Wrangling | Parsing, vinculação de mídia, transcrição |
| | Feature Engineering | Criação de 35+ variáveis derivadas |
| | Model Features | Sentiment analysis multi-modelo, embeddings |
| **Analysis** | EDA | Análise exploratória por dimensão (temporal, interação, conteúdo) |
| | Advanced Analysis | Clustering semântico, PCA, MCA, N-Grams, TF-IDF |

## Structure

```
whatsapp-interaction-analysis/
│
├── index.qmd                         # Documento principal (overview)
├── .env.example                       # Template de configuração
├── requirements.txt                   # Dependências Python
├── _quarto.yml                        # Config Quarto principal
├── ROADMAP.md                         # Roadmap e próximos passos
│
├── whatsapp/                          # Pacote principal
│   ├── __init__.py                    # Versão e metadata
│   ├── __main__.py                    # python -m whatsapp
│   ├── cli/                           # CLI (whatsapp-interaction)
│   │   ├── __init__.py                # App Typer + comando run
│   │   ├── helpers.py                 # Helpers compartilhados
│   │   ├── prepare.py                 # Comandos: clean, wrangle, transcribe
│   │   ├── process.py                 # Comandos: sentiment, embeddings
│   │   └── _status.py                 # Comando: status
│   └── pipeline/                      # Módulos do pipeline
│       ├── config.py                  # Configurações (lê do .env)
│       ├── profiling.py               # Funções de investigação
│       ├── cleaning.py                # Pipeline de limpeza (7 etapas)
│       ├── wrangling.py               # Pipeline de wrangling (6 etapas)
│       └── utils/                     # Utilitários
│           ├── audit.py               # Sistema de auditoria
│           ├── dataframe_helpers.py   # Helpers para DataFrames
│           ├── file_helpers.py        # Helpers para arquivos
│           └── text_helpers.py        # Helpers para texto
│
├── scripts/                           # Scripts standalone
│   ├── transcribe_media.py            # Transcrição via Groq/Whisper
│   ├── sentiment_*.py                 # Sentiment analysis (RoBERTa, DistilBERT, DeBERTa, ensemble)
│   ├── generate_embeddings*.py        # Geração de embeddings (mpnet, minilm, distiluse)
│   ├── compare_embeddings_models.py   # Comparação entre modelos de embeddings
│   ├── migrate_sentiment_columns.py   # Migração de colunas de sentimento
│   └── remove_alias_columns.py        # Limpeza de colunas alias
│
├── notebooks/                         # Documentos Quarto (ver tabela abaixo)
│
├── tests/                             # Testes unitários (pytest)
│   ├── test_cleaning.py               # Testes do pipeline de limpeza
│   ├── test_wrangling.py              # Testes de parsing e classificação
│   └── test_cli.py                    # Testes do CLI
│
├── data/                              # Não versionado (dados pessoais)
│   ├── raw/                           # Exports brutos por período
│   ├── interim/                       # Arquivos intermediários
│   ├── processed/                     # DataFrames por execução
│   ├── external/                      # Dados de contexto externo
│   └── integrated/                    # Base consolidada
│
├── docs/
│   ├── SETUP-GUIDE.md                 # Guia de instalação
│   ├── INCREMENTAL-GUIDE.md           # Guia para novos exports
│   └── data-dictionary.md             # Dicionário de dados
│
├── .github/workflows/                 # CI/CD
│   └── tests.yml                      # Testes automáticos (Python 3.11/3.12)
│
└── analysis/                          # Não versionado (outputs)
```

## Notebooks

### Preparation

| # | Notebook | Descrição |
|---|---------|-----------|
| 00 | [Data Discovery](notebooks/00-data-discovery.qmd) | Exploração inicial do arquivo |
| 00 | [Data Profiling](notebooks/00-data-profiling.qmd) | Investigação sistemática |
| 01 | [Data Cleaning](notebooks/01-data-cleaning.qmd) | Limpeza e normalização |
| 02 | [Data Wrangling](notebooks/02-data-wrangling.qmd) | Parsing, mídia, transcrição |
| 03 | [Feature Engineering](notebooks/03-feature-engineering.qmd) | Criação de 35+ variáveis |

### Model Features (opcional)

| # | Notebook | Descrição |
|---|---------|-----------|
| 04 | [Model Features](notebooks/04-model-features.qmd) | Overview das features de ML |
| 04a | [Sentiment — RoBERTa](notebooks/04a-sentiment-roberta.qmd) | Twitter-RoBERTa sentiment |
| 04b | [Sentiment — DistilBERT](notebooks/04b-sentiment-distilbert.qmd) | DistilBERT sentiment |
| 04c | [Sentiment — DeBERTa](notebooks/04c-sentiment-deberta.qmd) | DeBERTa sentiment |
| 04d | [Sentiment — Comparison](notebooks/04d-sentiment-comparison.qmd) | Comparação entre modelos |
| 04e | [Sentiment — Ensemble](notebooks/04e-sentiment-ensemble.qmd) | Ensemble dos 3 modelos |
| 04f | [Embeddings — mpnet](notebooks/04f-embeddings-mpnet.qmd) | all-mpnet-base-v2 |
| 04g | [Embeddings — MiniLM](notebooks/04g-embeddings-minilm.qmd) | all-MiniLM-L6-v2 |
| 04h | [Embeddings — DistilUSE](notebooks/04h-embeddings-distiluse.qmd) | distiluse-base-multilingual |
| 04i | [Embeddings — Comparison](notebooks/04i-embeddings-comparison.qmd) | Comparação entre modelos |

### Analysis

| # | Notebook | Descrição |
|---|---------|-----------|
| 02.1 | [EDA — Data Wrangling](notebooks/02.1-EDA-data-wrangling.qmd) | EDA pós-wrangling |
| 02.2 | [Contexto Externo](notebooks/02.2-adicionar-contexto-externo.qmd) | Integração de dados externos |
| 02.3 | [EDA — Conteúdo e Interação](notebooks/02.3-EDA-conteudo-interacao.qmd) | Análise de conteúdo |
| 03 | [Contexto Externo](notebooks/03-contexto-externo.qmd) | Pipeline de contexto |
| 04 | [EDA — Overview](notebooks/04-eda-overview.qmd) | Visão geral da EDA |
| 04.1 | [EDA — Temporal](notebooks/04.1-eda-temporal.qmd) | Padrões temporais |
| 04.2 | [EDA — Interação](notebooks/04.2-eda-interacao.qmd) | Dinâmicas de interação |
| 04.3 | [EDA — Conteúdo](notebooks/04.3-eda-conteudo.qmd) | Análise de conteúdo |
| 05 | [EDA](notebooks/05-eda.qmd) | Análise exploratória geral |
| 05 | [Feature Engineering](notebooks/05-feature-engineering.qmd) | Feature engineering final |
| 06 | [Advanced Analysis](notebooks/06-advanced-analysis.qmd) | Clustering semântico, N-Grams, TF-IDF |

## Quick Start

```bash
git clone https://github.com/mrlnlms/whatsapp-interaction-analysis.git
cd whatsapp-interaction-analysis

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edite o .env com seus paths

quarto preview
```

### Dados de exemplo (sample)

O repo inclui um dataset sintético para testar o pipeline sem dados pessoais:

```bash
# Configure o .env para usar os dados sample
echo "PROJECT_ROOT=$(pwd)" > .env
echo "DATA_FOLDER=sample" >> .env

# Rode o pipeline de preparação
whatsapp-interaction prepare clean
whatsapp-interaction prepare wrangle
whatsapp-interaction status
```

O dataset sample (200 mensagens, 7 dias) é gerado deterministicamente por `scripts/generate_sample_data.py`.

Ver [Guia de Setup](docs/SETUP-GUIDE.md) completo.

### CLI

```bash
pip install -e .

# Pipeline completo
whatsapp-interaction run

# Só preparação (clean → wrangle → transcribe)
whatsapp-interaction prepare

# Etapas individuais
whatsapp-interaction prepare clean --steps u200e,anonymize
whatsapp-interaction process sentiment --model deberta

# Ver estado atual
whatsapp-interaction status
```

### Transcrição de áudios (opcional)

```bash
# Adicione sua API key no .env
echo "GROQ_API_KEY=sua_chave_aqui" >> .env

# Execute o script de transcrição (~40 min para ~700 arquivos)
python scripts/transcribe_media.py

# Re-rode o wrangling
quarto render notebooks/02-data-wrangling.qmd
```

O script detecta automaticamente arquivos já transcritos e continua de onde parou.

## Tests

```bash
pip install pytest
pytest tests/ -v
```

75 testes cobrindo o pipeline de limpeza (cleaning.py), parsing/classificação (wrangling.py) e CLI. CI roda automaticamente via GitHub Actions em Python 3.11 e 3.12.

## Tech Stack

**Core**: Python 3.11+, Quarto

**Data**: Pandas, NumPy, PyArrow

**Visualization**: Matplotlib, Seaborn, Plotly, WordCloud

**ML/Statistics**: Scikit-learn, Prince (MCA), SciPy

**NLP**: Transformers/PyTorch (sentiment — RoBERTa, DistilBERT, DeBERTa), Sentence-Transformers (embeddings — mpnet, MiniLM, DistilUSE), Groq API/Whisper (transcrição)

## Outputs

O pipeline gera os seguintes arquivos em `data/processed/{export}/`:

| Arquivo | Colunas | Descrição |
|---------|---------|-----------|
| `messages.csv` | 8 | Dataset principal para análise |
| `messages.parquet` | 8 | Mesmo conteúdo, ~3x menor |
| `messages_full.csv` | 17 | Versão completa para debug |
| `chat_complete.txt` | — | Chat com transcrições |
| `corpus_*.txt` | — | Textos para NLP |

## Documentation

- [Guia de Setup](docs/SETUP-GUIDE.md) — Instalação e configuração
- [Guia Incremental](docs/INCREMENTAL-GUIDE.md) — Como rodar com novos exports
- [Dicionário de Dados](docs/data-dictionary.md) — Descrição das variáveis
- [Pipeline](docs/pipeline.md) — Mapa de scripts, notebooks e artefatos
- [Roadmap](ROADMAP.md) — Próximos passos e evolução planejada

## Privacy

Os dados (`data/` e `analysis/`) não são versionados por conterem informações pessoais.

---

*Desenvolvido por [@mrlnlms](https://github.com/mrlnlms)*
