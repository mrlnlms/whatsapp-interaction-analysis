"""
Migração: Adiciona Sufixo às Colunas de Sentimento

Renomeia as colunas de sentimento existentes para incluir sufixo do modelo,
mantendo aliases para retrocompatibilidade.

Uso:
    python scripts/migrate_sentiment_columns.py

Antes:
    sentimento_label, sentimento_score

Depois:
    sentimento_roberta_label, sentimento_roberta_score  (original com sufixo)
    sentimento_label, sentimento_score                   (aliases mantidos)
"""

import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from config import PATHS

def migrate_columns():
    print("="*80)
    print("🔄 MIGRAÇÃO DE COLUNAS DE SENTIMENTO")
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
    
    # Verifica se já tem as colunas antigas
    if 'sentimento_label' not in df.columns:
        print("\n⚠️  Coluna 'sentimento_label' não encontrada.")
        print("   Migração não necessária ou já foi executada.")
        return
    
    # Verifica se já migrou
    if 'sentimento_roberta_label' in df.columns:
        print("\n✅ Colunas já estão migradas!")
        print("   Nada a fazer.")
        return
    
    print("\n🔄 Aplicando migração...")
    
    # Cria colunas com sufixo (cópias)
    df['sentimento_roberta_label'] = df['sentimento_label']
    df['sentimento_roberta_score'] = df['sentimento_score']
    
    print("   ✅ Criadas colunas com sufixo:")
    print("      - sentimento_roberta_label")
    print("      - sentimento_roberta_score")
    print("\n   ✅ Mantidas colunas originais (aliases):")
    print("      - sentimento_label")
    print("      - sentimento_score")
    
    # Reorganiza ordem das colunas (sufixadas primeiro)
    cols = df.columns.tolist()
    
    # Remove as 4 colunas de sentimento
    for col in ['sentimento_roberta_label', 'sentimento_roberta_score', 
                'sentimento_label', 'sentimento_score']:
        if col in cols:
            cols.remove(col)
    
    # Adiciona na ordem desejada no final
    new_order = cols + [
        'sentimento_roberta_label',
        'sentimento_roberta_score',
        'sentimento_label',
        'sentimento_score'
    ]
    
    df = df[new_order]
    
    # Backup
    backup_path = PATHS['processed'] / 'messages_with_models_backup.parquet'
    print(f"\n💾 Criando backup: {backup_path.name}")
    df.to_parquet(backup_path, index=False)
    
    # Salva
    print(f"\n💾 Salvando arquivo atualizado: {file_path.name}")
    df.to_parquet(file_path, index=False)
    
    size_mb = file_path.stat().st_size / 1024 / 1024
    print(f"   Tamanho: {size_mb:.2f} MB")
    
    # Atualiza metadata também
    metadata_file = PATHS['processed'] / 'sentiment_metadata.json'
    if metadata_file.exists():
        import json
        
        print(f"\n📝 Atualizando metadata...")
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Adiciona nota sobre migração
        metadata['migrated'] = True
        metadata['migration_date'] = pd.Timestamp.now().isoformat()
        metadata['columns_created'] = [
            'sentimento_roberta_label',
            'sentimento_roberta_score'
        ]
        metadata['aliases_maintained'] = [
            'sentimento_label',
            'sentimento_score'
        ]
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print("   ✅ Metadata atualizado")
    
    print("\n" + "="*80)
    print("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*80)
    
    print("\n📊 Resumo:")
    print("   ✅ Backup criado")
    print("   ✅ Colunas renomeadas com sufixo '_roberta'")
    print("   ✅ Aliases mantidos para compatibilidade")
    print("   ✅ Metadata atualizado")
    
    print("\n💡 Próximo passo:")
    print("   Execute o novo modelo: python scripts/sentiment_distilbert.py")

if __name__ == '__main__':
    migrate_columns()