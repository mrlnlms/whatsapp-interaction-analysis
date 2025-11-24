# WhatsApp Conversation Analysis

> Transformando um ano de mensagens em dados estruturados para análise de padrões de comunicação.

## 📋 Sobre

Este projeto demonstra um pipeline completo de **Data Science**, desde a investigação inicial de dados brutos até análises avançadas com clustering e visualizações. O caso de estudo é um export do WhatsApp com ~92.000 mensagens ao longo de 1 ano de relacionamento.

## 🔄 Pipeline

```
DATA PREPARATION                          DATA ANALYSIS
┌─────────────────────────────────────┐   ┌─────────────────────────┐
│ Profiling → Cleaning → Wrangling → │ → │ EDA → Descritiva →     │ → Comunicação
│             Feature Engineering     │   │      Avançada          │
└─────────────────────────────────────┘   └─────────────────────────┘
```

### Etapas detalhadas

| Fase | Etapa | Descrição |
|------|-------|-----------|
| **Preparation** | Data Profiling | Investigação da estrutura do arquivo bruto |
| | Data Cleaning | Remoção de caracteres invisíveis, normalização |
| | Data Wrangling | Parsing, vinculação de mídia, transcrição |
| | Feature Engineering | Criação de 35 variáveis derivadas |
| **Analysis** | EDA | Análise exploratória |
| | Descritiva | Estatísticas e distribuições |
| | Avançada | Clustering, PCA, radar charts |

## 📁 Estrutura

```
whatsapp-analysis-v2/
│
├── index.qmd                    # Documento principal (overview)
│
├── src/                         # Módulos Python
│   ├── profiling.py            # Funções de investigação
│   ├── cleaning.py             # Limpeza de dados
│   ├── parsing.py              # Parser txt → DataFrame
│   ├── wrangling.py            # Vinculação e transcrição
│   ├── features.py             # Feature engineering
│   ├── audit.py                # Auditoria de transformações
│   └── config.py               # Configurações centralizadas
│
├── notebooks/                   # Documentos Quarto
│   ├── 00-data-profiling.qmd   # Investigação inicial
│   ├── 01-data-preparation.qmd # Pipeline de preparação
│   ├── 02-eda.qmd              # Análise exploratória
│   └── 03-advanced.qmd         # Análises avançadas
│
├── data/
│   ├── raw/                    # Dados brutos
│   ├── interim/                # Arquivos intermediários
│   └── processed/              # Outputs finais
│
├── docs/
│   └── data-dictionary.md      # Dicionário de dados
│
└── outputs/                    # Gráficos e relatórios
```

## 🛠️ Tecnologias

- **Python 3.11+**
- **Pandas** — Manipulação de dados
- **Quarto** — Documentação reprodutível
- **Matplotlib / Plotly** — Visualizações
- **Groq API (Whisper)** — Transcrição de áudios

## 📊 Dataset Final

| Métrica | Valor |
|---------|-------|
| Mensagens | 91.924 |
| Features | 35 |
| Período | Out/2024 — Out/2025 |
| Participantes | 2 (anonimizados) |

## 🚀 Como usar

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/whatsapp-analysis-v2.git

# Instale dependências
pip install pandas matplotlib plotly

# Execute o pipeline
cd notebooks
quarto render 00-data-profiling.qmd
```

## 📝 Documentos

- [index.qmd](index.qmd) — Overview do projeto
- [Data Profiling](notebooks/00-data-profiling.qmd) — Investigação inicial
- [Dicionário de Dados](docs/data-dictionary.md) — Descrição de todas as variáveis

## 📌 Highlights

- **Transcrição automática** de 695 áudios/vídeos via API
- **Pipeline modular** com funções reutilizáveis
- **Auditoria completa** de cada transformação
- **Radar chart** comparativo de perfis de comunicação

---

*Projeto desenvolvido como estudo de caso em Data Science.*
