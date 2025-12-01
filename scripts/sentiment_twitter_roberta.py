"""
Análise de Sentimento - Twitter-XLM-RoBERTa

Modelo: cardiffnlp/twitter-xlm-roberta-base-sentiment
Classes: 3 (positive, neutral, negative)
Treinado em: Tweets multilingual (ótimo para mensagens curtas)

Uso:
    python scripts/sentiment_twitter_roberta.py

Input:  data/processed/messages_enriched.parquet
Output: data/processed/messages_with_models.parquet
        data/processed/sentiment_metadata.json

Colunas adicionadas:
    - sentimento_label (category): positive/neutral/negative
    - sentimento_score (float): confiança do modelo (0-1)
"""

import sys
from pathlib import Path
import pandas as pd
import torch
from transformers import pipeline
from tqdm import tqdm
import time
import json

try:
    import protobuf
except ImportError:
    print("⚠️  Instalando dependência faltante: protobuf")
    import subprocess
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'protobuf', '--break-system-packages'])
    print("✅ Protobuf instalado!")

# ========== CONFIGURAÇÕES ==========
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from config import PATHS

MODEL_NAME = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
BATCH_SIZE = 100
MIN_TEXT_LENGTH = 5

# ========== FUNÇÕES ==========

def detectar_device():
    """Detecta GPU ou usa CPU"""
    if torch.cuda.is_available():
        device = 0
        device_name = torch.cuda.get_device_name(0)
        is_gpu = True
        print(f"✅ GPU: {device_name}")
        return device, device_name, is_gpu
    else:
        device = -1
        device_name = "CPU"
        is_gpu = False
        print("💻 Usando CPU")
        return device, device_name, is_gpu

def carregar_modelo(device):
    """Carrega modelo Twitter-RoBERTa"""
    print(f"\n⏳ Carregando: {MODEL_NAME}")
    inicio = time.time()
    
    analyzer = pipeline(
        "sentiment-analysis",
        model=MODEL_NAME,
        device=device,
        max_length=512,
        truncation=True,
        use_fast=False
    )
    
    tempo = time.time() - inicio
    print(f"✅ Modelo pronto! ({tempo:.1f}s)")
    return analyzer

def processar_batch(textos, analyzer):
    """Processa em batches com error handling"""
    resultados = []
    erros = 0
    
    for i in tqdm(range(0, len(textos), BATCH_SIZE), desc="🤖 Analisando"):
        batch = textos[i:i+BATCH_SIZE]
        
        try:
            batch_results = analyzer(batch)
            resultados.extend(batch_results)
        except Exception as e:
            # Se batch falhar, processa individual
            erros += 1
            
            for texto in batch:
                try:
                    result = analyzer(texto)[0]
                    resultados.append(result)
                except:
                    resultados.append({'label': None, 'score': None})
    
    if erros > 0:
        print(f"\n⚠️  {erros} batches precisaram processamento individual")
    
    return resultados

def aplicar_sentimento(input_file, analyzer, is_gpu):
    """
    Pipeline otimizado - carrega só conteudo, processa, depois faz merge
    """
    print("\n📂 Carregando dados (otimizado)...")
    
    # 1. CARREGA SÓ CONTEUDO (leve!)
    df_trabalho = pd.read_parquet(input_file, columns=['conteudo'])
    print(f"   {len(df_trabalho):,} mensagens carregadas")
    
    # 2. FILTRA
    mask = (
        df_trabalho['conteudo'].notna() & 
        (df_trabalho['conteudo'].str.len() > MIN_TEXT_LENGTH)
    )
    
    df_validas = df_trabalho[mask].copy()
    
    print(f"\n📊 Dataset:")
    print(f"   Total: {len(df_trabalho):,}")
    print(f"   Válidas: {len(df_validas):,}")
    print(f"   Puladas: {(~mask).sum():,}")
    
    if len(df_validas) == 0:
        print("⚠️  Nada para processar!")
        return None, None, 0
    
    # 3. ESTIMA TEMPO
    msgs_por_seg = 500 if is_gpu else 50
    tempo_min = len(df_validas) / msgs_por_seg / 60
    print(f"\n⏱️  Tempo estimado: ~{tempo_min:.1f} minutos")
    
    # 4. PROCESSA
    print()
    inicio_proc = time.time()
    
    textos = df_validas['conteudo'].tolist()
    resultados = processar_batch(textos, analyzer)
    
    tempo_proc = time.time() - inicio_proc
    
    # 5. EXTRAI RESULTADOS
    labels = [r['label'] if r['label'] else None for r in resultados]
    scores = [r['score'] if r['score'] else None for r in resultados]
    
    # 6. ADICIONA AO DF DE TRABALHO (leve)
    df_trabalho['sentimento_roberta_label'] = None
    df_trabalho['sentimento_roberta_score'] = None
    
    df_trabalho.loc[mask, 'sentimento_roberta_label'] = labels
    df_trabalho.loc[mask, 'sentimento_roberta_score'] = scores
    
    # Converte para category
    df_trabalho['sentimento_roberta_label'] = df_trabalho['sentimento_roberta_label'].astype('category')
    
    # 7. RETORNA DF LEVE + TEMPO
    return df_trabalho[['sentimento_roberta_label', 'sentimento_roberta_score']], len(df_trabalho), tempo_proc
    

    

    
def exibir_resumo(df):
    """Mostra estatísticas finais"""
    print("\n" + "="*80)
    print("📊 RESUMO")
    print("="*80)
    
    total = df['sentimento_label'].notna().sum()
    print(f"\n✅ Analisadas: {total:,}")
    
    if total > 0:
        print(f"\n📈 Distribuição:")
        dist = df['sentimento_label'].value_counts()
        for label, count in dist.items():
            pct = count / total * 100
            print(f"   {label:10s}: {count:6,} ({pct:5.1f}%)")
        
        print(f"\n📊 Confiança média:")
        for label in ['positive', 'neutral', 'negative']:
            if label in df['sentimento_label'].values:
                score = df[df['sentimento_label'] == label]['sentimento_score'].mean()
                print(f"   {label:10s}: {score:.3f}")

def salvar_metadata(df, tempo_total, tempo_proc, device_name):
    """Salva metadados do processamento"""
    metadata = {
        'modelo': MODEL_NAME,
        'timestamp_execucao': pd.Timestamp.now().isoformat(),
        'tempo_total_segundos': round(tempo_total, 2),
        'tempo_total_minutos': round(tempo_total / 60, 2),
        'tempo_processamento_segundos': round(tempo_proc, 2),
        'tempo_processamento_minutos': round(tempo_proc / 60, 2),
        'mensagens_total': len(df),
        'mensagens_processadas': int(df['sentimento_label'].notna().sum()),
        'mensagens_puladas': int(df['sentimento_label'].isna().sum()),
        'batch_size': BATCH_SIZE,
        'device': device_name,
        'distribuicao': {
            str(k): int(v) for k, v in df['sentimento_label'].value_counts().to_dict().items()
        },
        'confianca_media': {
            label: float(df[df['sentimento_label'] == label]['sentimento_score'].mean())
            for label in ['positive', 'neutral', 'negative']
            if label in df['sentimento_label'].values
        }
    }
    
    metadata_file = PATHS['processed'] / 'sentiment_metadata.json'
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    return metadata_file

def main():
    print("="*80)
    print("💕 SENTIMENT ANALYSIS - Twitter-XLM-RoBERTa")
    print("="*80)
    
    inicio_total = time.time()
    
    # Caminhos
    input_file = PATHS['processed'] / 'messages_enriched.parquet'
    output_file = PATHS['processed'] / 'messages_with_models.parquet'
    
    print(f"\n📂 Input: {input_file.name}")
    
    # Setup
    device, device_name, is_gpu = detectar_device()
    analyzer = carregar_modelo(device)
    
    # PROCESSA (otimizado - só carrega conteudo)
    df_sentiment, total_msgs, tempo_proc = aplicar_sentimento(input_file, analyzer, is_gpu)
    
    if df_sentiment is None:
        print("\n❌ Nenhuma mensagem para processar!")
        return
    
    # AGORA SIM carrega parquet completo (só no final!)
    print("\n📦 Carregando dataset completo para merge...")
    df_full = pd.read_parquet(input_file)
    
    # Merge das novas colunas
    df_full['sentimento_roberta_label'] = df_sentiment['sentimento_roberta_label']
    df_full['sentimento_roberta_score'] = df_sentiment['sentimento_roberta_score']

    # Tempo total
    tempo_total = time.time() - inicio_total
    
    # Resumo
    exibir_resumo(df_full)
    
    # Salva
    print(f"\n💾 Salvando: {output_file.name}")
    df_full.to_parquet(output_file, index=False)
    print(f"   {output_file.stat().st_size / 1024 / 1024:.2f} MB")
    
    # Metadata
    metadata_file = salvar_metadata(df_full, tempo_total, tempo_proc, device_name)
    print(f"\n📋 Metadata: {metadata_file.name}")
    
    print(f"\n⏱️  Tempo total: {tempo_total/60:.2f} minutos")
    
    print("\n" + "="*80)
    print("🎉 CONCLUÍDO!")
    print("="*80)
    
    print(f"\n💡 Próximo passo:")
    print(f"   Abra 05-eda.qmd e explore os resultados!")

if __name__ == '__main__':
    main()