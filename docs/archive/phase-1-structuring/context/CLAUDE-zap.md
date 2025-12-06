# WhatsApp DS Analytics - Guia Completo para Desenvolvimento

> **Versão:** 1.0  
> **Última atualização:** 2025-11-30  
> **Autor:** Marlon L.

Este documento é a **referência única e completa** para desenvolvimento no projeto WhatsApp DS Analytics. Leia-o integralmente antes de fazer qualquer modificação no código.

---

## 📋 Índice

1. [Visão Geral do Projeto](#visão-geral-do-projeto)
2. [Estrutura de Diretórios](#estrutura-de-diretórios)
3. [Configuração e Setup](#configuração-e-setup)
4. [Arquitetura do Pipeline](#arquitetura-do-pipeline)
5. [Padrões de Código Python](#padrões-de-código-python)
6. [Padrões de Código Quarto](#padrões-de-código-quarto)
7. [Convenções de Nomenclatura](#convenções-de-nomenclatura)
8. [Formatação e Apresentação](#formatação-e-apresentação)
9. [Documentação e Comentários](#documentação-e-comentários)
10. [Git e Versionamento](#git-e-versionamento)
11. [Regras Específicas por Módulo](#regras-específicas-por-módulo)
12. [Checklist de Qualidade](#checklist-de-qualidade)

---

## 📖 Visão Geral do Projeto

### Propósito
Pipeline de Data Science para análise de conversas exportadas do WhatsApp. Transforma arquivo TXT bruto em dataset estruturado e enriquecido com features de NLP, sentimento, clustering e visualizações interativas.

### Tecnologias Core
- **Python 3.11+** - Processamento de dados
- **Quarto** - Literate Programming e documentação reproduzível
- **Pandas/NumPy** - Manipulação de dados
- **Plotly** - Visualizações interativas
- **scikit-learn** - Machine Learning (clustering, PCA, MCA)
- **Transformers** - Sentiment Analysis (BERT)
- **Groq API** - Transcrição de áudio/vídeo (Whisper)

### Filosofia do Projeto
1. **Reprodutibilidade** - Todo processo deve ser documentado e replicável
2. **Modularidade** - Cada etapa é independente e reutilizável
3. **Auditabilidade** - Todas as transformações são rastreadas
4. **Profissionalismo** - Código limpo, documentado e versionado

---

## 📁 Estrutura de Diretórios

```
whatsapp-ds-analytics/
│
├── .env                          # Variáveis de ambiente (NÃO versionar)
├── .gitignore                    # Exclusões do Git
├── README.md                     # Documentação do projeto
├── CLAUDE.md                     # Este arquivo
├── requirements.txt              # Dependências Python
├── _quarto.yml                   # Configuração Quarto
│
├── data/
│   ├── raw/                      # Arquivo TXT original do WhatsApp
│   ├── interim/                  # Arquivos intermediários (cleaning)
│   ├── processed/                # Datasets finais (CSV, Parquet)
│   └── media/                    # Arquivos de áudio/vídeo/imagem
│
├── src/
│   ├── __init__.py
│   ├── config.py                 # Configurações centralizadas
│   ├── cleaning.py               # Pipeline de limpeza
│   ├── wrangling.py              # Pipeline de wrangling
│   ├── profiling.py              # Funções de profiling
│   ├── feature_engineering.py    # Criação de features
│   └── utils/
│       ├── __init__.py
│       ├── file_helpers.py       # Utilitários de arquivo
│       ├── dataframe_helpers.py  # Utilitários de DataFrame
│       └── visualization.py      # Utilitários de visualização
│
├── notebooks/
│   ├── 00-data-profiling.qmd
│   ├── 01-data-cleaning.qmd
│   ├── 02-data-wrangling.qmd
│   ├── 03-feature-engineering.qmd
│   ├── 04-eda.qmd
│   └── 05-advanced-analysis.qmd
│
├── scripts/
│   ├── transcribe_media.py       # Script de transcrição
│   └── setup_env.sh              # Setup do ambiente
│
└── assets/
    └── images/                   # Imagens para documentação
```

---

## ⚙️ Configuração e Setup

### .env (NÃO VERSIONAR)

```bash
# Caminhos
PROJECT_ROOT=/home/usuario/whatsapp-ds-analytics
DATA_FOLDER=data_bday  # Nome da pasta de dados

# APIs
GROQ_API_KEY=sua_chave_aqui
```

### src/config.py - Configuração Centralizada

**PRINCÍPIO FUNDAMENTAL:** Todos os paths e configurações devem estar centralizados aqui. NUNCA hardcode paths em notebooks ou módulos.

```python
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Paths absolutos
PROJECT_ROOT = Path(os.getenv('PROJECT_ROOT'))
DATA_FOLDER = os.getenv('DATA_FOLDER', 'data')

PATHS = {
    'raw': PROJECT_ROOT / DATA_FOLDER / 'raw' / '_chat.txt',
    'interim': PROJECT_ROOT / DATA_FOLDER / 'interim',
    'processed': PROJECT_ROOT / DATA_FOLDER / 'processed',
    'media': PROJECT_ROOT / DATA_FOLDER / 'media',
}
```

### Setup padrão em notebooks

**SEMPRE** usar este bloco no início de cada .qmd:

```python
#| label: setup
#| code-fold: false

import sys
import os
from dotenv import load_dotenv
from pathlib import Path

# Carrega .env e adiciona src ao path
load_dotenv()
sys.path.insert(0, os.getenv('PROJECT_ROOT') + '/src')

from config import PROJECT_ROOT, PATHS
```

**NUNCA** usar:
```python
# ❌ ERRADO - path relativo
sys.path.append('../src')

# ❌ ERRADO - hardcoded
DATA_DIR = '/home/marlon/projeto/data'
```

---

## 🔧 Arquitetura do Pipeline

### Estrutura de Pipeline Modular

Todos os pipelines seguem o padrão:

```python
# Definição de etapas
STEPS = {
    'step_id': {
        'name': 'Nome da Etapa',
        'description': 'Descrição detalhada',
        'function': funcao_transformacao,
    }
}

# Função de execução
def run_pipeline(order, input_file, output_dir, **kwargs):
    """
    order: lista de step_ids na ordem desejada
    input_file: arquivo de entrada
    output_dir: diretório de saída
    """
    result = {
        'outputs': {},      # Arquivos gerados
        'audits': {},       # Metadados de cada etapa
        'metrics': {},      # Métricas específicas
        'df_audit': None,   # DataFrame consolidado
        'totals': {},       # Totais acumulados
    }
    
    # Executa etapas em sequência
    # Cada etapa recebe input, retorna output
    # Audits são coletados automaticamente
    
    return result
```

### Auditoria Obrigatória

**TODA** transformação de arquivo deve registrar:

```python
audit = {
    'step_id': 'nome_etapa',
    'input': {
        'path': input_file,
        'size': tamanho_bytes,
        'size_formatted': '5.2 MB',
        'total_lines': numero_linhas,
        'total_chars': numero_caracteres,
    },
    'output': {
        # mesmo formato
    },
    'delta_bytes': diferenca,
    'delta_percent': percentual,
}
```

---

## 🐍 Padrões de Código Python

### Imports

```python
# 1. Bibliotecas padrão
import os
import sys
from pathlib import Path
from datetime import datetime

# 2. Bibliotecas externas
import pandas as pd
import numpy as np
import plotly.express as px

# 3. Módulos locais
from config import PROJECT_ROOT, PATHS
from utils import funcao_helper
```

### Docstrings

```python
def funcao_exemplo(param1: str, param2: int) -> dict:
    """
    Descrição breve da função.
    
    Descrição detalhada do que a função faz, como usa os parâmetros,
    e o que retorna. Incluir edge cases se necessário.
    
    Args:
        param1: Descrição do parâmetro
        param2: Descrição do parâmetro
        
    Returns:
        dict: Dicionário com estrutura:
            {
                'chave1': descrição,
                'chave2': descrição,
            }
            
    Example:
        >>> resultado = funcao_exemplo('teste', 42)
        >>> print(resultado['chave1'])
    """
    pass
```

### Type Hints

```python
# ✅ SEMPRE usar type hints
def processar_arquivo(path: Path, encoding: str = 'utf-8') -> pd.DataFrame:
    pass

# ❌ NUNCA omitir
def processar_arquivo(path, encoding='utf-8'):
    pass
```

### Nomenclatura Python

```python
# Variáveis e funções: snake_case
total_linhas = 100
def calcular_metricas():
    pass

# Classes: PascalCase
class DataProcessor:
    pass

# Constantes: UPPER_SNAKE_CASE
MAX_ITERATIONS = 1000
CLEANING_STEPS = {...}
```

---

## 📝 Padrões de Código Quarto

### Estrutura de Chunk

```python
```{python}
#| label: nome-descritivo-com-hifens
#| echo: false          # SEMPRE false para produção
#| output: false        # Se não quer mostrar resultado
#| code-fold: false     # Se quer mostrar código (raro)

# Código aqui
```
```

### Labels obrigatórios

```python
#| label: setup           # Bloco de setup inicial
#| label: load-data       # Carregamento de dados
#| label: compute-metrics # Computação de métricas
#| label: show-results    # Exibição de resultados
#| label: export          # Exportação
```

### ❌ NUNCA USAR: print() para apresentar dados

**ERRADO:**
```python
```{python}
#| echo: false

print(f"Total de linhas: {total:,}")
print(f"Redução: {reducao:.2f}%")
```
```

**CORRETO:**
```markdown
```{python}
#| label: compute-totals
#| output: false
#| echo: false

# Computa valores silenciosamente
total = calcular_total()
reducao = calcular_reducao()
```

Total de linhas: `{python} f"{total:,}"`  
Redução: `{python} f"{reducao:.2f}%"`
```

### Inline Code

```markdown
# Formatação numérica
Valor: `{python} f"{valor:,.2f}"`        # 1,234.56
Porcentagem: `{python} f"{pct:.1f}%"`    # 12.3%
Inteiro: `{python} f"{num:,}"`           # 1,234

# Strings
Nome: `{python} arquivo.name`
Path: `{python} str(caminho)`

# Booleanos
Status: `{python} 'Sim' if condicao else 'Não'`
```

### Tabelas

```python
# ✅ CORRETO - Pandas Styler
```{python}
#| echo: false

df_resultado.style.hide(axis='index')
```

# ❌ ERRADO - print(df)
```{python}
print(df_resultado)
```
```

---

## 🎨 Formatação e Apresentação

### Callouts (Blocos de Destaque)

```markdown
# Nota informativa
::: {.callout-note}
## Título opcional
Conteúdo da nota
:::

# Dica útil
::: {.callout-tip icon="false"}
## 💡 Título com emoji
Conteúdo da dica
:::

# Aviso importante
::: {.callout-warning}
### Decisão de Pipeline
Esta transformação remove X porque Y
:::

# Informação técnica
::: {.callout-note appearance="simple"}
### 📋 Regex para parsing
```python
pattern = r'^(\d{2}/\d{2}/\d{2})'
```
:::
```

### Accordions (Details/Summary)

```markdown
<details style="margin: 0.5em 0; list-style: none; border: 1px solid #d4d4d4; border-radius: 5px; padding: 10px;">
<summary style="font-size: 1.3em; font-weight: 600; color: #343a40; list-style: none;">
▸ Título do Accordion
</summary>

Conteúdo que será expandido/colapsado

</details>
```

### Tabs (Panel Tabset)

```markdown
::: panel-tabset
## Tab 1
Conteúdo do primeiro tab

## Tab 2  
Conteúdo do segundo tab
:::
```

### Hierarquia de Headers

```markdown
# Título Principal (H1) - Apenas 1 por documento

## Seção Principal (H2)

### Subseção (H3)

#### Detalhe (H4) - Usar apenas quando necessário
```

### Emojis e Ícones

```markdown
# Emojis padronizados do projeto
📊 Dados/Estatísticas
📁 Arquivo
📂 Diretório
🔧 Configuração
✅ Sucesso/Completo
❌ Erro/Incorreto
⚠️ Aviso
💡 Dica/Insight
🎯 Objetivo/Resultado
📈 Crescimento/Aumento
📉 Redução/Diminuição
🎬 Mídia
🎙️ Áudio/Transcrição
💾 Exportação
🔍 Análise/Investigação
```

---

## 📐 Convenções de Nomenclatura

### Arquivos e Diretórios

```bash
# Notebooks Quarto: número-nome-descritivo.qmd
00-data-profiling.qmd
01-data-cleaning.qmd
02-data-wrangling.qmd

# Módulos Python: snake_case.py
cleaning.py
feature_engineering.py
dataframe_helpers.py

# Arquivos de dados: nome_descritivo.extensão
raw-data.txt                    # Original
raw-data_cln1.txt              # Após etapa 1
raw-data_cln7.txt              # Após etapa 7
messages.csv                    # Dataset principal
messages_full.csv               # Dataset completo
corpus_full.txt                 # Corpus para NLP
```

### Variáveis em Python

```python
# DataFrames: df_ ou nome descritivo
df = pd.read_csv(...)           # DataFrame principal
df_audit = criar_auditoria()    # DataFrame de auditoria
df_stats = calcular_stats()     # DataFrame de estatísticas

# Paths: sempre Path object, nunca string
RAW_FILE = PATHS['raw']         # ✅
raw_file = 'data/raw.txt'       # ❌

# Configurações: UPPER_SNAKE_CASE
PIPELINE_ORDER = [...]
CLEANING_STEPS = {...}

# Resultados temporários: snake_case
total_linhas = len(df)
arquivo_nome = path.name
```

### Colunas de DataFrame

```python
# Snake_case para colunas
df.columns = [
    'timestamp',              # Datetime
    'remetente',              # Categorical
    'tipo_mensagem',          # Categorical
    'conteudo',               # String
    'conteudo_enriquecido',   # String
    'tem_transcricao',        # Boolean
    'is_synthetic',           # Boolean
]

# Prefixos úteis
tem_*      # Booleanos (tem_emoji, tem_link)
is_*       # Booleanos (is_synthetic, is_multiline)
tipo_*     # Categorias (tipo_mensagem, tipo_arquivo)
qtd_*      # Contadores (qtd_palavras, qtd_emojis)
```

---

## 📚 Documentação e Comentários

### Comentários em Python

```python
# ✅ BOM - Explica o PORQUÊ
# Remove U+200E pois não carrega informação semântica
# e representa ~4.6% do tamanho do arquivo
text = text.replace('\u200e', '')

# ❌ RUIM - Repete o código
# Remove U+200E
text = text.replace('\u200e', '')

# ✅ BOM - Documenta decisão técnica
# Usamos lazy=False para garantir que todas as linhas
# sejam carregadas em memória antes do processamento,
# evitando inconsistências em operações que precisam
# do contexto completo
df = pd.read_csv(file, lazy=False)

# Seções principais
# =============================================================================
# CONFIGURAÇÃO DO PIPELINE
# =============================================================================

# Subseções
# --- Carregamento de dados ---

# TODOs
# TODO: Implementar validação de encoding
# FIXME: Bug ao processar mensagens com emoji no nome
# HACK: Solução temporária até refatorar módulo X
```

### Markdown em Quarto

```markdown
<!-- Comentários HTML invisíveis no render -->
<!-- TODO: Adicionar gráfico de série temporal -->

> **Nota:** Use blockquotes para destacar informações importantes

**Negrito** para termos chave
*Itálico* para ênfase sutil
`código` para valores literais

---  <!-- Separador horizontal -->
```

---

## 🔀 Git e Versionamento

### .gitignore

```bash
# Dados sensíveis (NUNCA versionar)
.env
data/
*.csv
*.txt
*.parquet

# Ambiente Python
venv/
__pycache__/
*.pyc
.ipynb_checkpoints/

# Quarto
.quarto/
*_files/
*.html

# IDEs
.vscode/
.idea/
```

### Mensagens de Commit

```bash
# Formato: tipo(escopo): descrição

# Tipos:
feat: Nova funcionalidade
fix: Correção de bug
docs: Documentação
style: Formatação (não afeta código)
refactor: Refatoração
test: Testes
chore: Manutenção

# Exemplos:
feat(cleaning): adiciona etapa de remoção de U+200E
fix(wrangling): corrige parsing de mensagens multilinha
docs(readme): atualiza instruções de setup
refactor(profiling): modulariza funções de análise
style(qmd): padroniza formatação inline code
```

---

## 🧩 Regras Específicas por Módulo

### src/cleaning.py

```python
# OBRIGATÓRIO: Cada etapa deve retornar
def step_function(input_file: Path, output_file: Path) -> dict:
    """
    Returns:
        dict: {
            'metrics': {...},  # Métricas específicas da etapa
            'audit': {...},    # Auditoria padrão
        }
    """
    pass

# Naming: raw-data_cln{N}.txt
# onde N é o número da etapa (1-7)

# Ordem de execução SEMPRE registrada em PIPELINE_ORDER
```

### src/wrangling.py

```python
# Estrutura de retorno padrão
result = {
    'df': pd.DataFrame,           # DataFrame processado
    'outputs': dict,              # Paths dos arquivos gerados
    'stats': dict,                # Estatísticas do processamento
}

# Classificação de mensagens:
TIPOS_MENSAGEM = [
    'texto',
    'audio_omitted',
    'image_omitted', 
    'video_omitted',
    'audio_attached',
    'video_attached',
    # ...
]
```

### src/feature_engineering.py

```python
# Categorias de features
TEMPORAL_FEATURES = [...]    # ano, mes, dia_semana, periodo_dia
TEXT_FEATURES = [...]        # tamanho, tem_emoji, tem_link
CONVERSATION_FEATURES = [...] # tempo_desde_ultima, turno
MEDIA_FEATURES = [...]       # tipo_midia_simplificado

# SEMPRE retornar DataFrame com novas colunas
def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Adiciona features temporais ao DataFrame"""
    df = df.copy()  # ✅ Não modificar original
    # ... adicionar colunas
    return df
```

### notebooks/*.qmd

```markdown
---
title: "Título Descritivo"
subtitle: "Subtítulo explicativo"
author: "Marlon L."
date: today
---

# Setup (SEMPRE no início)
```{python}
#| label: setup
#| code-fold: false
# ... imports padrão
```

# Seções principais (H1)
## Subseções (H2)
### Detalhes (H3)

# Sempre terminar com "Próximos Passos"
```

---

## ✅ Checklist de Qualidade

Antes de commitar código, verificar:

### Python
- [ ] Imports organizados (padrão → externos → locais)
- [ ] Type hints em todas as funções
- [ ] Docstrings nas funções públicas
- [ ] Sem hardcoded paths (usar `config.py`)
- [ ] Funções < 50 linhas (quebrar se maior)
- [ ] Nomes descritivos (não `temp`, `x`, `data2`)

### Quarto
- [ ] Bloco `setup` no início
- [ ] `#| echo: false` em chunks de produção
- [ ] ZERO `print()` para apresentação
- [ ] Inline code com formatação (`f"{valor:,.2f}"`)
- [ ] Tabelas com `.style.hide(axis='index')`
- [ ] Callouts bem formatados
- [ ] Emojis padronizados

### Documentação
- [ ] README atualizado se mudou estrutura
- [ ] CLAUDE.md atualizado se mudou padrões
- [ ] Comentários explicam PORQUÊ, não O QUÊ
- [ ] TODOs documentados com contexto

### Git
- [ ] .env não versionado
- [ ] Dados não versionados
- [ ] Commit message descritivo
- [ ] Sem arquivos temporários

---

## 🚨 Erros Comuns a Evitar

```python
# ❌ Path relativo
sys.path.append('../src')

# ✅ Path absoluto via .env
sys.path.insert(0, os.getenv('PROJECT_ROOT') + '/src')

# ❌ Hardcoded
df = pd.read_csv('/home/marlon/data/messages.csv')

# ✅ Config centralizado
df = pd.read_csv(PATHS['processed'] / 'messages.csv')

# ❌ Print para apresentação
print(f"Total: {total}")

# ✅ Markdown + inline
Total: `{python} total`

# ❌ DataFrame sem estilo
df.head()

# ✅ DataFrame com estilo
df.head().style.hide(axis='index')

# ❌ Modificar DataFrame original
def add_feature(df):
    df['nova_col'] = ...
    return df

# ✅ Copiar antes de modificar
def add_feature(df):
    df = df.copy()
    df['nova_col'] = ...
    return df
```

---

## 🎯 Princípios Fundamentais

1. **Um lugar para cada coisa**  
   Paths no `config.py`, funções nos módulos, análises nos notebooks

2. **DRY (Don't Repeat Yourself)**  
   Se escreveu 2x, vira função. Se usou em 2 notebooks, vira módulo

3. **Reprodutibilidade primeiro**  
   Código deve rodar em qualquer ambiente só ajustando `.env`

4. **Documentação é código**  
   Se não está documentado, não existe

5. **Auditoria sempre**  
   Toda transformação deve ser rastreável

6. **Apresentação profissional**  
   Quarto não é Jupyter. Use markdown, não print()

---

## 📞 Convenções de Comunicação no Código

```python
# Mensagens de progresso
print("🔄 Processando etapa 1/7...")
print("✅ Etapa concluída em 2.3s")
print("⚠️ Aviso: arquivo não encontrado")
print("❌ Erro: encoding inválido")

# Logs estruturados
logger.info("Pipeline iniciado")
logger.debug(f"Arquivo: {file.name}")
logger.warning("Transcription file not found, skipping")
logger.error(f"Failed to process: {e}")
```

---

## 🔄 Workflow de Desenvolvimento

1. **Criar branch** para nova feature
2. **Atualizar CLAUDE.md** se mudou padrões
3. **Desenvolver** seguindo este guia
4. **Testar** localmente
5. **Revisar** com checklist
6. **Commit** com mensagem descritiva
7. **Push** e criar PR (se em equipe)

---

## 📖 Referências e Recursos

- [Quarto Documentation](https://quarto.org/docs/)
- [Pandas Style Guide](https://pandas.pydata.org/docs/development/contributing_docstring.html)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**Este documento é vivo.** Sempre que estabelecer um novo padrão ou convenção, documente aqui imediatamente.

**Última revisão:** 2025-11-30 por Marlon L.