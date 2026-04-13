# Issue #2 — Quarto Website: Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate overlapping notebooks, reorganize the site structure, and publish a Quarto website on GitHub Pages.

**Architecture:** 3 notebook merges reduce 26 notebooks to 20 (6 archived). EDA dimensional notebooks renumbered (04.x → 05.x). Full navbar/sidebar config. GitHub Pages deploy via `_freeze/` for heavy ML notebooks + workflow.

**Tech Stack:** Quarto, GitHub Pages, GitHub Actions

**Spec:** `docs/development/specs/2026-04-13-quarto-website-design.md`

---

## Chunk 1: Notebook Consolidations

### Task 1: Merge A — Contexto Externo

Merge `02.2-adicionar-contexto-externo.qmd` (1.062 lines) + `03-contexto-externo.qmd` (1.686 lines) into a single `03-contexto-externo.qmd`.

**Files:**
- Read: `notebooks/02.2-adicionar-contexto-externo.qmd`
- Read: `notebooks/03-contexto-externo.qmd`
- Create: `notebooks/03-contexto-externo.qmd` (overwrite old 03)

**Merge strategy:** Use 02.2 as the base (cleaner pipeline structure), then append unique sections from 03.

- [ ] **Step 0: Backup original 03-contexto-externo before overwriting**

```bash
cd /Users/mosx/Desktop/whatsapp-interaction-analysis
mkdir -p notebooks/archive
cp notebooks/03-contexto-externo.qmd notebooks/archive/03-contexto-externo-original.qmd
```

- [ ] **Step 1: Read both source notebooks fully**

Read `02.2-adicionar-contexto-externo.qmd` and `03-contexto-externo.qmd` in their entirety to understand the cell-by-cell structure.

- [ ] **Step 2: Build the consolidated notebook**

Construct `03-contexto-externo.qmd` with this section ordering:

| Section | Source | Notes |
|---------|--------|-------|
| YAML frontmatter | 02.2 | Title: "Contexto Externo — Encontros Presenciais e Fases do Relacionamento" |
| Introdução | 02.2 | Hipótese sobre impacto do contexto externo |
| Setup (bibliotecas, caminhos, carregamento) | 02.2 | Imports + config + data load |
| Definição dos Encontros | 02.2 | 10 meeting dates, colors |
| Estatísticas Gerais | 02.2 | Coverage stats |
| Integração ao Dataset | 02.2 | 10 context features creation |
| Validação da Hipótese (4 partes) | 02.2 | Timeline, volume, gaps, temporal patterns |
| Impacto nos Padrões Temporais | 02.2 | Hora do dia, dia da semana |
| **Descoberta: Período Pré-Relacionamento** | **03** | **Amizade vs Relacionamento phase discovery** |
| **Validação: "Nunca Ficaram Sem Falar"** | **03** | **301/309 days validation** |
| **Decisão Metodológica** | **03** | **fase_relacionamento feature + column cleanup** |
| Export Final | **03** | **7-step validation from 03** (replaces 02.2's simpler export) |
| Conclusões | **03** | **Extended conclusions in Portuguese** |

Key rules:
- Deduplicate shared code (setup, encontros definitions, feature creation)
- Keep ALL unique insights/visualizations from both
- Use 03's export section (more thorough validation)
- Use 03's conclusions (more complete)
- Output: `messages_with_context.parquet`

- [ ] **Step 3: Validate the consolidated notebook renders**

Run: `cd /Users/mosx/Desktop/whatsapp-interaction-analysis && quarto render notebooks/03-contexto-externo.qmd`
Expected: Renders without error (may warn about missing data — that's OK with sample data)

- [ ] **Step 4: Commit**

```bash
~/.claude/scripts/commit.sh "feat: consolida notebooks de contexto externo (02.2 + 03) em 03-contexto-externo"
```

### Task 2: Merge B — Feature Engineering

Merge `03-feature-engineering.qmd` (1.246 lines) + `05-feature-engineering.qmd` (497 lines) into `04-feature-engineering.qmd`.

**Files:**
- Read: `notebooks/03-feature-engineering.qmd`
- Read: `notebooks/05-feature-engineering.qmd`
- Create: `notebooks/04-feature-engineering.qmd`

**Merge strategy:** Use 03-FE as the base (complete implementation of 35 features), insert 05-FE's unique documentation/validation sections.

- [ ] **Step 1: Read both source notebooks fully**

Read `03-feature-engineering.qmd` and `05-feature-engineering.qmd` in their entirety.

- [ ] **Step 2: Build the consolidated notebook**

Construct `04-feature-engineering.qmd` with this section ordering:

| Section | Source | Notes |
|---------|--------|-------|
| YAML frontmatter | 03-FE | Title: "Feature Engineering", Subtitle: "Implementação completa e consolidação de variáveis derivadas" |
| Introdução | 05-FE | Clearer objectives statement |
| Setup e configuração | 03-FE | More complete imports + paths |
| Carregamento dos dados | 03-FE | Load messages.parquet |
| **Dicionário de variáveis** | **05-FE** | **Documents upstream features from all notebooks** |
| Features Temporais (9) | 03-FE | Full implementation |
| Features de Texto (9) | 03-FE | Full implementation |
| Features de Conversação (7) | 03-FE | Full implementation incl. merge_asof helper |
| Features de Contexto Externo (10) | 03-FE | Full implementation from encontros.csv |
| **Consolidação e validação** | **05-FE** | **Category table with fill rates** |
| Exportação | 03-FE | Save messages_enriched.parquet |
| Resumo das Features | 03-FE | Complete 35-feature catalog |

Key rules:
- 05-FE's intro replaces 03-FE's (better framing)
- 05-FE's variable dictionary goes BEFORE implementation (context for reader)
- 05-FE's validation table goes AFTER implementation (verification)
- All 35 feature implementations from 03-FE preserved intact
- Output: `messages_enriched.parquet`

- [ ] **Step 3: Validate the consolidated notebook renders**

Run: `cd /Users/mosx/Desktop/whatsapp-interaction-analysis && quarto render notebooks/04-feature-engineering.qmd`
Expected: Renders without error

- [ ] **Step 4: Commit**

```bash
~/.claude/scripts/commit.sh "feat: consolida notebooks de feature engineering (03 + 05) em 04-feature-engineering"
```

### Task 3: Merge C — EDA Overview

Merge `04-eda-overview.qmd` (609 lines) + `05-eda.qmd` (343 lines) into `05-eda-overview.qmd`.

**Files:**
- Read: `notebooks/04-eda-overview.qmd`
- Read: `notebooks/05-eda.qmd`
- Create: `notebooks/05-eda-overview.qmd`

**Merge strategy:** Use 04-eda as the base (richer analysis with context), append 05-eda's unique sentiment analysis section.

- [ ] **Step 1: Read both source notebooks fully**

Read `04-eda-overview.qmd` and `05-eda.qmd` in their entirety.

- [ ] **Step 2: Build the consolidated notebook**

Construct `05-eda-overview.qmd` with this section ordering:

| Section | Source | Notes |
|---------|--------|-------|
| YAML frontmatter | 04-eda | Title: "Análise Exploratória Completa (EDA)", Subtitle: "Volume, tipos, contexto e sentimento integrados" |
| Introdução | 04-eda | Purpose + context integration |
| Setup | Both | Merge imports; prefer 05-eda's config-based paths (PATHS from config) |
| Carregamento dos dados | 04-eda | Load messages_with_context.parquet |
| Preview dos dados | 05-eda | Sample + inline statistics |
| Visão geral — Volume | 04-eda | Daily time series, by context, by sender (7 Plotly charts) |
| Distribuição de tipos de mensagem | 04-eda | Type breakdown + context comparison |
| **Análise de sentimento** | **05-eda** | **DistilBERT vs RoBERTa comparison, discordance, recommendation** |
| Síntese e conclusões | 04-eda | "Two communication modes" narrative |
| Próximos passos | 05-eda | Links to downstream analyses |

Key rules:
- No data output files (both are display-only)
- 04-eda's 7 Plotly visualizations ALL preserved
- 05-eda's sentiment section is the unique contribution — preserve intact
- Use callout boxes for insights (04-eda's style)

- [ ] **Step 3: Validate the consolidated notebook renders**

Run: `cd /Users/mosx/Desktop/whatsapp-interaction-analysis && quarto render notebooks/05-eda-overview.qmd`
Expected: Renders without error

- [ ] **Step 4: Commit**

```bash
~/.claude/scripts/commit.sh "feat: consolida notebooks de EDA (04-overview + 05-eda) em 05-eda-overview"
```

---

## Chunk 2: Renaming, Archiving, Cross-References

### Task 4: Rename EDA dimensional notebooks (04.x → 05.x)

**Files:**
- Rename: `notebooks/04.1-eda-temporal.qmd` → `notebooks/05.1-eda-temporal.qmd`
- Rename: `notebooks/04.2-eda-interacao.qmd` → `notebooks/05.2-eda-interacao.qmd`
- Rename: `notebooks/04.3-eda-conteudo.qmd` → `notebooks/05.3-eda-conteudo.qmd`

- [ ] **Step 1: Rename the 3 files**

```bash
cd /Users/mosx/Desktop/whatsapp-interaction-analysis/notebooks
git mv 04.1-eda-temporal.qmd 05.1-eda-temporal.qmd
git mv 04.2-eda-interacao.qmd 05.2-eda-interacao.qmd
git mv 04.3-eda-conteudo.qmd 05.3-eda-conteudo.qmd
```

- [ ] **Step 2: Commit**

```bash
~/.claude/scripts/commit.sh "refactor: renumera EDAs dimensionais (04.x -> 05.x)"
```

### Task 5: Archive original notebooks

**Files:**
- Create: `notebooks/archive/` directory
- Move: 6 original notebooks to archive

- [ ] **Step 1: Create archive directory and move originals**

```bash
cd /Users/mosx/Desktop/whatsapp-interaction-analysis
mkdir -p notebooks/archive
git mv notebooks/02.2-adicionar-contexto-externo.qmd notebooks/archive/
git mv notebooks/03-feature-engineering.qmd notebooks/archive/
git mv notebooks/05-feature-engineering.qmd notebooks/archive/
git mv notebooks/04-eda-overview.qmd notebooks/archive/
git mv notebooks/05-eda.qmd notebooks/archive/
```

Note: `03-contexto-externo.qmd` was overwritten in Task 1. The original was backed up in Task 1, Step 0 as `notebooks/archive/03-contexto-externo-original.qmd`.

- [ ] **Step 2: Commit**

```bash
~/.claude/scripts/commit.sh "chore: arquiva notebooks originais substituidos pelos consolidados"
```

### Task 6: Update cross-references in notebooks

Several notebooks reference old filenames. Update them all.

**Files to modify:**

| File | Old reference | New reference |
|------|--------------|---------------|
| `notebooks/02-data-wrangling.qmd:667` | `03-feature-engineering.qmd` | `04-feature-engineering.qmd` |
| `notebooks/02.1-EDA-data-wrangling.qmd:1273,1312` | `02.2-adicionar-contexto-externo.qmd` | `03-contexto-externo.qmd` |
| `notebooks/02.1-EDA-data-wrangling.qmd:1765` | `03-feature-engineering.qmd` | `04-feature-engineering.qmd` |
| `notebooks/02.3-EDA-conteudo-interacao.qmd:26,2327` | `02.2-adicionar-contexto-externo.qmd` | `03-contexto-externo.qmd` |
| `notebooks/02.3-EDA-conteudo-interacao.qmd:4816` | `03-feature-engineering.qmd` | `04-feature-engineering.qmd` |
| `notebooks/04-model-features.qmd:421` | `05-eda.qmd` | `05-eda-overview.qmd` |
| `notebooks/04e-sentiment-ensemble.qmd:537` | `05-eda.qmd` | `05-eda-overview.qmd` |
| `docs/data-dictionary.md` | `03-feature-engineering.qmd` | `04-feature-engineering.qmd` |
| `docs/INCREMENTAL-GUIDE.md` | `03-feature-engineering.qmd` | `04-feature-engineering.qmd` |

Also update any references inside the 3 newly consolidated notebooks (03-contexto-externo, 04-feature-engineering, 05-eda-overview) that may point to old names. In particular, the originals contained references to `05-eda-interacao.qmd` (a file that never existed — the correct name is `05.2-eda-interacao.qmd` after renaming).

- [ ] **Step 1: Update each cross-reference**

For each file, find the old reference and replace with the new one. Use the Edit tool with `replace_all: true` per file for each old name.

Key replacements:
- `02.2-adicionar-contexto-externo` → `03-contexto-externo` (everywhere)
- `03-feature-engineering` → `04-feature-engineering` (everywhere except archive/)
- `05-feature-engineering` → `04-feature-engineering` (everywhere except archive/)
- `04-eda-overview` → `05-eda-overview` (everywhere except archive/)
- `05-eda.qmd` → `05-eda-overview.qmd` (everywhere except archive/)
- `04.1-eda-temporal` → `05.1-eda-temporal` (everywhere)
- `04.2-eda-interacao` → `05.2-eda-interacao` (everywhere)
- `04.3-eda-conteudo` → `05.3-eda-conteudo` (everywhere)

**IMPORTANT:** Do NOT update files in `notebooks/archive/` or `docs/archive/` — those are historical records.

- [ ] **Step 2: Verify no broken references remain**

```bash
cd /Users/mosx/Desktop/whatsapp-interaction-analysis
# Search for old filenames in active notebooks (should return nothing)
grep -r "02.2-adicionar-contexto-externo\|03-feature-engineering\|05-feature-engineering\|04-eda-overview\|04\.1-eda-temporal\|04\.2-eda-interacao\|04\.3-eda-conteudo\|05-eda-interacao" notebooks/*.qmd index.qmd docs/pipeline.md docs/data-dictionary.md docs/INCREMENTAL-GUIDE.md 2>/dev/null || echo "All clean"
```

Note: `05-eda` matches will include `05-eda-overview` (the new name), so check manually that no bare `05-eda.qmd` references remain.

- [ ] **Step 3: Commit**

```bash
~/.claude/scripts/commit.sh "fix: atualiza cross-references entre notebooks apos consolidacao e renumeracao"
```

---

## Chunk 3: Quarto Site Configuration

### Task 7: Update _quarto.yml

Replace the current incomplete `_quarto.yml` with the full site configuration from the spec.

**Files:**
- Modify: `_quarto.yml`

- [ ] **Step 1: Write the complete _quarto.yml**

Replace the full content of `_quarto.yml` with:

```yaml
project:
  type: website
  output-dir: _site
  render:
    - "*.qmd"
    - "notebooks/*.qmd"
    - "docs/*.md"
    - "!docs/archive/**"
    - "!notebooks/archive/**"

website:
  title: "WhatsApp DS Analytics"
  description: "Pipeline de Data Science para análise de conversas do WhatsApp"

  navbar:
    title: "WhatsApp DS Analytics"
    left:
      - href: index.qmd
        text: Home
      - text: Preparação
        menu:
          - href: notebooks/00-data-discovery.qmd
            text: "00 - Data Discovery"
          - href: notebooks/00-data-profiling.qmd
            text: "00 - Data Profiling"
          - href: notebooks/01-data-cleaning.qmd
            text: "01 - Data Cleaning"
          - href: notebooks/02-data-wrangling.qmd
            text: "02 - Data Wrangling"
          - href: notebooks/02.1-EDA-data-wrangling.qmd
            text: "02.1 - EDA Data Wrangling"
          - href: notebooks/02.3-EDA-conteudo-interacao.qmd
            text: "02.3 - EDA Conteúdo e Interação"
          - href: notebooks/03-contexto-externo.qmd
            text: "03 - Contexto Externo"
          - href: notebooks/04-feature-engineering.qmd
            text: "04 - Feature Engineering"
      - text: Modelos
        menu:
          - href: notebooks/04-model-features.qmd
            text: "Modelos — Overview"
          - text: "---"
          - text: "Sentiment Analysis"
          - href: notebooks/04a-sentiment-roberta.qmd
            text: "04a - RoBERTa"
          - href: notebooks/04b-sentiment-distilbert.qmd
            text: "04b - DistilBERT"
          - href: notebooks/04c-sentiment-deberta.qmd
            text: "04c - DeBERTa"
          - href: notebooks/04d-sentiment-comparison.qmd
            text: "04d - Comparação"
          - href: notebooks/04e-sentiment-ensemble.qmd
            text: "04e - Ensemble"
          - text: "---"
          - text: "Embeddings"
          - href: notebooks/04f-embeddings-mpnet.qmd
            text: "04f - MPNet"
          - href: notebooks/04g-embeddings-minilm.qmd
            text: "04g - MiniLM"
          - href: notebooks/04h-embeddings-distiluse.qmd
            text: "04h - DistilUSE"
          - href: notebooks/04i-embeddings-comparison.qmd
            text: "04i - Comparação"
      - text: Análise
        menu:
          - href: notebooks/05-eda-overview.qmd
            text: "05 - EDA Overview"
          - href: notebooks/05.1-eda-temporal.qmd
            text: "05.1 - EDA Temporal"
          - href: notebooks/05.2-eda-interacao.qmd
            text: "05.2 - EDA Interação"
          - href: notebooks/05.3-eda-conteudo.qmd
            text: "05.3 - EDA Conteúdo"
          - href: notebooks/06-advanced-analysis.qmd
            text: "06 - Análise Avançada"
      - text: Referência
        menu:
          - href: docs/data-dictionary.md
            text: "Dicionário de Dados"
          - href: docs/pipeline.md
            text: "Pipeline"
    tools:
      - icon: github
        href: https://github.com/mrlnlms/whatsapp-interaction-analysis

  sidebar:
    style: docked
    search: true
    contents:
      - section: "Projeto"
        contents:
          - index.qmd
          - docs/data-dictionary.md
          - docs/pipeline.md
      - section: "Preparação"
        contents:
          - notebooks/00-data-discovery.qmd
          - notebooks/00-data-profiling.qmd
          - notebooks/01-data-cleaning.qmd
          - notebooks/02-data-wrangling.qmd
          - notebooks/02.1-EDA-data-wrangling.qmd
          - notebooks/02.3-EDA-conteudo-interacao.qmd
          - notebooks/03-contexto-externo.qmd
          - notebooks/04-feature-engineering.qmd
      - section: "Modelos"
        contents:
          - notebooks/04-model-features.qmd
          - section: "Sentiment"
            contents:
              - notebooks/04a-sentiment-roberta.qmd
              - notebooks/04b-sentiment-distilbert.qmd
              - notebooks/04c-sentiment-deberta.qmd
              - notebooks/04d-sentiment-comparison.qmd
              - notebooks/04e-sentiment-ensemble.qmd
          - section: "Embeddings"
            contents:
              - notebooks/04f-embeddings-mpnet.qmd
              - notebooks/04g-embeddings-minilm.qmd
              - notebooks/04h-embeddings-distiluse.qmd
              - notebooks/04i-embeddings-comparison.qmd
      - section: "Análise"
        contents:
          - notebooks/05-eda-overview.qmd
          - notebooks/05.1-eda-temporal.qmd
          - notebooks/05.2-eda-interacao.qmd
          - notebooks/05.3-eda-conteudo.qmd
          - notebooks/06-advanced-analysis.qmd

  page-footer:
    center: |
      Desenvolvido por [@mrlnlms](https://github.com/mrlnlms)

format:
  html:
    theme: cosmo
    toc: true
    toc-depth: 3
    code-fold: true
    code-tools: true
    code-overflow: wrap
    highlight-style: github

execute:
  freeze: auto
  warning: false
  message: false
  echo: true
  jupyter: whatsapp-ds
  daemon: false
```

- [ ] **Step 2: Commit**

```bash
~/.claude/scripts/commit.sh "feat: atualiza _quarto.yml com estrutura completa do site (20 notebooks, 5 secoes)"
```

### Task 8: Fix .gitignore and add freeze to heavy notebooks

**Files:**
- Modify: `.gitignore` (remove `_freeze/`)
- Modify: 8 heavy notebooks (add `freeze: true` to frontmatter)

- [ ] **Step 1: Remove `_freeze/` from .gitignore**

In `.gitignore`, remove the line `_freeze/` from the "Quarto gerados" section.

- [ ] **Step 2: Add `freeze: true` to heavy notebook frontmatters**

For each of these 8 notebooks, add `execute: freeze: true` to the YAML frontmatter:

1. `notebooks/04-model-features.qmd`
2. `notebooks/04a-sentiment-roberta.qmd`
3. `notebooks/04b-sentiment-distilbert.qmd`
4. `notebooks/04c-sentiment-deberta.qmd`
5. `notebooks/04f-embeddings-mpnet.qmd`
6. `notebooks/04g-embeddings-minilm.qmd`
7. `notebooks/04h-embeddings-distiluse.qmd`
8. `notebooks/06-advanced-analysis.qmd`

Example frontmatter addition:
```yaml
execute:
  freeze: true
```

Note: `04d-sentiment-comparison`, `04e-sentiment-ensemble`, and `04i-embeddings-comparison` are **light** notebooks (no torch/transformers) — do NOT add freeze to them.

- [ ] **Step 3: Commit**

```bash
~/.claude/scripts/commit.sh "chore: remove _freeze/ do .gitignore e adiciona freeze: true nos notebooks heavy"
```

---

## Chunk 4: Content Updates and Deploy

### Task 9: Update index.qmd

The current `index.qmd` has outdated references (`src/`, old notebook names, broken links).

**Files:**
- Modify: `index.qmd`

- [ ] **Step 1: Read current index.qmd**

Read the full file to identify all outdated references.

- [ ] **Step 2: Update the navigation table**

Replace the "Pipeline Principal" table with updated notebook names:

```markdown
## Pipeline Principal

| Fase | Documento | Descrição |
|------|-----------|-----------|
| Discovery | [00-data-discovery](notebooks/00-data-discovery.qmd) | Exploração inicial do arquivo bruto |
| Profiling | [00-data-profiling](notebooks/00-data-profiling.qmd) | Investigação da estrutura do arquivo |
| Cleaning | [01-data-cleaning](notebooks/01-data-cleaning.qmd) | Limpeza e normalização |
| Wrangling | [02-data-wrangling](notebooks/02-data-wrangling.qmd) | Parsing, vinculação de mídia, transcrição |
| Contexto | [03-contexto-externo](notebooks/03-contexto-externo.qmd) | Integração de contexto externo |
| Features | [04-feature-engineering](notebooks/04-feature-engineering.qmd) | Criação de 35+ variáveis derivadas |
| EDA | [05-eda-overview](notebooks/05-eda-overview.qmd) | Análise exploratória com contexto |
| Advanced | [06-advanced-analysis](notebooks/06-advanced-analysis.qmd) | Clustering, N-Grams, TF-IDF |
```

- [ ] **Step 3: Update the architecture section**

Replace references from `src/` to `whatsapp/pipeline/`:

```
whatsapp/pipeline/              # Lógica (módulos Python)
├── config.py                   # Configurações
├── cleaning.py                 # Pipeline de limpeza (7 etapas)
├── wrangling.py                # Pipeline de wrangling (6 etapas)
└── utils/                      # Utilitários
```

- [ ] **Step 4: Update the project structure tree**

Replace the `src/` tree with `whatsapp/` tree matching current reality.

- [ ] **Step 5: Commit**

```bash
~/.claude/scripts/commit.sh "fix: atualiza index.qmd com nomes consolidados e estrutura whatsapp/"
```

### Task 10: Update README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add site link at the top**

After the blockquote, add:

```markdown
**[Ver site publicado](https://mrlnlms.github.io/whatsapp-interaction-analysis/)**
```

- [ ] **Step 2: Update the Notebooks section**

Replace the entire Notebooks section with the new structure matching the spec's final notebook table (Preparação, Modelos, Análise sections).

- [ ] **Step 3: Update test count**

Current text says "75 testes" — update to "149 testes" (current count).

- [ ] **Step 4: Commit**

```bash
~/.claude/scripts/commit.sh "docs: atualiza README com link do site e notebooks consolidados"
```

### Task 11: Add GitHub Pages deploy workflow

**Files:**
- Create: `.github/workflows/publish.yml`

- [ ] **Step 1: Write the workflow file**

Create `.github/workflows/publish.yml` with this content:

```yaml
name: Quarto Publish

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build-deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v5

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - uses: quarto-dev/quarto-actions/setup@v2

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[test]" jupyter ipykernel
          python -m ipykernel install --user --name whatsapp-ds

      - name: Render
        run: quarto render

      - uses: actions/upload-pages-artifact@v3
        with:
          path: _site

      - uses: actions/deploy-pages@v4
        id: deployment
```

- [ ] **Step 2: Commit**

```bash
~/.claude/scripts/commit.sh "feat: adiciona workflow de deploy Quarto para GitHub Pages"
```

### Task 12: Local render, commit _freeze/, and validate

**CRITICAL:** This must happen before pushing. The `_freeze/` directory needs to be populated and committed so CI doesn't try to render heavy notebooks.

- [ ] **Step 1: Render the full site locally**

```bash
cd /Users/mosx/Desktop/whatsapp-interaction-analysis
quarto render
```

Expected: All light notebooks render. Heavy notebooks with `freeze: true` either use cached freeze or skip (first render will execute them if no cache exists — this is expected and may take a while).

If heavy notebooks fail (missing torch/data), that's OK — their `freeze: true` means CI will also skip them. We can populate `_freeze/` for them later when the user renders locally with the right environment.

**Fallback — render only light notebooks individually:**
```bash
for nb in 00-data-discovery 00-data-profiling 01-data-cleaning 02-data-wrangling 02.1-EDA-data-wrangling 02.3-EDA-conteudo-interacao 03-contexto-externo 04-feature-engineering 04d-sentiment-comparison 04e-sentiment-ensemble 04i-embeddings-comparison 05-eda-overview 05.1-eda-temporal 05.2-eda-interacao 05.3-eda-conteudo; do
  quarto render "notebooks/${nb}.qmd" || echo "FAILED: ${nb}"
done
quarto render index.qmd
quarto render docs/data-dictionary.md
quarto render docs/pipeline.md
```

- [ ] **Step 2: Verify _site/ was generated**

```bash
ls _site/index.html
ls _site/notebooks/
```

Expected: `index.html` exists, notebook HTML files present.

- [ ] **Step 3: Commit _freeze/ if populated**

```bash
git add _freeze/
~/.claude/scripts/commit.sh "chore: adiciona _freeze/ para cache de notebooks no CI"
```

- [ ] **Step 4: Verify site locally**

```bash
quarto preview
```

Open in browser, check:
- [ ] Navbar has all 5 sections (Home, Preparação, Modelos, Análise, Referência)
- [ ] Sidebar navigation works
- [ ] Light notebooks render with content
- [ ] Links between notebooks work
- [ ] GitHub icon in navbar links correctly

### Task 13: Enable GitHub Pages and push

- [ ] **Step 1: Verify GitHub Pages is configured**

The repo needs Pages enabled with "GitHub Actions" as source (not branch-based).

```bash
gh api repos/mrlnlms/whatsapp-interaction-analysis/pages 2>/dev/null || echo "Pages not configured yet"
```

If not configured, the user needs to enable it in repo Settings > Pages > Source: GitHub Actions.

- [ ] **Step 2: Push all changes**

```bash
git push origin main
```

- [ ] **Step 3: Verify deployment**

```bash
gh run list --workflow=publish.yml --limit=1
```

Wait for the run to complete, then verify the site is live at `https://mrlnlms.github.io/whatsapp-interaction-analysis/`.
