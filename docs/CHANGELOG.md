# Changelog

Histórico das fases do projeto. Não segue SemVer — projeto pré-release sem tags publicadas. Entradas em ordem cronológica reversa.

## Não publicado

### 2026-05-06/07 — Archeology v3 + manutenção

Reconstrução completa do histórico git e bloco de manutenção em sequência.

**Archeology v3:**
- 28 arquivos preservados que estavam fora do histórico antigo (variantes de cleaning/wrangling, R experiments, notas .md de fases pré-projeto, precursores)
- 105 → 139 commits backdated, heatmap do GitHub corrigido (08/dez pintado, densidade 24-26/nov)
- Pasta canonical antiga renomeada → backup → Trash; v3 virou canonical
- Plano completo em `docs/development/plans/2026-05-06-archeology-v3.md`

**Segurança:**
- Chave Groq antiga (hardcoded em `scripts/transcribe_media.py:42` no commit `43c92ab`) removida do histórico via `git filter-repo --replace-text` em todos os blobs afetados
- Chave rotacionada no Groq Console e atualizada no `.env` local
- Tag local `pre-secret-cleanup` preservada como segurança caso queira reverter

**CI/CD:**
- Workflow `publish.yml` ganhou setup R 4.5 (binários RSPM) + 7 pacotes: `tidyverse`, `gganimate`, `ggbump`, `ggtext`, `ggwordcloud`, `plotly`, `reticulate`
- Migração `setup-r-dependencies` (pak) → `install.packages` direto após bug de "dependency conflict" do pak v0.x com Ubuntu noble
- Actions bumpadas pro Node.js 24: `checkout@v6`, `setup-python@v6`, `deploy-pages@v5`, `upload-pages-artifact@v5`

**Site Quarto:**
- Seção **Lab** no navbar e sidebar com 8 experimentos R+Python preservados:
  - R + Python: Galeria de Visualizações, Gráficos R, Snippets R, Python ↔ R (reticulate)
  - Variantes Python: Cleaning Static/Hardened, Wrangling v1/Backup
- `notebooks/experiments/teste.qmd` excluído do render (imports legacy `from src.config` quebrados)
- Link `04-sentiment-ensemble.qmd` → `04e-sentiment-ensemble.qmd` corrigido em `04d-sentiment-comparison.qmd` e `docs/notes/6.4-Comparação...`

**README:**
- Traduzido para inglês
- **R 4.5** adicionado no Tech Stack com pacotes listados
- Seção Lab listando os 8 experimentos R+Python
- Seção CI/CD dedicada explicando os 2 workflows (tests + publish)
- Quick Start corrigido (extra `[all]` inexistente → recomendação `[notebooks]` modular)
- Badges: Tests, Quarto Publish, Python 3.11+, R 4.5, Quarto

**Mídia:**
- `data-overview` GIF (75MB, 256 cores) → MP4 H.264 (13.7MB, 16M cores) via `ffmpeg -crf 20`, redução de 82%
- `<img>` → `<video autoplay loop muted playsinline>` em `00-data-discovery.qmd`
- GIF original 80MB preservado em `local/` (gitignored)

**Versionamento:**
- `data/external/encontros.csv` (1KB, marcos do relacionamento — referenciado em `04-feature-engineering` e `02.3-EDA-conteudo-interacao`) versionado com exception no `.gitignore`
- `_quarto-naked.yml` e `_quarto-playground.yml` untracked do git, mantidos no FS local como scratch de layout
- Restauração de `.gitkeep` em `analysis/` e `data/integrated/`
- `local/` adicionado ao `.gitignore` (originais, fontes pesadas, scratch)

**Cleanup local (~3 GB liberados):**
- `local-workbench/REVIEW/Backup/`: 2 pastas (`whatsapp-ds-analytics 2/3`) + 24 .qmd/.md/.py soltos + 2 zips + Gemini image
- `local-workbench/REVIEW/QUARTO Studies/`: 4 variantes experimentais + zip precursor `whatsapp-analysis-v2`
- `local-workbench/REVIEW/QUALIA SURVEY BACKUPS/backup QMD AND QUALIA/`: subpastas `src/`, `utils/`, `notebooks/` + `_quarto.yml`
- `Môre/onboarding Môre Smiles/WhatsAPP DS/`: pasta inteira (19 .md, 5 .txt, 10 imagens — tudo já incorporado em `docs/notes/` e `local/`)
- `whatsapp-interaction-analysis-OLD-pre-v3/`: backup local pré-swap (2.7 GB)

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
