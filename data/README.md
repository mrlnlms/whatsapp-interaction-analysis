# 📁 /data

Esta pasta contém os dados do projeto. **Não é versionada** por conter informações pessoais.

------------------------------------------------------------------------

## Estrutura esperada

```         
data/
│
├── raw/                         # Exports brutos do WhatsApp
│   ├── export_2024-10/          # Por período de export
│   │   ├── raw-data.txt         # Arquivo de texto exportado
│   │   └── media/               # Arquivos de mídia (se incluídos)
│   │       ├── 00001-AUDIO-2024-10-15.opus
│   │       ├── 00002-PHOTO-2024-10-16.jpg
│   │       └── ...
│   │
│   └── export_2024-11/          # Novo export
│       ├── raw-data.txt
│       └── media/
│
├── interim/                     # Arquivos intermediários (por execução)
│   ├── export_2024-10/
│   │   ├── cln1.txt             # Após remoção U+200E
│   │   ├── cln2.txt             # Após timestamps vazios
│   │   └── ...
│   └── export_2024-11/
│
├── processed/                   # DataFrames finais (por execução)
│   ├── export_2024-10/
│   │   └── df_final.csv
│   └── export_2024-11/
│       └── df_final.csv
│
└── integrated/                  # Base consolidada (merge de todos)
    └── df_master.csv
```

------------------------------------------------------------------------

## Como obter os dados

### 1. Exportar conversa do WhatsApp

1.  Abra a conversa no WhatsApp
2.  Toque em **⋮** (menu) → **Mais** → **Exportar conversa**
3.  Escolha **Incluir mídia** (se quiser transcrever áudios)
4.  Salve o arquivo `.zip`

### 2. Organizar no projeto

``` bash
# Extraia o zip
unzip "WhatsApp Chat.zip" -d data/raw/export_2024-11/

# Renomeie o arquivo principal (se necessário)
mv "data/raw/export_2024-11/_chat.txt" "data/raw/export_2024-11/raw-data.txt"
```

### 3. Executar o pipeline

``` bash
# Ajuste o path no config.py ou passe como parâmetro
quarto render notebooks/01-data-preparation.qmd
```

------------------------------------------------------------------------

## Nomenclatura sugerida

| Pasta          | Formato          | Exemplo          |
|----------------|------------------|------------------|
| Export         | `export_YYYY-MM` | `export_2024-11` |
| Arquivo raw    | `raw-data.txt`   | —                |
| CSV processado | `df_final.csv`   | —                |
| CSV integrado  | `df_master.csv`  | —                |

------------------------------------------------------------------------

## Integração de múltiplos exports

Quando tiver mais de um export processado:

``` python
import pandas as pd
from pathlib import Path

# Lista todos os CSVs processados
processed_dir = Path('data/processed')
dfs = []

for export_dir in processed_dir.glob('export_*'):
    csv_path = export_dir / 'df_final.csv'
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        df['source_export'] = export_dir.name  # Marca origem
        dfs.append(df)

# Concatena e remove duplicatas (por timestamp + remetente)
df_master = pd.concat(dfs, ignore_index=True)
df_master = df_master.drop_duplicates(subset=['timestamp', 'remetente', 'conteudo'])
df_master = df_master.sort_values('timestamp').reset_index(drop=True)

# Salva base integrada
df_master.to_csv('data/integrated/df_master.csv', index=False)
```

------------------------------------------------------------------------

## ⚠️ Lembrete de privacidade

Esta pasta contém **dados pessoais**. Certifique-se de que:

-   [ ] Não está sendo versionada (verificar `.gitignore`)
-   [ ] Nomes foram anonimizados (P1, P2)
-   [ ] Não compartilhar publicamente