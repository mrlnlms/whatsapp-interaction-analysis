"""
Remove Colunas Alias de Sentimento

Remove as colunas alias (sentimento_label, sentimento_score) mantendo apenas
as colunas específicas de cada modelo (sentimento_roberta_*, sentimento_distilbert_*).

Uso:
    python scripts/remove_alias_columns.py

Colunas removidas:
    - sentimento_label (alias de sentimento_roberta_label)
    - sentimento_score (alias de sentimento_roberta_score)

Colunas mantidas:
    - sentimento_roberta_label
    - sentimento_roberta_score
    - sentimento_distilbert_label
    - sentimento_distilbert_score
    - ... todas as outras
"""

import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from config import PATHS

def remove_alias_columns():
    print("="*80)
    print("🧹 REMOÇÃO DE COLUNAS ALIAS")
    print("="*80)
    
    # Arquivo
    file_path = PATHS['processed'] / 'messages_with_models.parquet'
    
    if not file_path.exists():
        print("\n❌ Arquivo não encontrado!")
        print(f"   {file_path}")
        return
    
    # Carrega
    print(f"\n📂 Carregando: {file_path.name}")
    df = pd.read_parquet(file_path)
    print(f"   {len(df):,} linhas | {len(df.columns)} colunas")
    
    # Verifica se tem as colunas alias
    alias_columns = ['sentimento_label', 'sentimento_score']
    found_aliases = [col for col in alias_columns if col in df.columns]
    
    if not found_aliases:
        print("\n✅ Nenhuma coluna alias encontrada!")
        print("   Nada a remover.")
        return
    
    print(f"\n🔍 Colunas alias encontradas: {found_aliases}")
    
    # Verifica se tem as colunas específicas (segurança)
    specific_columns = [
        'sentimento_roberta_label',
        'sentimento_roberta_score',
        'sentimento_distilbert_label',
        'sentimento_distilbert_score'
    ]
    
    found_specific = [col for col in specific_columns if col in df.columns]
    
    if not found_specific:
        print("\n⚠️  AVISO: Nenhuma coluna específica de modelo encontrada!")
        print("   Isso pode indicar que algo deu errado.")
        print("   Abortando por segurança.")
        return
    
    print(f"\n✅ Colunas específicas encontradas: {found_specific}")
    
    # Verifica se valores batem (validação)
    if 'sentimento_label' in df.columns and 'sentimento_roberta_label' in df.columns:
        mask = df['sentimento_label'].notna() & df['sentimento_roberta_label'].notna()
        if mask.any():
            iguais = (df.loc[mask, 'sentimento_label'] == df.loc[mask, 'sentimento_roberta_label']).all()
            if iguais:
                print("\n✅ Validação: Alias = RoBERTa (valores idênticos)")
            else:
                print("\n⚠️  AVISO: Alias ≠ RoBERTa (valores diferentes!)")
                print("   Recomendo verificar manualmente antes de remover.")
                resposta = input("   Continuar mesmo assim? (s/n): ")
                if resposta.lower() != 's':
                    print("\n❌ Operação cancelada.")
                    return
    
    # Backup
    backup_path = PATHS['processed'] / 'messages_with_models_backup_before_alias_removal.parquet'
    print(f"\n💾 Criando backup: {backup_path.name}")
    df.to_parquet(backup_path, index=False)
    
    # Remove colunas alias
    print(f"\n🗑️  Removendo colunas: {found_aliases}")
    df_cleaned = df.drop(columns=found_aliases)
    
    # Salva
    print(f"\n💾 Salvando arquivo limpo: {file_path.name}")
    df_cleaned.to_parquet(file_path, index=False)
    
    size_mb = file_path.stat().st_size / 1024 / 1024
    print(f"   Tamanho: {size_mb:.2f} MB")
    print(f"   Colunas: {len(df.columns)} → {len(df_cleaned.columns)}")
    
    print("\n" + "="*80)
    print("🎉 REMOÇÃO CONCLUÍDA!")
    print("="*80)
    
    print("\n📊 Resumo:")
    print(f"   ✅ Backup criado: {backup_path.name}")
    print(f"   ✅ Colunas removidas: {len(found_aliases)}")
    print(f"   ✅ Colunas restantes: {len(df_cleaned.columns)}")
    
    print("\n📋 Colunas de sentimento mantidas:")
    sentiment_cols = [col for col in df_cleaned.columns if 'sentimento' in col]
    for col in sorted(sentiment_cols):
        print(f"   - {col}")
    
    print("\n💡 Se precisar desfazer:")
    print(f"   Restaure o backup: {backup_path.name}")

if __name__ == '__main__':
    remove_alias_columns()