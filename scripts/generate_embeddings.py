"""
Generate Embeddings - Representação Semântica de Mensagens

Gera embeddings (vetores semânticos) para todas as mensagens usando
Sentence Transformers (paraphrase-multilingual-mpnet-base-v2).

Embeddings capturam o SIGNIFICADO das mensagens, permitindo:
- Busca semântica
- Clustering
- Topic modeling
- Análise de similaridade
- Visualizações

Uso:
    python scripts/generate_embeddings.py

Input:  data/processed/messages_with_models.parquet
Output: data/processed/message_embeddings.npy (arquivo separado, ~180 MB)
        data/processed/embeddings_metadata.json
        data/processed/messages_with_models.parquet (atualizado com features derivadas)

Features adicionadas ao parquet:
    - similaridade_anterior (float): similaridade com mensagem anterior
    - densidade_local (float): distância média aos 10 vizinhos mais próximos

Embeddings salvos separadamente:
    - message_embeddings.npy: array (n_mensagens, 384)
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
MODEL_NAME = 'paraphrase-multilingual-mpnet-base-v2'
EMBEDDING_DIM = 768 # Dimensionalidade nativa do modelo base
BATCH_SIZE = 100  # Ajuste baseado na memória disponível

# ========== FUNÇÕES ==========

def verificar_instalacao():
    """Verifica se sentence-transformers está instalado"""
    try:
        import sentence_transformers
        print(f"✅ sentence-transformers {sentence_transformers.__version__}")
        return True
    except ImportError:
        print("\n❌ Biblioteca 'sentence-transformers' não encontrada!")
        print("\n📦 Instale com:")
        print("   pip install sentence-transformers")
        return False

def carregar_modelo():
    """Carrega modelo de embeddings"""
    from sentence_transformers import SentenceTransformer
    import torch
    
    print(f"\n📦 Carregando modelo: {MODEL_NAME}")
    print("   (Primeira vez: ~420 MB de download)")
    
    # Detecta device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"   Device: {device}")
    
    if device == 'cuda':
        print("   🚀 GPU detectada! Processamento será mais rápido.")
    else:
        print("   💻 CPU mode. Tempo estimado: 10-15 minutos.")
    
    # Carrega modelo
    model = SentenceTransformer(MODEL_NAME, device=device)
    
    print(f"✅ Modelo carregado!")
    print(f"   Dimensões: {EMBEDDING_DIM}")
    
    return model, device

def gerar_embeddings(model, textos, batch_size=BATCH_SIZE):
    """
    Gera embeddings para lista de textos
    
    Args:
        model: SentenceTransformer
        textos: Lista de strings
        batch_size: Tamanho do batch para processamento
    
    Returns:
        numpy array (n_textos, 384)
    """
    print(f"\n🧠 Gerando embeddings...")
    print(f"   Mensagens: {len(textos):,}")
    print(f"   Batch size: {batch_size}")
    
    # Encode com progress bar
    embeddings = model.encode(
        textos,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True  # Normaliza para cosine similarity
    )
    
    print(f"✅ Embeddings gerados!")
    print(f"   Shape: {embeddings.shape}")
    print(f"   Dtype: {embeddings.dtype}")
    print(f"   Tamanho: {embeddings.nbytes / 1024 / 1024:.2f} MB")
    
    return embeddings

def calcular_features_derivadas(embeddings, df):
    """
    Calcula features derivadas dos embeddings
    
    Features:
    - similaridade_anterior: similaridade com mensagem anterior
    - densidade_local: distância média aos 10 vizinhos mais próximos
    """
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.neighbors import NearestNeighbors
    
    print("\n📊 Calculando features derivadas...")
    
    # 1. Similaridade com mensagem anterior
    print("   1/2 Similaridade com anterior...")
    df['similaridade_anterior'] = 0.0
    
    for i in tqdm(range(1, len(embeddings)), desc="      Processando"):
        sim = cosine_similarity(
            embeddings[i].reshape(1, -1),
            embeddings[i-1].reshape(1, -1)
        )[0][0]
        df.iloc[i, df.columns.get_loc('similaridade_anterior')] = sim
    
    print(f"      ✅ Similaridade média com anterior: {df['similaridade_anterior'].mean():.3f}")
    
    # 2. Densidade local (distância média aos 10 vizinhos)
    print("   2/2 Densidade local (10-NN)...")
    knn = NearestNeighbors(n_neighbors=11, metric='cosine')  # 11 porque inclui a própria
    knn.fit(embeddings)
    
    distances, _ = knn.kneighbors(embeddings)
    
    # Remove primeira coluna (distância para si mesmo = 0)
    distances = distances[:, 1:]
    
    # Média das distâncias
    df['densidade_local'] = distances.mean(axis=1)
    
    print(f"      ✅ Densidade local média: {df['densidade_local'].mean():.3f}")
    
    print("✅ Features derivadas calculadas!")
    
    return df

def salvar_embeddings(embeddings, output_path):
    """Salva embeddings em formato .npy (otimizado)"""
    print(f"\n💾 Salvando embeddings: {output_path.name}")
    np.save(output_path, embeddings)
    
    tamanho_mb = output_path.stat().st_size / 1024 / 1024
    print(f"   {tamanho_mb:.2f} MB")
    
    return tamanho_mb

def salvar_metadata(metadata, output_path):
    """Salva metadados em JSON"""
    print(f"\n📋 Salvando metadata: {output_path.name}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Metadata salvo")

def exibir_resumo(df, embeddings, tempo_total):
    """Exibe resumo do processamento"""
    print("\n" + "="*80)
    print("📊 RESUMO")
    print("="*80)
    
    print(f"\n✅ Mensagens processadas: {len(embeddings):,}")
    print(f"\n📈 Estatísticas dos embeddings:")
    print(f"   Shape:  {embeddings.shape}")
    print(f"   Média:  {embeddings.mean():.4f}")
    print(f"   Std:    {embeddings.std():.4f}")
    print(f"   Min:    {embeddings.min():.4f}")
    print(f"   Max:    {embeddings.max():.4f}")
    
    print(f"\n📊 Features derivadas:")
    print(f"   Similaridade anterior:")
    print(f"      Média: {df['similaridade_anterior'].mean():.3f}")
    print(f"      Mediana: {df['similaridade_anterior'].median():.3f}")
    print(f"      Std: {df['similaridade_anterior'].std():.3f}")
    
    print(f"\n   Densidade local:")
    print(f"      Média: {df['densidade_local'].mean():.3f}")
    print(f"      Mediana: {df['densidade_local'].median():.3f}")
    print(f"      Std: {df['densidade_local'].std():.3f}")
    
    print(f"\n⏱️  Tempo total: {tempo_total/60:.2f} minutos")
    print(f"   Velocidade: {len(embeddings)/(tempo_total):.1f} mensagens/segundo")

def main():
    print("="*80)
    print("🧠 GENERATE EMBEDDINGS")
    print("="*80)
    
    inicio_total = time.time()
    
    # Verifica instalação
    if not verificar_instalacao():
        return
    
    # Caminhos
    input_file = PATHS['processed'] / 'messages_with_models.parquet'
    embeddings_file = PATHS['processed'] / 'message_embeddings.npy'
    metadata_file = PATHS['processed'] / 'embeddings_metadata.json'
    
    # Verifica se já existe
    if embeddings_file.exists():
        print(f"\n⚠️  Arquivo de embeddings já existe: {embeddings_file.name}")
        resposta = input("   Deseja sobrescrever? (s/n): ").lower()
        if resposta != 's':
            print("   ❌ Operação cancelada.")
            return
    
    # Verifica input
    if not input_file.exists():
        print(f"\n❌ Arquivo não encontrado: {input_file}")
        print("   Execute os scripts de sentiment primeiro.")
        return
    
    print(f"\n📂 Input: {input_file.name}")
    
    # Carrega dados
    print(f"\n📦 Carregando dataset...")
    df = pd.read_parquet(input_file)
    print(f"   {len(df):,} mensagens | {len(df.columns)} colunas")
    
    # Filtra mensagens válidas (com conteúdo)
    print(f"\n🔍 Filtrando mensagens válidas...")
    mask_valido = df['conteudo'].notna() & (df['conteudo'].str.strip() != '')
    df_valido = df[mask_valido].copy()
    
    total_processar = len(df_valido)
    total_pular = len(df) - total_processar
    
    print(f"   Processar: {total_processar:,}")
    print(f"   Pular: {total_pular:,}")
    
    if total_processar == 0:
        print("\n❌ Nenhuma mensagem válida para processar!")
        return
    
    # Carrega modelo
    model, device = carregar_modelo()
    
    # Prepara textos
    textos = df_valido['conteudo'].tolist()
    
    # Gera embeddings
    inicio_proc = time.time()
    embeddings = gerar_embeddings(model, textos, batch_size=BATCH_SIZE)
    tempo_proc = time.time() - inicio_proc
    
    # Features derivadas
    df_valido = calcular_features_derivadas(embeddings, df_valido)
    
    # Atualiza DataFrame original
    df.loc[mask_valido, 'similaridade_anterior'] = df_valido['similaridade_anterior'].values
    df.loc[mask_valido, 'densidade_local'] = df_valido['densidade_local'].values
    
    # Salva embeddings
    tamanho_mb = salvar_embeddings(embeddings, embeddings_file)
    
    # Salva DataFrame atualizado
    print(f"\n💾 Atualizando dataset: {input_file.name}")
    df.to_parquet(input_file, index=False)
    print(f"   ✅ Dataset atualizado com features derivadas")
    
    # Tempo total
    tempo_total = time.time() - inicio_total
    
    # Metadata
    metadata = {
        'timestamp_execucao': pd.Timestamp.now().isoformat(),
        'modelo': MODEL_NAME,
        'dimensoes': EMBEDDING_DIM,
        'device': device,
        'batch_size': BATCH_SIZE,
        'mensagens_total': len(df),
        'mensagens_processadas': total_processar,
        'mensagens_puladas': total_pular,
        'tempo_processamento_segundos': round(tempo_proc, 2),
        'tempo_processamento_minutos': round(tempo_proc / 60, 2),
        'tempo_total_segundos': round(tempo_total, 2),
        'tempo_total_minutos': round(tempo_total / 60, 2),
        'mensagens_por_segundo': round(total_processar / tempo_proc, 1),
        'tamanho_mb': round(tamanho_mb, 2),
        'embeddings_shape': list(embeddings.shape),
        'embeddings_stats': {
            'mean': float(embeddings.mean()),
            'std': float(embeddings.std()),
            'min': float(embeddings.min()),
            'max': float(embeddings.max()),
        },
        'features_derivadas': {
            'similaridade_anterior': {
                'mean': float(df['similaridade_anterior'].mean()),
                'median': float(df['similaridade_anterior'].median()),
                'std': float(df['similaridade_anterior'].std()),
            },
            'densidade_local': {
                'mean': float(df['densidade_local'].mean()),
                'median': float(df['densidade_local'].median()),
                'std': float(df['densidade_local'].std()),
            }
        }
    }
    
    salvar_metadata(metadata, metadata_file)
    
    # Resumo
    exibir_resumo(df_valido, embeddings, tempo_total)
    
    print("\n" + "="*80)
    print("🎉 EMBEDDINGS GERADOS COM SUCESSO!")
    print("="*80)
    
    print(f"\n📁 Arquivos gerados:")
    print(f"   1. {embeddings_file.name} (~{tamanho_mb:.0f} MB)")
    print(f"   2. {metadata_file.name}")
    print(f"   3. {input_file.name} (atualizado)")
    
    print(f"\n💡 Como usar os embeddings:")
    print(f"   ```python")
    print(f"   import numpy as np")
    print(f"   embeddings = np.load('{embeddings_file}')")
    print(f"   print(embeddings.shape)  # ({total_processar}, {EMBEDDING_DIM})")
    print(f"   ```")
    
    print(f"\n🔮 Próximos passos:")
    print(f"   1. Renderizar: quarto render notebooks/04f-embeddings.qmd")
    print(f"   2. Clustering: python scripts/generate_clusters.py")
    print(f"   3. Topic Modeling: python scripts/generate_topics.py")
    print(f"   4. Visualização: Usar UMAP/t-SNE no EDA")

if __name__ == '__main__':
    main()