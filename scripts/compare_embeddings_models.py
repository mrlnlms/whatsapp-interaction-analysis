"""
Compare Embeddings Models

Compara 3 modelos de embeddings em múltiplas dimensões:

Modelos:
1. MPNet Base (768d) - Máxima qualidade
2. MiniLM (384d) - Velocidade e eficiência
3. DistilUSE (512d) - Balanceado

Métricas de Comparação:
1. Qualidade de Similaridade Semântica
   - Pares de teste conhecidos
   - Correlação de rankings
   
2. Performance em Clustering
   - Silhouette Score
   - Davies-Bouldin Index
   - Calinski-Harabasz Score

3. Eficiência
   - Velocidade de geração
   - Tamanho de arquivo
   - Dimensionalidade

4. Consistência
   - Correlação entre modelos
   - Concordância de rankings

Uso:
    python scripts/compare_embeddings_models.py

Output:
    data/processed/embeddings_comparison.json
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import json
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from scipy.stats import spearmanr
import time

# ========== CONFIGURAÇÕES ==========
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from config import PATHS  # noqa: E402

# Modelos a comparar
MODELS = {
    'mpnet': {
        'name': 'MPNet Base',
        'file': 'message_embeddings_mpnet.npy',
        'metadata': 'embeddings_mpnet_metadata.json',
        'dims': 768
    },
    'minilm': {
        'name': 'MiniLM',
        'file': 'message_embeddings_minilm.npy',
        'metadata': 'embeddings_minilm_metadata.json',
        'dims': 384
    },
    'distiluse': {
        'name': 'DistilUSE',
        'file': 'message_embeddings_distiluse.npy',
        'metadata': 'embeddings_distiluse_metadata.json',
        'dims': 512
    }
}

# Pares de teste para similaridade semântica
TEST_PAIRS = [
    # Pares SIMILARES (devem ter alta similaridade)
    ("Amo você", "Te amo muito", True),
    ("Vamos viajar?", "Que tal uma viagem?", True),
    ("Tô com fome", "Estou morrendo de fome", True),
    ("Boa noite", "Durma bem", True),
    ("Obrigado", "Muito obrigado", True),
    ("Como foi seu dia?", "Como você está?", True),
    ("Saudades", "Sentindo sua falta", True),
    ("Hahahaha", "Kkkkkk", True),
    
    # Pares DIFERENTES (devem ter baixa similaridade)
    ("Amo você", "Preciso comprar pão", False),
    ("Vamos viajar?", "Está chovendo", False),
    ("Boa noite", "Bom dia", False),
    ("Obrigado", "De nada", False),
    ("Saudades", "Até logo", False),
]

# ========== FUNÇÕES ==========

def carregar_embeddings_e_metadata():
    """Carrega todos os embeddings e metadados"""
    print("="*80)
    print("📦 CARREGANDO EMBEDDINGS E METADADOS")
    print("="*80)
    
    embeddings_data = {}
    
    for model_id, model_info in MODELS.items():
        print(f"\n📂 {model_info['name']}...")
        
        emb_file = PATHS['processed'] / model_info['file']
        meta_file = PATHS['processed'] / model_info['metadata']
        
        if not emb_file.exists():
            print(f"   ❌ Embeddings não encontrados: {emb_file.name}")
            print(f"   Execute: python scripts/generate_embeddings_{model_id}.py")
            continue
        
        if not meta_file.exists():
            print(f"   ⚠️  Metadata não encontrado: {meta_file.name}")
            metadata = {}
        else:
            with open(meta_file, 'r') as f:
                metadata = json.load(f)
        
        # Carrega embeddings
        embeddings = np.load(emb_file)
        
        print(f"   ✅ {embeddings.shape}")
        print(f"   📊 {embeddings.nbytes / 1024 / 1024:.2f} MB")
        
        embeddings_data[model_id] = {
            'embeddings': embeddings,
            'metadata': metadata,
            'info': model_info
        }
    
    if len(embeddings_data) < 2:
        print("\n❌ Necessário pelo menos 2 modelos para comparação!")
        return None
    
    print(f"\n✅ {len(embeddings_data)} modelos carregados!")
    return embeddings_data

def testar_similaridade_semantica(embeddings_data, df):
    """Testa qualidade de similaridade semântica"""
    print("\n" + "="*80)
    print("🧪 TESTE 1: SIMILARIDADE SEMÂNTICA")
    print("="*80)
    
    from sentence_transformers import SentenceTransformer
    
    # Carrega modelos para encodar pares de teste
    models_st = {}
    for model_id in embeddings_data.keys():
        if model_id == 'mpnet':
            models_st[model_id] = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
        elif model_id == 'minilm':
            models_st[model_id] = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        elif model_id == 'distiluse':
            models_st[model_id] = SentenceTransformer('distiluse-base-multilingual-cased-v2')
    
    results = {}
    
    for model_id, data in embeddings_data.items():
        print(f"\n📊 {data['info']['name']}...")
        
        model = models_st[model_id]
        
        # Encode pares de teste
        similar_scores = []
        different_scores = []
        
        for text1, text2, is_similar in TEST_PAIRS:
            emb1 = model.encode([text1], normalize_embeddings=True)[0]
            emb2 = model.encode([text2], normalize_embeddings=True)[0]
            
            sim = cosine_similarity([emb1], [emb2])[0][0]
            
            if is_similar:
                similar_scores.append(sim)
            else:
                different_scores.append(sim)
        
        mean_similar = np.mean(similar_scores)
        mean_different = np.mean(different_scores)
        separation = mean_similar - mean_different
        
        print(f"   Pares similares:   {mean_similar:.3f}")
        print(f"   Pares diferentes:  {mean_different:.3f}")
        print(f"   Separação:         {separation:.3f}")
        
        results[model_id] = {
            'mean_similar': float(mean_similar),
            'mean_different': float(mean_different),
            'separation': float(separation),
            'similar_scores': [float(s) for s in similar_scores],
            'different_scores': [float(s) for s in different_scores]
        }
    
    return results

def testar_clustering_quality(embeddings_data):
    """Testa qualidade de clustering"""
    print("\n" + "="*80)
    print("🧪 TESTE 2: QUALIDADE DE CLUSTERING")
    print("="*80)
    
    results = {}
    
    # Usa amostra para velocidade
    sample_size = min(10000, min([len(d['embeddings']) for d in embeddings_data.values()]))
    
    print(f"\n📊 Amostra: {sample_size:,} mensagens")
    print(f"   Clusters: K=10 (K-means)")
    
    for model_id, data in embeddings_data.items():
        print(f"\n📊 {data['info']['name']}...")
        
        embeddings = data['embeddings']
        
        # Amostra aleatória
        np.random.seed(42)
        indices = np.random.choice(len(embeddings), sample_size, replace=False)
        sample_emb = embeddings[indices]
        
        # K-means clustering
        print("   Clustering...")
        inicio = time.time()
        kmeans = KMeans(n_clusters=10, random_state=42, n_init=10)
        labels = kmeans.fit_predict(sample_emb)
        tempo = time.time() - inicio
        
        # Métricas
        print("   Calculando métricas...")
        silhouette = silhouette_score(sample_emb, labels, sample_size=min(5000, sample_size))
        davies_bouldin = davies_bouldin_score(sample_emb, labels)
        calinski = calinski_harabasz_score(sample_emb, labels)
        
        print(f"   ✅ Silhouette:       {silhouette:.3f}")
        print(f"   ✅ Davies-Bouldin:   {davies_bouldin:.3f}")
        print(f"   ✅ Calinski-Harabasz: {calinski:.1f}")
        print(f"   ⏱️  Tempo:            {tempo:.2f}s")
        
        results[model_id] = {
            'silhouette': float(silhouette),
            'davies_bouldin': float(davies_bouldin),
            'calinski_harabasz': float(calinski),
            'tempo_clustering': float(tempo)
        }
    
    return results

def testar_consistencia_entre_modelos(embeddings_data):
    """Testa consistência entre modelos"""
    print("\n" + "="*80)
    print("🧪 TESTE 3: CONSISTÊNCIA ENTRE MODELOS")
    print("="*80)
    
    # Usa amostra
    sample_size = min(5000, min([len(d['embeddings']) for d in embeddings_data.values()]))
    
    print(f"\n📊 Amostra: {sample_size:,} mensagens")
    
    # Pega mesma amostra para todos
    np.random.seed(42)
    indices = np.random.choice(
        min([len(d['embeddings']) for d in embeddings_data.values()]),
        sample_size,
        replace=False
    )
    
    # Calcula rankings de similaridade para cada modelo
    print("\n📊 Calculando rankings de similaridade...")
    
    rankings = {}
    
    for model_id, data in embeddings_data.items():
        print(f"   {data['info']['name']}...")
        
        sample_emb = data['embeddings'][indices]
        
        # Pega primeira mensagem como query
        query = sample_emb[0]
        
        # Calcula similaridade com todas
        similarities = cosine_similarity([query], sample_emb)[0]
        
        # Ranking (índices ordenados por similaridade)
        ranking = np.argsort(-similarities)
        
        rankings[model_id] = ranking
    
    # Calcula correlação de Spearman entre rankings
    print("\n📊 Correlação de rankings:")
    
    correlations = {}
    model_ids = list(rankings.keys())
    
    for i, model1 in enumerate(model_ids):
        for model2 in model_ids[i+1:]:
            corr, pval = spearmanr(rankings[model1], rankings[model2])
            
            name1 = embeddings_data[model1]['info']['name']
            name2 = embeddings_data[model2]['info']['name']
            
            print(f"   {name1} × {name2}: {corr:.3f}")
            
            correlations[f"{model1}_vs_{model2}"] = {
                'correlation': float(corr),
                'p_value': float(pval)
            }
    
    return correlations

def compilar_metricas_eficiencia(embeddings_data):
    """Compila métricas de eficiência dos metadados"""
    print("\n" + "="*80)
    print("📊 MÉTRICAS DE EFICIÊNCIA")
    print("="*80)
    
    results = {}
    
    for model_id, data in embeddings_data.items():
        metadata = data['metadata']
        
        print(f"\n📊 {data['info']['name']}:")
        print(f"   Dimensões:  {metadata.get('dimensoes', 'N/A')}")
        print(f"   Tempo:      {metadata.get('tempo_total_minutos', 'N/A'):.2f} min")
        velocidade = metadata.get('mensagens_por_segundo', None)
        if velocidade is not None:
            print(f"   Velocidade: {velocidade:.1f} msgs/s")
        else:
            print(f"   Velocidade: N/A")
        print(f"   Tamanho:    {metadata.get('tamanho_mb', 'N/A'):.2f} MB")
        
        results[model_id] = {
            'dimensoes': metadata.get('dimensoes', None),
            'tempo_minutos': metadata.get('tempo_total_minutos', None),
            'velocidade_msgs_s': metadata.get('mensagens_por_segundo', None),
            'tamanho_mb': metadata.get('tamanho_mb', None)
        }
    
    return results

def gerar_resumo_comparativo(all_results):
    """Gera tabela resumo comparativo"""
    print("\n" + "="*80)
    print("📊 RESUMO COMPARATIVO")
    print("="*80)
    
    # Tabela
    rows = []
    
    for model_id in all_results['eficiencia'].keys():
        model_name = MODELS[model_id]['name']
        efic = all_results['eficiencia'][model_id]
        sim = all_results['similaridade'][model_id]
        clust = all_results['clustering'][model_id]
        
        # Helper para formatar com checagem de None
        def fmt(valor, formato='.1f', default='N/A'):
            if valor is not None:
                return f"{valor:{formato}}"
            return default
        
        row = {
            'Modelo': model_name,
            'Dims': fmt(efic['dimensoes'], 'd', 'N/A'),
            'Tamanho (MB)': fmt(efic['tamanho_mb'], '.1f'),
            'Velocidade (msg/s)': fmt(efic['velocidade_msgs_s'], '.1f'),
            'Tempo (min)': fmt(efic['tempo_minutos'], '.1f'),
            'Separação Semântica': fmt(sim['separation'], '.3f'),
            'Silhouette': fmt(clust['silhouette'], '.3f'),
            'Davies-Bouldin': fmt(clust['davies_bouldin'], '.3f'),
        }
        
        rows.append(row)
    
    df_summary = pd.DataFrame(rows)
    
    print("\n")
    print(df_summary.to_string(index=False))
    
    return df_summary

def salvar_resultados(all_results, df_summary):
    """Salva resultados em JSON"""
    output_file = PATHS['processed'] / 'embeddings_comparison.json'
    
    print(f"\n💾 Salvando resultados: {output_file.name}")
    
    # Converte DataFrame para dict
    summary_dict = df_summary.to_dict(orient='records')
    
    final_results = {
        'timestamp': pd.Timestamp.now().isoformat(),
        'models_compared': list(MODELS.keys()),
        'summary_table': summary_dict,
        'detailed_results': all_results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Resultados salvos!")
    
    return output_file

def main():
    print("="*80)
    print("📐 COMPARAÇÃO DE MODELOS DE EMBEDDINGS")
    print("="*80)
    
    # Carrega dados
    embeddings_data = carregar_embeddings_e_metadata()
    
    if embeddings_data is None:
        return
    
    # Carrega dataset para testes
    df = pd.read_parquet(PATHS['processed'] / 'messages_with_models.parquet')
    
    # Testes
    results_similaridade = testar_similaridade_semantica(embeddings_data, df)
    results_clustering = testar_clustering_quality(embeddings_data)
    results_consistencia = testar_consistencia_entre_modelos(embeddings_data)
    results_eficiencia = compilar_metricas_eficiencia(embeddings_data)
    
    # Compila tudo
    all_results = {
        'similaridade': results_similaridade,
        'clustering': results_clustering,
        'consistencia': results_consistencia,
        'eficiencia': results_eficiencia
    }
    
    # Resumo
    df_summary = gerar_resumo_comparativo(all_results)
    
    # Salva
    output_file = salvar_resultados(all_results, df_summary)
    
    # Conclusão
    print("\n" + "="*80)
    print("🎉 COMPARAÇÃO CONCLUÍDA!")
    print("="*80)
    
    print(f"\n📁 Arquivo gerado:")
    print(f"   {output_file.name}")
    
    print(f"\n🔮 Próximos passos:")
    print(f"   1. Renderizar: quarto render notebooks/04i-embeddings-comparison.qmd")
    print(f"   2. Escolher melhor modelo para clustering")
    print(f"   3. Partir para análises avançadas!")

if __name__ == '__main__':
    main()