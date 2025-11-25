# WhatsApp DS Analytics

> Pipeline completo de Data Science para análise de conversas do WhatsApp.

## 📋 Sobre

Este projeto demonstra um pipeline completo de **Data Science**, desde a investigação inicial de dados brutos até análises avançadas com clustering e visualizações. O caso de estudo é um export do WhatsApp com ~92.000 mensagens ao longo de 1 ano.

O projeto foi desenvolvido para ser **reprodutível** — permite rodar o pipeline com novos exports e integrar os resultados à base existente.

## 🔄 Pipeline

![](./assets/images/ds-pipeline-to-insight.png)

### Etapas detalhadas

| Fase | Etapa | Descrição |
|------------------|---------------------|---------------------------------|
| **Preparation** | Data Profiling | Investigação da estrutura do arquivo bruto |
|  | Data Cleaning | Remoção de caracteres invisíveis, normalização |
|  | Data Wrangling | Parsing, vinculação de mídia, transcrição |
|  | Feature Engineering | Criação de 35 variáveis derivadas |
| **Analysis** | EDA | Análise exploratória |
|  | Descritiva | Estatísticas e distribuições |
|  | Avançada | Clustering, PCA, radar charts |

## 📁 Estrutura

```
whatsapp-ds-analytics/
│
├── .env.example                 # Template de configuração
├── index.qmd                    # Documento principal (overview)
│
├── assets/                      # Recursos estáticos
│   └── images/                  # Diagramas, screenshots
│
├── src/                         # Módulos Python
│   ├── config.py                # Configurações (lê do .env)
│   ├── profiling.py             # Funções de investigação
│   ├── cleaning.py              # Pipeline de limpeza (7 etapas)
│   ├── wrangling.py             # Pipeline de wrangling (6 etapas)
│   ├── features.py              # Feature engineering
│   └── utils/
│       ├── __init__.py
│       └── audit.py             # Sistema de auditoria
│
├── scripts/                     # Scripts standalone
│   ├── README.md                # Documentação dos scripts
│   └── transcribe_media.py      # Transcrição via Groq/Whisper
│
├── notebooks/                   # Documentos Quarto
│   ├── 00-data-profiling.qmd
│   ├── 01-data-cleaning.qmd
│   ├── 02-data-wrangling.qmd
│   ├── 03-feature-engineering.qmd
│   ├── 04-eda.qmd
│   └── 05-advanced-analysis.qmd
│
├── data/                        # 🚫 Não versionado
│   ├── raw/                     # Exports brutos por período
│   ├── interim/                 # Arquivos intermediários
│   ├── processed/               # DataFrames por execução
│   └── integrated/              # Base consolidada
│
├── analysis/                    # 🚫 Não versionado
│
└── docs/
    ├── SETUP-GUIDE.md           # Guia de instalação
    └── data-dictionary.md       # Dicionário de dados
```

## 🚀 Quick Start

```bash
# Clone e configure
git clone https://github.com/mrlnlms/whatsapp-ds-analytics.git
cd whatsapp-ds-analytics

# Setup do ambiente
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m ipykernel install --user --name=whatsapp-ds --display-name="WhatsApp DS"

# Configure seus paths
cp .env.example .env
# Edite o .env com seus paths

# Rode o projeto
quarto preview
```

Veja o [Guia de Setup](docs/SETUP-GUIDE.md) completo para mais detalhes.

### 🎙️ Transcrição de Áudios (Opcional)

Para transcrever áudios e vídeos do WhatsApp:

```bash
# Adicione sua API key no .env
echo "GROQ_API_KEY=sua_chave_aqui" >> .env

# Execute o script de transcrição (~40 min para ~700 arquivos)
python scripts/transcribe_media.py

# Rode o notebook de wrangling novamente
quarto render notebooks/02-data-wrangling.qmd
```

O script detecta automaticamente arquivos já transcritos e continua de onde parou.

## 🛠️ Tecnologias

- **Python 3.11+**
- **Quarto** — Documentação reprodutível

### Data Manipulation

- **Pandas / NumPy** — Manipulação e análise de dados
- **PyArrow** — Export otimizado em Parquet

### Visualization

- **Matplotlib / Seaborn / Plotly** — Gráficos e visualizações
- **WordCloud** — Nuvens de palavras

### Machine Learning & Statistics

- **Scikit-learn** — Clustering, PCA, métricas
- **Prince** — Análise de Correspondência Múltipla (MCA)
- **SciPy** — Estatística

### NLP & Sentiment Analysis

- **Transformers / PyTorch** — Análise de sentimento (BERT)
- **Groq API (Whisper)** — Transcrição de áudios/vídeos

## 📦 Outputs do Pipeline

O pipeline gera os seguintes arquivos em `data/processed/{DATA_FOLDER}/`:

| Arquivo | Colunas | Descrição |
|---------|---------|-----------|
| `messages.csv` | 8 | **Dataset principal para análise** |
| `messages.parquet` | 8 | Mesmo conteúdo, ~3x menor |
| `messages_full.csv` | 17 | Versão completa para debug |
| `chat_complete.txt` | — | Chat com transcrições |
| `corpus_*.txt` | — | Textos para NLP |

## 📝 Documentação

- [Guia de Setup](docs/SETUP-GUIDE.md) — Instalação e configuração
- [Dicionário de Dados](docs/data-dictionary.md) — Descrição das variáveis
- [Scripts](scripts/README.md) — Documentação dos scripts utilitários

### Notebooks

| # | Notebook | Descrição |
|---|----------|-----------|
| 00 | [Data Profiling](notebooks/00-data-profiling.qmd) | Investigação do arquivo bruto |
| 01 | [Data Cleaning](notebooks/01-data-cleaning.qmd) | Limpeza e normalização |
| 02 | [Data Wrangling](notebooks/02-data-wrangling.qmd) | Parsing, mídia, transcrição |
| 03 | [Feature Engineering](notebooks/03-feature-engineering.qmd) | Criação de variáveis |
| 04 | [EDA](notebooks/04-eda.qmd) | Análise exploratória |
| 05 | [Advanced Analysis](notebooks/05-advanced-analysis.qmd) | Clustering, MCA, PCA |

## 📌 Highlights

- **Pipeline reprodutível** — rode com novos exports e integre à base
- **Arquitetura modular** — lógica em `src/`, apresentação em `notebooks/`
- **Configuração via `.env`** — um só lugar pra ajustar paths
- **Transcrição automática** de áudios/vídeos via Groq API
- **Export otimizado** — CSV para compatibilidade, Parquet para performance
- **Sistema de auditoria** — métricas de cada transformação

## 🔒 Privacidade

Os dados (`data/` e `analysis/`) **não são versionados** por conterem informações pessoais.

---

*Desenvolvido por [@mrlnlms](https://github.com/mrlnlms)*