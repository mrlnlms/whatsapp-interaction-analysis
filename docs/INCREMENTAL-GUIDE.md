# Guia de Processamento Incremental

> Como rodar o pipeline com um novo export sem reprocessar dados antigos.

## 📋 Contexto

Processos custosos que queremos evitar re-executar:

| Processo                   | Tempo       | Arquivo de Cache      |
|----------------------------|-------------|-----------------------|
| Transcrição (Groq/Whisper) | \~40 min    | `transcriptions.csv`  |
| Sentimento (BERT)          | \~30-60 min | `sentiment_cache.csv` |

------------------------------------------------------------------------

## 🔄 Fluxo para Novo Export

### 1. Baixar novo export do WhatsApp

```         
Configurações → Conversas → Exportar conversa → Anexar mídia
```

Salvar em:

```         
data/raw/export_2024-10_2025-11/    ← Nova pasta com novo período
├── _chat.txt
└── media/
    └── (arquivos de mídia)
```

### 2. Atualizar `.env`

``` properties
DATA_FOLDER=export_2024-10_2025-11   # ← Novo período
```

### 3. Copiar caches do export anterior

``` bash
# Define pastas
OLD_EXPORT="data/processed/export_2024-10_2025-10"
NEW_EXPORT="data/processed/export_2024-10_2025-11"

# Cria pasta se não existir
mkdir -p $NEW_EXPORT

# Copia caches (se existirem)
cp $OLD_EXPORT/transcriptions.csv $NEW_EXPORT/ 2>/dev/null || echo "Sem cache de transcrição"
cp $OLD_EXPORT/sentiment_cache.csv $NEW_EXPORT/ 2>/dev/null || echo "Sem cache de sentimento"
```

### 4. Rodar pipeline

``` bash
# 1. Transcrição (só processa mídias novas)
python scripts/transcribe_media.py

# 2. Pipeline completo
quarto render notebooks/01-data-cleaning.qmd
quarto render notebooks/02-data-wrangling.qmd
quarto render notebooks/04-feature-engineering.qmd  # BERT usa cache aqui
quarto render notebooks/05-eda-overview.qmd
```

------------------------------------------------------------------------

## 🧠 Como funciona o cache

### Transcrição (`transcriptions.csv`)

**Chave:** `filename` (nome do arquivo de mídia)

```         
00000789-AUDIO-2025-08-28-13-48-53.opus → "Eu acho que talvez..."
```

-   Se filename existe no CSV → pula
-   Se filename não existe → transcreve e adiciona

### Sentimento (`sentiment_cache.csv`)

**Chave:** `message_hash` (hash de timestamp + remetente + conteúdo)

``` python
hash = hashlib.md5(f"{timestamp}|{remetente}|{conteudo}".encode()).hexdigest()
```

```         
a1b2c3d4e5f6... → {"label": "positive", "score": 0.92}
```

-   Se hash existe no CSV → usa valor cacheado
-   Se hash não existe → processa BERT e adiciona

------------------------------------------------------------------------

## 📁 Estrutura de Arquivos

```         
data/processed/
├── export_2024-10_2025-10/          # Export antigo
│   ├── messages.csv
│   ├── messages.parquet
│   ├── transcriptions.csv           # Cache de transcrição
│   └── sentiment_cache.csv          # Cache de sentimento
│
└── export_2024-10_2025-11/          # Export novo
    ├── messages.csv
    ├── messages.parquet
    ├── transcriptions.csv           # ← Copiado + novos
    └── sentiment_cache.csv          # ← Copiado + novos
```

------------------------------------------------------------------------

## ⚠️ Cuidados

1.  **Não renomear arquivos de mídia** — o cache usa filename como chave
2.  **Manter mesmo fuso horário** — afeta o hash das mensagens
3.  **Copiar caches ANTES de rodar** — senão reprocessa tudo

------------------------------------------------------------------------

## 🚀 Script de Migração (opcional)

Se quiser automatizar, crie `scripts/migrate_caches.py`:

``` python
#!/usr/bin/env python3
"""Copia caches de um export anterior para o novo."""

import shutil
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(os.getenv('PROJECT_ROOT', '.'))
DATA_FOLDER = os.getenv('DATA_FOLDER')

# Detecta export anterior (você pode ajustar isso)
PREVIOUS_FOLDER = 'export_2024-10_2025-10'

old_dir = PROJECT_ROOT / 'data' / 'processed' / PREVIOUS_FOLDER
new_dir = PROJECT_ROOT / 'data' / 'processed' / DATA_FOLDER

new_dir.mkdir(parents=True, exist_ok=True)

caches = ['transcriptions.csv', 'sentiment_cache.csv']

for cache in caches:
    old_file = old_dir / cache
    new_file = new_dir / cache
    
    if old_file.exists() and not new_file.exists():
        shutil.copy(old_file, new_file)
        print(f"✅ Copiado: {cache}")
    elif new_file.exists():
        print(f"⏭️  Já existe: {cache}")
    else:
        print(f"⚠️  Não encontrado: {cache}")

print("\n✅ Migração concluída!")
```

------------------------------------------------------------------------

## 📊 Estimativa de Tempo

| Cenário                                    | Transcrição | BERT     | Total   |
|-----------------|------------------------|----------------|----------------|
| **Primeiro export** (92K msgs, 700 mídias) | \~40 min    | \~45 min | \~1h30  |
| **Novo export** (+2K msgs, +50 mídias)     | \~3 min     | \~2 min  | \~5 min |

O cache faz MUITA diferença! 🚀