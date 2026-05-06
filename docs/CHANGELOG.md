# Changelog

Histórico das fases do projeto. Não segue SemVer — projeto pré-release sem tags publicadas. Entradas em ordem cronológica reversa.

## Não publicado

### 2026-05-06 — Lab R+Python

- Adicionada seção **Lab** no navbar e sidebar do site Quarto com experimentos R+Python
- Workflow de deploy fixado em R 4.5 (binários RSPM) — uso direto de `install.packages` em vez de `setup-r-dependencies` (pak)
- Restauração de `.gitkeep` em `analysis/` e `data/integrated/`
- `local/` adicionado ao gitignore (originais, fontes pesadas, scratch)

### 2026-04-13 — Camada de findings + site Quarto público

**Findings (notebooks 07-11):**
- 07 — Overview narrativo + arco do ano
- 08 — Dinâmica temporal (89k msgs em 308 dias, 297/dia média)
- 09 — Sentimento (ensemble de 3 modelos: 58% neutro / 27% pos / 15% neg, estável no ano)
- 10 — Temas (K-Means k=10 sobre mpnet embeddings + TF-IDF + UMAP 2D)
- 11 — Estilos P1 vs P2 (P1 emoji-diverso; P2 carimba 💚 1.504 vezes)
- Seção "Principais Descobertas" no topo da home com 5 bullets linkando os findings

**Site Quarto ([issue #2](https://github.com/mrlnlms/whatsapp-interaction-analysis/issues/2)):**
- Publicado em [mrlnlms.github.io/whatsapp-interaction-analysis](https://mrlnlms.github.io/whatsapp-interaction-analysis/)
- Deploy automático via `publish.yml` (GitHub Pages)
- 25 notebooks ativos em 6 seções (Home, Preparação, Modelos, Análise, Descobertas, Referência)
- `freeze: true` global + `error: true` — CI usa `_freeze/` commitado, nunca re-executa
- Timeline Ultimate na página principal (`assets/images/timeline-ultimate.png`)
- Script gerador: `scripts/generate_timeline_chart.py`

**Consolidação de notebooks:**
- `02.2 + 03-contexto-externo` → `03-contexto-externo.qmd`
- `03-FE + 05-FE` → `04-feature-engineering.qmd`
- `04-eda-overview + 05-eda` → `05-eda-overview.qmd`
- EDAs dimensionais renumeradas: 04.x → 05.x
- 6 originais preservados em `notebooks/archive/`

**Refactor de imports:**
- Migração de `sys.path` hacks para `from whatsapp.pipeline.*` em todos os notebooks
- Símlink `src/` removido

### 2026-03-29 — Hardening + reestruturação

Sessão maratona reorganizando o projeto para padrão de produção.

- **Testes:** 149 testes unitários, CI verde em Python 3.11/3.12
- **CLI unificado:** `whatsapp-interaction` (Typer) com comandos `prepare`, `process`, `run`, `status` — [issue #3](https://github.com/mrlnlms/whatsapp-interaction-analysis/issues/3)
- **Pacote unificado:** reestruturação `src/` → `whatsapp/` (imports absolutos, zero `sys.path` hacks)
- **Dependências:** migração para `pyproject.toml` com optional groups (eliminados `requirements.txt` e `requirements-test.txt`)
- **Schema validation** entre stages do pipeline de wrangling
- **Type hints** em `cleaning.py`
- **Exceções específicas** em vez de `except Exception`
- **Path traversal fix** e tratamento de NaN em `link_media_to_messages` / `extract_filename_from_content`
- **Dataset sample:** 200 mensagens sintéticas (seed=42) em `data/raw/sample/` — [issue #1](https://github.com/mrlnlms/whatsapp-interaction-analysis/issues/1)
- README e SETUP-GUIDE atualizados para instalação via pyproject

## Pré-história (reconstrução arqueológica)

História antes do repo atual. Os 17 primeiros commits foram **replayed backdated** em 29/mar/2026 a partir de 3 fontes:

| Alias | Path | Conteúdo |
|-------|------|----------|
| MAIN  | `~/Desktop/Whatsapps Project` | Pasta principal de trabalho |
| WT    | `~/.claude-worktrees/whatsapp-ds-analytics/nostalgic-tharp` | Worktree branch NLP/advanced |
| GH    | GitHub `mrlnlms/whatsapp-ds-analytics` | Repo original, 12 commits |

Backups originais preservados em `~/Desktop/_backup-whatsapp-old/`. O repo no GitHub foi renomeado de `whatsapp-ds-analytics` para `whatsapp-interaction-analysis` e force-pushed com o histórico reconstruído.

### 2025-12-07 — NLP avançado (worktree nostalgic-tharp)

- `06-advanced-analysis.qmd` — clustering semântico, N-Grams, TF-IDF (37KB)

### 2025-11-30 a 2025-12-06 — Phase 1b ("ZAP")

- Versões otimizadas dos embeddings, EDA alternativo
- Arquivado em `docs/archive/phase-1-structuring/`

### 2025-11-24 a 2025-11-29 — Estruturação

- Estrutura `notebooks/`, `src/`, `scripts/`
- Sentiment multi-modelo: RoBERTa, DistilBERT, DeBERTa, ensemble
- Embeddings: mpnet, MiniLM, DistilUSE
- EDA por dimensão (temporal, interação, conteúdo)

### 2025-11-20 a 2025-11-25 — Exploração (whats-le)

- Scripts soltos, 7+ iterações de wrangling
- Notebooks exploratórios
- Arquivado em `docs/archive/phase-0-exploration/`
