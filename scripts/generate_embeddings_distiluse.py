"""
Generate Embeddings - DistilUSE (512 dimensões)

Modelo: distiluse-base-multilingual-cased-v2
- Dimensões: 512
- Velocidade: Balanceada
- Qualidade: Muito boa
- Tamanho: ~500 MB

Características:
- Meio termo entre MPNet e MiniLM
- Universal Sentence Encoder destilado
- Bom para casos gerais

Uso:
    python scripts/generate_embeddings_distiluse.py

Output: 
    data/processed/message_embeddings_distiluse.npy
    data/processed/embeddings_distiluse_metadata.json
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import time
import json
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# ========== CONFIGURAÇÕES ==========
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from config import PATHS  # noqa: E402

# Modelo de embeddings
MODEL_NAME = 'distiluse-base-multilingual-cased-v2'
MODEL_NICKNAME = 'distiluse'
EMBEDDING_DIM = 512  # Esperado
BATCH_SIZE = 100

# ========== FUNÇÕES ==========
# [MESMAS FUNÇÕES DO SCRIPT ANTERIOR - COPIAR TUDO]
# Muda apenas: MODEL_NAME, MODEL_NICKNAME, EMBEDDING_DIM

def verificar_instalacao():
    """Verifica se sentence-transformers está instalado"""
    try:
        import sentence_transformers
        print(f"✅ sentence-transformers {sentence_transformers.__version__}")
        return True
    except ImportError:
        print("\n❌ Biblioteca 'sentence-transformers' não encontrada!")
        return False

def carregar_modelo():
    """Carrega modelo de embeddings"""
    from sentence_transformers import SentenceTransformer
    import torch
    
    print(f"\n📦 Carregando modelo: {MODEL_NAME}")
    print("   (Primeira vez: ~500 MB de download)")
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"   Device: {device}")
    
    if device == 'cuda':
        print("   🚀 GPU detectada!")
    else:
        print("   💻 CPU mode. Tempo estimado: ~6-8 minutos.")
    
    model = SentenceTransformer(MODEL_NAME, device=device)
    actual_dim = model.get_sentence_embedding_dimension()
    
    print(f"✅ Modelo carregado!")
    print(f"   Dimensões: {actual_dim}")
    
    if actual_dim != EMBEDDING_DIM:
        print(f"   ⚠️  Esperado: {EMBEDDING_DIM}, Obtido: {actual_dim}")
    
    return model, device, actual_dim

def gerar_embeddings(model, textos, batch_size=BATCH_SIZE):
    """Gera embeddings para lista de textos"""
    print(f"\n🧠 Gerando embeddings...")
    print(f"   Mensagens: {len(textos):,}")
    print(f"   Batch size: {batch_size}")
    
    embeddings = model.encode(
        textos,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    
    print(f"✅ Embeddings gerados!")
    print(f"   Shape: {embeddings.shape}")
    print(f"   Tamanho: {embeddings.nbytes / 1024 / 1024:.2f} MB")
    
    return embeddings

def calcular_features_derivadas(embeddings, df):
    """Calcula features derivadas"""
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.neighbors import NearestNeighbors
    
    print("\n📊 Calculando features derivadas...")
    
    # Similaridade anterior
    print("   1/2 Similaridade com anterior...")
    df[f'similaridade_anterior_{MODEL_NICKNAME}'] = 0.0
    
    for i in tqdm(range(1, len(embeddings)), desc="      Processando"):
        sim = cosine_similarity(
            embeddings[i].reshape(1, -1),
            embeddings[i-1].reshape(1, -1)
        )[0][0]
        df.iloc[i, df.columns.get_loc(f'similaridade_anterior_{MODEL_NICKNAME}')] = sim
    
    print(f"      ✅ Similaridade média: {df[f'similaridade_anterior_{MODEL_NICKNAME}'].mean():.3f}")
    
    # Densidade local
    print("   2/2 Densidade local...")
    knn = NearestNeighbors(n_neighbors=11, metric='cosine')
    knn.fit(embeddings)
    distances, _ = knn.kneighbors(embeddings)
    df[f'densidade_local_{MODEL_NICKNAME}'] = distances[:, 1:].mean(axis=1)
    
    print(f"      ✅ Densidade local média: {df[f'densidade_local_{MODEL_NICKNAME}'].mean():.3f}")
    
    return df

def salvar_embeddings(embeddings, output_path):
    """Salva embeddings"""
    print(f"\n💾 Salvando: {output_path.name}")
    np.save(output_path, embeddings)
    tamanho_mb = output_path.stat().st_size / 1024 / 1024
    print(f"   {tamanho_mb:.2f} MB")
    return tamanho_mb

def salvar_metadata(metadata, output_path):
    """Salva metadata"""
    print(f"\n📋 Salvando metadata: {output_path.name}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

def exibir_resumo(embeddings, tempo_total):
    """Resumo"""
    print("\n" + "="*80)
    print("📊 RESUMO")
    print("="*80)
    print(f"\n✅ Mensagens: {len(embeddings):,}")
    print(f"   Shape: {embeddings.shape}")
    print(f"⏱️  Tempo: {tempo_total/60:.2f} min")
    print(f"   Velocidade: {len(embeddings)/tempo_total:.1f} msgs/s")

def main():
    print("="*80)
    print(f"🧠 GENERATE EMBEDDINGS - {MODEL_NAME}")
    print("="*80)
    
    inicio_total = time.time()
    
    if not verificar_instalacao():
        return
    
    # Caminhos
    input_file = PATHS['processed'] / 'messages_with_models.parquet'
    embeddings_file = PATHS['processed'] / f'message_embeddings_{MODEL_NICKNAME}.npy'
    metadata_file = PATHS['processed'] / f'embeddings_{MODEL_NICKNAME}_metadata.json'
    
    if embeddings_file.exists():
        print(f"\n⚠️  Arquivo já existe: {embeddings_file.name}")
        resposta = input("   Sobrescrever? (s/n): ").lower()
        if resposta != 's':
            return
    
    print(f"\n📦 Carregando dataset...")
    df = pd.read_parquet(input_file)
    
    mask_valido = df['conteudo'].notna() & (df['conteudo'].str.strip() != '')
    df_valido = df[mask_valido].copy()
    
    print(f"   Processar: {len(df_valido):,}")
    
    model, device, actual_dim = carregar_modelo()
    textos = df_valido['conteudo'].tolist()
    
    inicio_proc = time.time()
    embeddings = gerar_embeddings(model, textos)
    tempo_proc = time.time() - inicio_proc
    
    df_valido = calcular_features_derivadas(embeddings, df_valido)
    
    df.loc[mask_valido, f'similaridade_anterior_{MODEL_NICKNAME}'] = df_valido[f'similaridade_anterior_{MODEL_NICKNAME}'].values
    df.loc[mask_valido, f'densidade_local_{MODEL_NICKNAME}'] = df_valido[f'densidade_local_{MODEL_NICKNAME}'].values
    
    tamanho_mb = salvar_embeddings(embeddings, embeddings_file)
    
    df.to_parquet(input_file, index=False)
    
    tempo_total = time.time() - inicio_total
    
    metadata = {
        'timestamp_execucao': pd.Timestamp.now().isoformat(),
        'modelo': MODEL_NAME,
        'modelo_nickname': MODEL_NICKNAME,
        'dimensoes': actual_dim,
        'device': device,
        'mensagens_processadas': len(embeddings),
        'tempo_total_minutos': round(tempo_total / 60, 2),
        'tamanho_mb': round(tamanho_mb, 2),
    }
    
    salvar_metadata(metadata, metadata_file)
    exibir_resumo(embeddings, tempo_total)
    
    print("\n" + "="*80)
    print("🎉 EMBEDDINGS DISTILUSE GERADOS!")
    print("="*80)
    print(f"\n🔮 Próximo: python scripts/compare_embeddings_models.py")

if __name__ == '__main__':
    main()