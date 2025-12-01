"""
Sentiment Ensemble - Combinação Inteligente de Modelos

Cria classificação consensual combinando 3 modelos de sentiment analysis:
- Twitter-XLM-RoBERTa (Equilibrado)
- DistilBERT (Polarizador)
- RoBERTa Latest (Ultra Conservador)

Estratégia:
    - Majority Voting: 2+ modelos concordam → usa esse label
    - Weighted Tiebreak: Todos discordam → usa maior confiança
    - Confidence Calibration: Ajusta confiança baseado em concordância

Uso:
    python scripts/sentiment_ensemble.py

Input:  data/processed/messages_with_models.parquet (com 3 modelos)
Output: data/processed/messages_with_models.parquet (atualizado)
        data/processed/sentiment_ensemble_metadata.json

Colunas adicionadas:
    - sentimento_ensemble_label (category): positive/neutral/negative
    - sentimento_ensemble_confidence (float): confiança do ensemble (0-1)
    - sentimento_ensemble_votes (int): número de modelos concordando (1-3)
    - sentimento_ensemble_method (str): unanimous/majority/weighted_tiebreak
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import time
import json
from collections import Counter

# ========== CONFIGURAÇÕES ==========
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from config import PATHS  # noqa: E402

# Modelos disponíveis
MODELS = {
    'roberta': {
        'label': 'sentimento_roberta_label',
        'score': 'sentimento_roberta_score',
        'name': 'Twitter-RoBERTa'
    },
    'distilbert': {
        'label': 'sentimento_distilbert_label',
        'score': 'sentimento_distilbert_score',
        'name': 'DistilBERT'
    },
    'deberta': {
        'label': 'sentimento_deberta_label',
        'score': 'sentimento_deberta_score',
        'name': 'RoBERTa Latest'
    }
}

# ========== FUNÇÕES ==========

def verificar_modelos(df):
    """Verifica se todos os modelos necessários existem no DataFrame"""
    print("\n🔍 Verificando modelos disponíveis...")
    
    modelos_faltando = []
    modelos_presentes = []
    
    for model_id, model_info in MODELS.items():
        label_col = model_info['label']
        score_col = model_info['score']
        
        if label_col in df.columns and score_col in df.columns:
            count = df[label_col].notna().sum()
            modelos_presentes.append(model_info['name'])
            print(f"   ✅ {model_info['name']}: {count:,} mensagens")
        else:
            modelos_faltando.append(model_info['name'])
            print(f"   ❌ {model_info['name']}: não encontrado")
    
    if modelos_faltando:
        print(f"\n⚠️  Modelos faltando: {', '.join(modelos_faltando)}")
        print("   Execute os scripts dos modelos faltantes primeiro.")
        return False
    
    print(f"\n✅ Todos os 3 modelos encontrados!")
    return True

def aplicar_ensemble(df):
    """
    Aplica ensemble usando majority voting + weighted tiebreak
    
    Estratégia:
    1. Se 3 concordam → unanimous (confiança média dos 3)
    2. Se 2 concordam → majority (confiança média dos 2)
    3. Se todos discordam → weighted_tiebreak (maior confiança individual)
    """
    print("\n🎯 Aplicando ensemble...")
    print("   Estratégia: Majority Voting + Weighted Tiebreak")
    
    # Colunas dos modelos
    label_cols = [MODELS[m]['label'] for m in MODELS]
    score_cols = [MODELS[m]['score'] for m in MODELS]
    
    # Inicializa colunas resultado
    df['sentimento_ensemble_label'] = None
    df['sentimento_ensemble_confidence'] = None
    df['sentimento_ensemble_votes'] = None
    df['sentimento_ensemble_method'] = None
    
    # Filtra mensagens com todos os 3 modelos
    mask = df[label_cols[0]].notna() & df[label_cols[1]].notna() & df[label_cols[2]].notna()
    df_validos = df[mask].copy()
    
    total_processar = len(df_validos)
    print(f"\n📊 Mensagens a processar: {total_processar:,}")
    
    if total_processar == 0:
        print("\n⚠️  Nenhuma mensagem com os 3 modelos disponível!")
        return df
    
    # Processa cada mensagem
    inicio = time.time()
    
    ensemble_labels = []
    ensemble_confidences = []
    ensemble_votes = []
    ensemble_methods = []
    
    for idx, row in df_validos.iterrows():
        # Coleta votos e scores
        votes = {
            'positive': 0,
            'neutral': 0,
            'negative': 0
        }
        
        scores_by_label = {
            'positive': [],
            'neutral': [],
            'negative': []
        }
        
        # Conta votos
        for label_col, score_col in zip(label_cols, score_cols):
            label = row[label_col]
            score = row[score_col]
            
            if pd.notna(label) and pd.notna(score):
                votes[label] += 1
                scores_by_label[label].append(score)
        
        # Encontra label vencedor
        max_votes = max(votes.values())
        winning_labels = [label for label, count in votes.items() if count == max_votes]
        
        # DECISÃO DO ENSEMBLE
        
        if max_votes == 3:
            # CASO 1: Consenso total (unanimous)
            final_label = winning_labels[0]
            final_confidence = np.mean(scores_by_label[final_label])
            final_votes = 3
            final_method = 'unanimous'
            
            # Boost de confiança (consenso total)
            final_confidence = min(final_confidence * 1.05, 1.0)
            
        elif max_votes == 2:
            # CASO 2: Maioria (majority)
            final_label = winning_labels[0]
            final_confidence = np.mean(scores_by_label[final_label])
            final_votes = 2
            final_method = 'majority'
            
        else:
            # CASO 3: Empate triplo - usa maior confiança (weighted_tiebreak)
            best_label = None
            best_score = 0
            
            for label in ['positive', 'neutral', 'negative']:
                if scores_by_label[label]:
                    score = scores_by_label[label][0]
                    if score > best_score:
                        best_score = score
                        best_label = label
            
            final_label = best_label
            final_confidence = best_score * 0.95  # Penaliza desacordo
            final_votes = 1
            final_method = 'weighted_tiebreak'
        
        # Armazena resultados
        ensemble_labels.append(final_label)
        ensemble_confidences.append(final_confidence)
        ensemble_votes.append(final_votes)
        ensemble_methods.append(final_method)
    
    # Adiciona ao DataFrame
    df.loc[mask, 'sentimento_ensemble_label'] = ensemble_labels
    df.loc[mask, 'sentimento_ensemble_confidence'] = ensemble_confidences
    df.loc[mask, 'sentimento_ensemble_votes'] = ensemble_votes
    df.loc[mask, 'sentimento_ensemble_method'] = ensemble_methods
    
    # Converte para category
    df['sentimento_ensemble_label'] = df['sentimento_ensemble_label'].astype('category')
    
    tempo_proc = time.time() - inicio
    
    print(f"✅ Ensemble aplicado em {tempo_proc:.2f} segundos")
    
    return df

def exibir_resumo(df):
    """Mostra estatísticas do ensemble"""
    print("\n" + "="*80)
    print("📊 RESUMO DO ENSEMBLE")
    print("="*80)
    
    mask = df['sentimento_ensemble_label'].notna()
    total = mask.sum()
    
    print(f"\n✅ Mensagens processadas: {total:,}")
    
    if total > 0:
        # Distribuição
        print(f"\n📈 Distribuição:")
        dist = df['sentimento_ensemble_label'].value_counts()
        for label, count in dist.items():
            pct = count / total * 100
            emoji = {'positive': '😊', 'neutral': '😐', 'negative': '😢'}.get(label, '')
            print(f"   {emoji} {label:10s}: {count:6,} ({pct:5.1f}%)")
        
        # Confiança média
        print(f"\n📊 Confiança média: {df[mask]['sentimento_ensemble_confidence'].mean():.3f}")
        
        # Distribuição por votos
        print(f"\n🗳️  Distribuição por votos:")
        votes_dist = df[mask]['sentimento_ensemble_votes'].value_counts().sort_index()
        for votes, count in votes_dist.items():
            pct = count / total * 100
            
            if votes == 3:
                desc = "Consenso total"
                emoji = "✅"
            elif votes == 2:
                desc = "Maioria"
                emoji = "🤝"
            else:
                desc = "Desacordo (tiebreak)"
                emoji = "⚠️"
            
            print(f"   {emoji} {votes} voto(s) - {desc:20s}: {count:6,} ({pct:5.1f}%)")
        
        # Métodos usados
        print(f"\n🔧 Métodos aplicados:")
        methods_dist = df[mask]['sentimento_ensemble_method'].value_counts()
        for method, count in methods_dist.items():
            pct = count / total * 100
            print(f"   {method:20s}: {count:6,} ({pct:5.1f}%)")

def comparar_com_modelos(df):
    """Compara ensemble com modelos individuais"""
    print("\n" + "="*80)
    print("🔍 COMPARAÇÃO COM MODELOS INDIVIDUAIS")
    print("="*80)
    
    mask = df['sentimento_ensemble_label'].notna()
    
    print("\n📊 Concordância com Ensemble:\n")
    
    for model_id, model_info in MODELS.items():
        label_col = model_info['label']
        
        if label_col in df.columns:
            # Mensagens com ambos
            mask_both = mask & df[label_col].notna()
            
            if mask_both.sum() > 0:
                concordancia = (df.loc[mask_both, 'sentimento_ensemble_label'] == df.loc[mask_both, label_col]).mean()
                print(f"   {model_info['name']:20s}: {concordancia*100:5.1f}%")

def salvar_metadata(df, tempo_total):
    """Salva metadados do ensemble"""
    
    mask = df['sentimento_ensemble_label'].notna()
    
    metadata = {
        'timestamp_execucao': pd.Timestamp.now().isoformat(),
        'tempo_total_segundos': round(tempo_total, 2),
        'tempo_total_minutos': round(tempo_total / 60, 2),
        'mensagens_total': len(df),
        'mensagens_processadas': int(mask.sum()),
        'mensagens_puladas': int((~mask).sum()),
        
        # Distribuição
        'distribuicao': {
            str(k): int(v) for k, v in df['sentimento_ensemble_label'].value_counts().to_dict().items()
        },
        
        # Confiança
        'confianca_media': float(df[mask]['sentimento_ensemble_confidence'].mean()),
        
        # Votos
        'consenso_total': int((df['sentimento_ensemble_votes'] == 3).sum()),
        'consenso_total_pct': float((df['sentimento_ensemble_votes'] == 3).sum() / mask.sum() * 100),
        'maioria': int((df['sentimento_ensemble_votes'] == 2).sum()),
        'maioria_pct': float((df['sentimento_ensemble_votes'] == 2).sum() / mask.sum() * 100),
        'desacordo': int((df['sentimento_ensemble_votes'] == 1).sum()),
        'desacordo_pct': float((df['sentimento_ensemble_votes'] == 1).sum() / mask.sum() * 100),
        
        # Métodos
        'metodos': {
            str(k): int(v) for k, v in df['sentimento_ensemble_method'].value_counts().to_dict().items()
        },
    }
    
    # Concordância com cada modelo
    for model_id, model_info in MODELS.items():
        label_col = model_info['label']
        score_col = model_info['score']
        
        if label_col in df.columns:
            mask_both = mask & df[label_col].notna()
            
            if mask_both.sum() > 0:
                concordancia = (df.loc[mask_both, 'sentimento_ensemble_label'] == df.loc[mask_both, label_col]).mean()
                
                metadata[f'concordancia_{model_id}'] = float(concordancia * 100)
                metadata[f'confianca_{model_id}'] = float(df[mask_both][score_col].mean())
    
    metadata_file = PATHS['processed'] / 'sentiment_ensemble_metadata.json'
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    return metadata_file

def main():
    print("="*80)
    print("🎯 SENTIMENT ENSEMBLE")
    print("="*80)
    
    inicio_total = time.time()
    
    # Caminhos
    input_file = PATHS['processed'] / 'messages_with_models.parquet'
    output_file = PATHS['processed'] / 'messages_with_models.parquet'
    
    # Verifica se arquivo existe
    if not input_file.exists():
        print(f"\n❌ Arquivo não encontrado: {input_file}")
        print("   Execute os modelos individuais primeiro:")
        print("   1. python scripts/sentiment_twitter_roberta.py")
        print("   2. python scripts/sentiment_distilbert.py")
        print("   3. python scripts/sentiment_deberta.py")
        return
    
    print(f"\n📂 Input: {input_file.name}")
    
    # Carrega dados
    print(f"\n📦 Carregando dataset...")
    df = pd.read_parquet(input_file)
    print(f"   {len(df):,} mensagens | {len(df.columns)} colunas")
    
    # Verifica modelos
    if not verificar_modelos(df):
        return
    
    # Aplica ensemble
    df = aplicar_ensemble(df)
    
    # Resumo
    exibir_resumo(df)
    
    # Comparação
    comparar_com_modelos(df)
    
    # Tempo total
    tempo_total = time.time() - inicio_total
    
    # Salva
    print(f"\n💾 Salvando: {output_file.name}")
    df.to_parquet(output_file, index=False)
    print(f"   {output_file.stat().st_size / 1024 / 1024:.2f} MB")
    
    # Metadata
    metadata_file = salvar_metadata(df, tempo_total)
    print(f"\n📋 Metadata: {metadata_file.name}")
    
    print(f"\n⏱️  Tempo total: {tempo_total:.2f} segundos")
    
    print("\n" + "="*80)
    print("🎉 ENSEMBLE CONCLUÍDO!")
    print("="*80)
    
    print(f"\n💡 Próximos passos:")
    print(f"   1. Renderize o notebook: quarto render notebooks/04e-sentiment-ensemble.qmd")
    print(f"   2. Use 'sentimento_ensemble_label' no EDA como classificação principal")
    print(f"   3. Filtre por 'sentimento_ensemble_confidence' para análises robustas")

if __name__ == '__main__':
    main()