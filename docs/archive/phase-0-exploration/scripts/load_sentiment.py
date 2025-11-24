import pandas as pd
import json

print("="*80)
print("📂 CARREGANDO DADOS SALVOS (SEM RODAR BERT DE NOVO!)")
print("="*80)

# ========== 1. CARREGA DATAFRAME COMPLETO ==========
print("\n⏳ Carregando DataFrame completo...")

df = pd.read_csv('output/df_with_sentiment.csv')

# Converte timestamp de volta pra datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

print(f"✅ DataFrame carregado!")
print(f"   • Total de mensagens: {len(df):,}")
print(f"   • Com sentiment: {df['sentiment_score'].notna().sum():,}")
print(f"   • Período: {df['timestamp'].min().date()} até {df['timestamp'].max().date()}")
print(f"   • Colunas: {len(df.columns)}")

# ========== 2. CARREGA TIMELINE ==========
print("\n⏳ Carregando timeline agregada...")

sentiment_timeline = pd.read_csv('output/sentiment_timeline.csv')
sentiment_timeline['week'] = pd.to_datetime(sentiment_timeline['week'])

print(f"✅ Timeline carregada: {len(sentiment_timeline)} semanas")

# ========== 3. CARREGA COMPARAÇÃO ==========
print("\n⏳ Carregando comparação P1 vs P2...")

comparison = pd.read_csv('output/sentiment_comparison.csv')

print(f"✅ Comparação carregada:")
print(comparison.to_string(index=False))

# ========== 4. CARREGA ESTATÍSTICAS ==========
print("\n⏳ Carregando estatísticas...")

with open('output/sentiment_stats.json', 'r', encoding='utf-8') as f:
    stats = json.load(f)

print(f"✅ Estatísticas carregadas!")
print(f"\n📊 Sentimento Geral:")
print(f"   • Média: {stats['geral']['media']:.3f}")
print(f"   • Mediana: {stats['geral']['mediana']:.3f}")
print(f"   • Desvio: {stats['geral']['desvio_padrao']:.3f}")

print(f"\n📊 Por Pessoa:")
for pessoa, valores in stats['por_pessoa'].items():
    print(f"   • {pessoa}: média={valores['media']:.3f}, total={valores['total']:,}")

# ========== 5. RESUMO ==========
print("\n" + "="*80)
print("🎉 TUDO CARREGADO COM SUCESSO!")
print("="*80)

print("\n🚀 Variáveis disponíveis:")
print("   • df (DataFrame completo)")
print("   • sentiment_timeline (agregado semanal)")
print("   • comparison (P1 vs P2)")
print("   • stats (estatísticas dict)")

print("\n💡 Agora você pode:")
print("   • Fazer novos gráficos")
print("   • Atualizar visualizações")
print("   • Adicionar dados novos")
print("   • Escrever a narrativa")

print("\n⚡ Tempo de carregamento: ~3 segundos (vs 27 minutos do BERT!)")