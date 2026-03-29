# Reorganização do Pacote Python — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganizar o projeto de dois pacotes soltos (`cli/` + `src/`) para um pacote Python unificado (`whatsapp/`) com imports absolutos, eliminando todos os hacks de `sys.path`.

**Architecture:** Mover `cli/` para `whatsapp/cli/` e `src/` para `whatsapp/pipeline/`, criando um namespace único. O pyproject.toml usa setuptools package discovery com `include = ["whatsapp*"]`. Scripts standalone em `scripts/` continuam fora do pacote mas importam via `from whatsapp.pipeline.config import PATHS` (requer `pip install -e .`).

**Tech Stack:** Python 3.11+, Typer (CLI), setuptools (packaging), pytest

---

## File Structure

### Novos arquivos
- `whatsapp/__init__.py` — versão e metadata do pacote
- `whatsapp/__main__.py` — entry point para `python -m whatsapp`

### Arquivos movidos (cli/ → whatsapp/cli/)
- `cli/__init__.py` → `whatsapp/cli/__init__.py`
- `cli/__main__.py` → removido (substituído por `whatsapp/__main__.py`)
- `cli/helpers.py` → `whatsapp/cli/helpers.py`
- `cli/prepare.py` → `whatsapp/cli/prepare.py`
- `cli/process.py` → `whatsapp/cli/process.py`
- `cli/_status.py` → `whatsapp/cli/_status.py`

### Arquivos movidos (src/ → whatsapp/pipeline/)
- `src/__init__.py` → removido (conteúdo migra para `whatsapp/__init__.py`)
- `src/config.py` → `whatsapp/pipeline/config.py`
- `src/cleaning.py` → `whatsapp/pipeline/cleaning.py`
- `src/wrangling.py` → `whatsapp/pipeline/wrangling.py`
- `src/profiling.py` → `whatsapp/pipeline/profiling.py`
- `src/utils/__init__.py` → `whatsapp/pipeline/utils/__init__.py`
- `src/utils/audit.py` → `whatsapp/pipeline/utils/audit.py`
- `src/utils/dataframe_helpers.py` → `whatsapp/pipeline/utils/dataframe_helpers.py`
- `src/utils/file_helpers.py` → `whatsapp/pipeline/utils/file_helpers.py`
- `src/utils/text_helpers.py` → `whatsapp/pipeline/utils/text_helpers.py`

### Arquivos modificados (imports)
- `pyproject.toml` — entry point + package discovery
- `tests/conftest.py` — sem mudança (sem imports de src/cli)
- `tests/test_cleaning.py` — imports
- `tests/test_wrangling.py` — imports
- `tests/test_cli.py` — imports
- `scripts/*.py` (12 arquivos) — imports
- `.github/workflows/tests.yml` — adicionar `pip install -e .`
- `README.md` — diagrama de estrutura

### Arquivos removidos
- `cli/` (diretório antigo, após mover)
- `src/` (diretório antigo, após mover)

---

## Chunk 1: Estrutura e movimentação

### Task 1: Criar estrutura do pacote whatsapp/

**Files:**
- Create: `whatsapp/__init__.py`
- Create: `whatsapp/__main__.py`
- Create: `whatsapp/pipeline/__init__.py`

- [ ] **Step 1: Criar `whatsapp/__init__.py`**

```python
"""WhatsApp Interaction Analysis — pipeline de análise de conversas."""

__version__ = '0.1.0'
__author__ = 'Marlon'
```

- [ ] **Step 2: Criar `whatsapp/__main__.py`**

```python
"""Entry point para python -m whatsapp."""

from whatsapp.cli import app

app()
```

- [ ] **Step 3: Criar `whatsapp/pipeline/__init__.py`**

```python
"""Módulos de processamento de dados do pipeline WhatsApp."""

from .config import (
    PARTICIPANTES,
    PATHS,
    THRESHOLDS,
    PERIODOS_DIA,
    DIAS_SEMANA,
    MESES,
    REGEX_PATTERNS
)
```

- [ ] **Step 4: Commit**

```bash
~/.claude/scripts/commit.sh "feat: cria estrutura do pacote whatsapp/"
```

---

### Task 2: Mover src/ → whatsapp/pipeline/

**Files:**
- Move: `src/config.py` → `whatsapp/pipeline/config.py`
- Move: `src/cleaning.py` → `whatsapp/pipeline/cleaning.py`
- Move: `src/wrangling.py` → `whatsapp/pipeline/wrangling.py`
- Move: `src/profiling.py` → `whatsapp/pipeline/profiling.py`
- Move: `src/utils/` → `whatsapp/pipeline/utils/`
- Remove: `src/`

- [ ] **Step 1: Mover arquivos (usar git mv para preservar histórico)**

```bash
# Mover módulos
git mv src/config.py whatsapp/pipeline/config.py
git mv src/cleaning.py whatsapp/pipeline/cleaning.py
git mv src/wrangling.py whatsapp/pipeline/wrangling.py
git mv src/profiling.py whatsapp/pipeline/profiling.py

# Mover utils/
mkdir -p whatsapp/pipeline/utils
git mv src/utils/__init__.py whatsapp/pipeline/utils/__init__.py
git mv src/utils/audit.py whatsapp/pipeline/utils/audit.py
git mv src/utils/dataframe_helpers.py whatsapp/pipeline/utils/dataframe_helpers.py
git mv src/utils/file_helpers.py whatsapp/pipeline/utils/file_helpers.py
git mv src/utils/text_helpers.py whatsapp/pipeline/utils/text_helpers.py

# Remover src/__init__.py (não migra — conteúdo já está em whatsapp/__init__.py)
git rm src/__init__.py
```

- [ ] **Step 2: Atualizar import interno em `whatsapp/pipeline/cleaning.py`**

Trocar:
```python
from utils import audit_transformation, audit_pipeline
```
Por:
```python
from whatsapp.pipeline.utils import audit_transformation, audit_pipeline
```

- [ ] **Step 3: Atualizar imports internos em `whatsapp/pipeline/wrangling.py`**

Procurar qualquer `from config import`, `from utils import` e trocar para imports absolutos com prefixo `whatsapp.pipeline.`.

- [ ] **Step 4: Atualizar imports internos em `whatsapp/pipeline/profiling.py`**

Mesmo padrão: trocar imports bare para `whatsapp.pipeline.X`.

- [ ] **Step 5: Atualizar `whatsapp/pipeline/utils/` se houver imports cruzados**

Verificar se arquivos em utils/ importam de config ou outros módulos e atualizar.

- [ ] **Step 6: Remover `PATHS['src']` de `whatsapp/pipeline/config.py`**

O path `'src': PROJECT_ROOT / 'src'` aponta para diretório que não existe mais. Remover a linha:

```python
# REMOVER de PATHS dict:
'src': PROJECT_ROOT / 'src',
```

- [ ] **Step 7: Commit**

```bash
~/.claude/scripts/commit.sh "refactor: move src/ para whatsapp/pipeline/"
```

---

### Task 3: Mover cli/ → whatsapp/cli/

**Files:**
- Move: `cli/__init__.py` → `whatsapp/cli/__init__.py`
- Move: `cli/helpers.py` → `whatsapp/cli/helpers.py`
- Move: `cli/prepare.py` → `whatsapp/cli/prepare.py`
- Move: `cli/process.py` → `whatsapp/cli/process.py`
- Move: `cli/_status.py` → `whatsapp/cli/_status.py`
- Remove: `cli/__main__.py`, `cli/`

- [ ] **Step 1: Mover arquivos (usar git mv para preservar histórico)**

```bash
mkdir -p whatsapp/cli
git mv cli/__init__.py whatsapp/cli/__init__.py
git mv cli/helpers.py whatsapp/cli/helpers.py
git mv cli/prepare.py whatsapp/cli/prepare.py
git mv cli/process.py whatsapp/cli/process.py
git mv cli/_status.py whatsapp/cli/_status.py

# __main__.py do cli/ não é mais necessário (whatsapp/__main__.py substitui)
git rm cli/__main__.py
```

- [ ] **Step 2: Atualizar `whatsapp/cli/__init__.py`**

Trocar todos `from cli.X` para `from whatsapp.cli.X`:

```python
from whatsapp.cli.prepare import prepare_app
from whatsapp.cli.process import process_app
from whatsapp.cli._status import run_status
```

E dentro do comando `run()`:
```python
from whatsapp.cli.helpers import require_config
from whatsapp.cli.prepare import _run_clean, _run_wrangle, _run_transcribe
from whatsapp.cli.process import _load_and_run_script, SENTIMENT_SCRIPTS, EMBEDDINGS_SCRIPTS
```

- [ ] **Step 3: Atualizar `whatsapp/cli/helpers.py`**

Remover o hack de sys.path inteiro (linhas 3-4, 11-14) e trocar o import:

```python
# REMOVER:
import os
import sys
_src_dir = str(Path(__file__).parent.parent / "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

# TROCAR em load_config():
# De: from config import PATHS, PROJECT_ROOT
# Para:
from whatsapp.pipeline.config import PATHS, PROJECT_ROOT
```

Também remover `import os` (não usado).

- [ ] **Step 4: Atualizar `whatsapp/cli/prepare.py`**

Trocar todos os imports:
- `from cli.helpers import X` → `from whatsapp.cli.helpers import X`
- `from cleaning import X` → `from whatsapp.pipeline.cleaning import X`
- `from wrangling import X` → `from whatsapp.pipeline.wrangling import X`

- [ ] **Step 5: Atualizar `whatsapp/cli/process.py`**

Trocar:
- `from cli.helpers import X` → `from whatsapp.cli.helpers import X`
- Remover `from pathlib import Path` (import não usado)

- [ ] **Step 6: Atualizar `whatsapp/cli/_status.py`**

Trocar:
- `from cli.helpers import load_config` → `from whatsapp.cli.helpers import load_config`

- [ ] **Step 7: Commit**

```bash
~/.claude/scripts/commit.sh "refactor: move cli/ para whatsapp/cli/"
```

---

## Chunk 2: Atualizar consumidores externos

### Task 4: Atualizar pyproject.toml

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Atualizar pyproject.toml**

```toml
[project]
name = "whatsapp-interaction-analysis"
version = "0.1.0"
description = "End-to-end data science pipeline for WhatsApp conversation analysis"
requires-python = ">=3.11"

[project.scripts]
whatsapp-interaction = "whatsapp.cli:app"

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
include = ["whatsapp*"]
```

- [ ] **Step 2: Instalar em modo editável e testar entry point**

```bash
pip install -e .
whatsapp-interaction --help
```

Expected: help text com prepare, process, status, run.

- [ ] **Step 3: Testar python -m whatsapp**

```bash
python -m whatsapp --help
```

Expected: mesmo output.

- [ ] **Step 4: Commit**

```bash
~/.claude/scripts/commit.sh "fix: corrige entry point e package discovery no pyproject.toml"
```

---

### Task 5: Atualizar testes

**Files:**
- Modify: `tests/test_cleaning.py`
- Modify: `tests/test_wrangling.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Atualizar `tests/test_cleaning.py`**

Remover o hack de sys.path e trocar imports:

```python
# REMOVER:
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# TROCAR:
# De: from cleaning import (...)
# Para:
from whatsapp.pipeline.cleaning import (
    remove_u200e,
    remove_empty_lines,
    normalize_whitespace,
    anonymize_participants,
    optimize_timestamps,
    normalize_indentation,
    # ... resto dos imports
)
```

- [ ] **Step 2: Atualizar `tests/test_wrangling.py`**

Mesmo padrão:

```python
# REMOVER sys.path hack

# TROCAR:
# De: from wrangling import (...)
# Para:
from whatsapp.pipeline.wrangling import (
    parse_to_dataframe,
    classify_message_type,
    # ... resto dos imports
)
```

- [ ] **Step 3: Atualizar `tests/test_cli.py`**

```python
# REMOVER:
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# TROCAR:
# De: from cli import app / from cli.helpers import validate_steps
# Para:
from whatsapp.cli import app
from whatsapp.cli.helpers import validate_steps
```

- [ ] **Step 4: Rodar testes**

```bash
pytest tests/ -v
```

Expected: 75 testes passando.

- [ ] **Step 5: Commit**

```bash
~/.claude/scripts/commit.sh "refactor: atualiza imports dos testes para pacote whatsapp/"
```

---

### Task 6: Atualizar scripts standalone

**Files:**
- Modify: todos os `scripts/*.py` que fazem `sys.path.insert(0, str(PROJECT_ROOT / 'src'))`

Lista completa (12 arquivos):
- `scripts/sentiment_ensemble.py`
- `scripts/sentiment_distilbert.py`
- `scripts/sentiment_deberta.py`
- `scripts/sentiment_twitter_roberta.py`
- `scripts/sentiment_analysis.py`
- `scripts/generate_embeddings.py`
- `scripts/generate_embeddings_minilm.py`
- `scripts/generate_embeddings_distiluse.py`
- `scripts/compare_embeddings_models.py`
- `scripts/compare_embedding_dimensions.py`
- `scripts/migrate_sentiment_columns.py`
- `scripts/remove_alias_columns.py`

- [ ] **Step 1: Em cada script, remover sys.path hack e trocar import**

Padrão a aplicar em todos:

```python
# REMOVER:
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

# TROCAR:
# De: from config import PATHS
# Para:
from whatsapp.pipeline.config import PATHS
```

Nota: `PROJECT_ROOT = Path(__file__).parent.parent` pode continuar — é usado para localizar scripts, não para imports.

- [ ] **Step 2: Verificar se algum script importa outros módulos de src/**

Procurar por `from wrangling import`, `from cleaning import`, etc. e atualizar.

- [ ] **Step 3: Testar um script representativo**

```bash
python scripts/generate_sample_data.py --help 2>/dev/null || python scripts/generate_sample_data.py
```

- [ ] **Step 4: Commit**

```bash
~/.claude/scripts/commit.sh "refactor: atualiza imports dos scripts para pacote whatsapp/"
```

---

### Task 7: Atualizar CI

**Files:**
- Modify: `.github/workflows/tests.yml`

- [ ] **Step 1: Adicionar `pip install -e .` ao workflow**

```yaml
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest pandas python-dotenv "typer[all]"
          pip install -e .
```

- [ ] **Step 2: Commit**

```bash
~/.claude/scripts/commit.sh "fix: adiciona pip install -e . ao CI para resolver imports"
```

---

### Task 8: Atualizar documentação

**Files:**
- Modify: `README.md` (diagrama de estrutura)

- [ ] **Step 1: Atualizar diagrama de estrutura no README.md**

Trocar a seção de estrutura para refletir `whatsapp/` em vez de `cli/` e `src/`:

```
├── whatsapp/                          # Pacote principal
│   ├── __init__.py                    # Versão e metadata
│   ├── __main__.py                    # python -m whatsapp
│   ├── cli/                           # CLI (whatsapp-interaction)
│   │   ├── __init__.py                # App Typer + comandos raiz
│   │   ├── helpers.py                 # Helpers compartilhados
│   │   ├── prepare.py                 # Subcomandos prepare
│   │   ├── process.py                 # Subcomandos process
│   │   └── _status.py                # Comando status
│   └── pipeline/                      # Módulos do pipeline
│       ├── config.py                  # Configurações centralizadas
│       ├── cleaning.py                # Pipeline de limpeza
│       ├── wrangling.py               # Parsing e enriquecimento
│       ├── profiling.py               # Profiling de dados brutos
│       └── utils/                     # Utilitários
```

- [ ] **Step 2: Atualizar referência de instalação se existir**

Verificar se README menciona `python -m cli` e trocar para `python -m whatsapp` ou `whatsapp-interaction`.

- [ ] **Step 3: Commit**

```bash
~/.claude/scripts/commit.sh "docs: atualiza README com nova estrutura whatsapp/"
```

---

## Chunk 3: Verificação final

### Task 9: Verificação completa

- [ ] **Step 1: Confirmar que src/ e cli/ não existem mais**

```bash
ls -la src/ cli/ 2>&1
```

Expected: "No such file or directory" para ambos.

- [ ] **Step 2: Confirmar estrutura do pacote**

```bash
find whatsapp/ -name "*.py" | sort
```

Expected:
```
whatsapp/__init__.py
whatsapp/__main__.py
whatsapp/cli/__init__.py
whatsapp/cli/_status.py
whatsapp/cli/helpers.py
whatsapp/cli/prepare.py
whatsapp/cli/process.py
whatsapp/pipeline/__init__.py
whatsapp/pipeline/cleaning.py
whatsapp/pipeline/config.py
whatsapp/pipeline/profiling.py
whatsapp/pipeline/utils/__init__.py
whatsapp/pipeline/utils/audit.py
whatsapp/pipeline/utils/dataframe_helpers.py
whatsapp/pipeline/utils/file_helpers.py
whatsapp/pipeline/utils/text_helpers.py
whatsapp/pipeline/wrangling.py
```

- [ ] **Step 3: Rodar suite completa de testes**

```bash
pytest tests/ -v
```

Expected: 75 testes passando.

- [ ] **Step 4: Testar CLI via entry point**

```bash
whatsapp-interaction --help
whatsapp-interaction prepare --help
whatsapp-interaction process --help
whatsapp-interaction status
```

Expected: todos respondem sem erro.

- [ ] **Step 5: Verificar que nenhum sys.path hack restou**

```bash
grep -r "sys.path.insert" --include="*.py" .
```

Expected: zero resultados (exceto possivelmente em scripts/transcribe_media.py que precisa ser verificado).

- [ ] **Step 6: Verificar que nenhum import bare restou**

```bash
grep -rn "from config import\|from cleaning import\|from wrangling import\|from profiling import\|from utils import" --include="*.py" . | grep -v whatsapp
```

Expected: zero resultados.

- [ ] **Step 7: Commit final se houver ajustes**

```bash
~/.claude/scripts/commit.sh "chore: verificacao final da reorganizacao"
```
