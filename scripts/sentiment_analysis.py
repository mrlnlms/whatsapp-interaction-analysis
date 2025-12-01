"""
Análise de Sentimento usando BERT

Aplica modelo BERT pré-treinado para classificar sentimento das mensagens.

Uso:
    python scripts/sentiment_analysis.py

Input:  data/processed/messages_enriched.parquet
Output: data/processed/messages_with_models.parquet
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Adiciona raiz do projeto ao path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from config import PATHS

# TODO: Importar suas libs de sentimento aqui
# from transformers import pipeline
# ou o que você já usa

def aplicar_sentimento(df):
    """
    Aplica análise de sentimento ao DataFrame
    
    TODO: Substituir por seu código real de sentimento
    """
    print("🤖 Aplicando modelo BERT...")
    
    # Seu código aqui
    # Por enquanto, placeholder:
    df['sentimento_label'] = None
    df['sentimento_score'] = None
    df['sentimento_positivo'] = None
    df['sentimento_neutro'] = None
    df['sentimento_negativo'] = None
    
    # TODO: Implementar chamada ao modelo
    
    return df

def main():
    # Caminhos
    input_file = PATHS['processed'] / 'messages_enriched.parquet'
    output_file = PATHS['processed'] / 'messages_with_models.parquet'
    
    print(f"📂 Carregando: {input_file}")
    df = pd.read_parquet(input_file)
    print(f"   {len(df):,} mensagens")
    
    # Aplica sentimento
    df = aplicar_sentimento(df)
    
    # Salva
    print(f"\n💾 Salvando: {output_file}")
    df.to_parquet(output_file, index=False)
    
    # Resumo
    print("\n✅ Concluído!")
    print(f"📊 Distribuição:")
    if df['sentimento_label'].notna().any():
        print(df['sentimento_label'].value_counts())
    else:
        print("   (Sentimento ainda não implementado)")

if __name__ == '__main__':
    main()
```

---

## Atualização dos Arquivos Seguintes

Agora os arquivos ficam:
```
01-data-profiling.qmd       # Perfil dos dados
02-data-cleaning.qmd        # Limpeza
03-feature-engineering.qmd  # Features estruturais
04-model-features.qmd       # Features de ML ← NOVO
05-eda.qmd                  # Análise exploratória (era 04)
06-advanced-analysis.qmd    # Análise avançada (era 05)