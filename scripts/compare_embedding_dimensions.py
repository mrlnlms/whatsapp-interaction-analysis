"""
Comparação de Dimensionalidades de Embeddings

Gera embeddings com diferentes dimensionalidades e compara:
- Qualidade de similaridade semântica
- Velocidade de processamento
- Tamanho de arquivo
- Performance em clustering

Dimensões testadas: 768 (original), 384, 256, 128
"""

from pathlib import Path
import pandas as pd
import numpy as np
import time
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from whatsapp.pipeline.config import PATHS

PROJECT_ROOT = Path(__file__).parent.parent

# Dimensionalidades para testar
DIMENSIONS = [768, 384, 256, 128]

def carregar_embeddings_originais():
    """Carrega embeddings 768d originais"""
    print("📦 Carregando embeddings originais (768d)...")
    embeddings = np.load(PATHS['processed'] / 'message_embeddings.npy')
    print(f"   Shape: {embeddings.shape}")
    return embeddings

def reduzir_dimensionalidade(embeddings_768, target_dim):
    """Reduz dimensionalidade usando PCA"""
    print(f"\n🔧 Reduzindo para {target_dim} dimensões...")
    
    inicio = time.time()
    pca = PCA(n_components=target_dim, random_state=42)
    embeddings_reduced = pca.fit_transform(embeddings_768)
    tempo = time.time() - inicio
    
    variance = pca.explained_variance_ratio_.sum()
    
    print(f"   ✅ Redução completa em {tempo:.2f}s")
    print(f"   Variância explicada: {variance*100:.1f}%")
    
    return embeddings_reduced, variance, tempo

def testar_qualidade_similaridade(embeddings, df, n_samples=1000):
    """Testa qualidade de similaridade semântica"""
    print(f"\n🧪 Testando qualidade de similaridade...")
    
    # Amostra aleatória
    indices = np.random.choice(len(embeddings), n_samples, replace=False)
    sample_emb = embeddings[indices]
    
    # Calcula similaridades
    inicio = time.time()
    similarities = cosine_similarity(sample_emb)
    tempo = time.time() - inicio
    
    # Remove diagonal
    np.fill_diagonal(similarities, 0)
    
    stats = {
        'mean': similarities.mean(),
        'std': similarities.std(),
        'min': similarities.min(),
        'max': similarities.max(),
        'tempo_ms': tempo * 1000
    }
    
    print(f"   Média: {stats['mean']:.3f}")
    print(f"   Std: {stats['std']:.3f}")
    print(f"   Tempo: {stats['tempo_ms']:.2f}ms")
    
    return stats

def comparar_dimensionalidades():
    """Compara todas as dimensionalidades"""
    print("="*80)
    print("📐 COMPARAÇÃO DE DIMENSIONALIDADES")
    print("="*80)
    
    # Carrega originais
    embeddings_768 = carregar_embeddings_originais()
    df = pd.read_parquet(PATHS['processed'] / 'messages_with_models.parquet')
    
    # Resultados
    results = []
    
    # 768d (original)
    print("\n" + "="*80)
    print("📊 DIMENSIONALIDADE: 768 (Original)")
    print("="*80)
    
    tamanho_mb = embeddings_768.nbytes / 1024 / 1024
    qual_sim = testar_qualidade_similaridade(embeddings_768, df)
    
    results.append({
        'dimensoes': 768,
        'variancia_explicada': 1.0,
        'tamanho_mb': tamanho_mb,
        'tempo_reducao_s': 0.0,
        'similaridade_media': qual_sim['mean'],
        'similaridade_std': qual_sim['std'],
        'tempo_similaridade_ms': qual_sim['tempo_ms']
    })
    
    # Outras dimensões
    for dim in [384, 256, 128]:
        print("\n" + "="*80)
        print(f"📊 DIMENSIONALIDADE: {dim}")
        print("="*80)
        
        # Reduz
        emb_reduced, variance, tempo_red = reduzir_dimensionalidade(embeddings_768, dim)
        
        # Tamanho
        tamanho_mb = emb_reduced.nbytes / 1024 / 1024
        print(f"   Tamanho: {tamanho_mb:.2f} MB")
        
        # Qualidade
        qual_sim = testar_qualidade_similaridade(emb_reduced, df)
        
        results.append({
            'dimensoes': dim,
            'variancia_explicada': variance,
            'tamanho_mb': tamanho_mb,
            'tempo_reducao_s': tempo_red,
            'similaridade_media': qual_sim['mean'],
            'similaridade_std': qual_sim['std'],
            'tempo_similaridade_ms': qual_sim['tempo_ms']
        })
    
    # Resumo comparativo
    print("\n" + "="*80)
    print("📊 RESUMO COMPARATIVO")
    print("="*80)
    
    df_results = pd.DataFrame(results)
    
    print("\n### Tabela Completa\n")
    print(df_results.to_string(index=False))
    
    # Análise
    print("\n### 🎯 Análise\n")
    
    # Perda de qualidade
    base_sim = df_results.iloc[0]['similaridade_media']
    for _, row in df_results.iterrows():
        if row['dimensoes'] != 768:
            perda = (base_sim - row['similaridade_media']) / base_sim * 100
            ganho_espaco = (1 - row['tamanho_mb'] / df_results.iloc[0]['tamanho_mb']) * 100
            
            print(f"\n**{int(row['dimensoes'])} dims:**")
            print(f"  Variância capturada: {row['variancia_explicada']*100:.1f}%")
            print(f"  Perda de qualidade: {perda:.2f}%")
            print(f"  Ganho de espaço: {ganho_espaco:.1f}%")
            print(f"  Speedup: {df_results.iloc[0]['tempo_similaridade_ms'] / row['tempo_similaridade_ms']:.2f}x")
    
    # Salva resultados
    output_file = PATHS['processed'] / 'embeddings_dimensionality_comparison.json'
    df_results.to_json(output_file, orient='records', indent=2)
    print(f"\n💾 Resultados salvos: {output_file.name}")
    
    return df_results

if __name__ == '__main__':
    results = comparar_dimensionalidades()