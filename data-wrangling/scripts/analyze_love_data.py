import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import emoji
import os
from datetime import datetime
import re
# from datetime import datetime

# --- 1. Carregar o DataFrame ---
df = pd.read_csv('/Users/mosx/Desktop/local-workbench/whats-le/data-wrangling/data/structured_chat.csv')

print("✅ DataFrame carregado com sucesso!")
print(f"Linhas: {len(df)} | Colunas: {len(df.columns)}")
print("\n--- Primeiras 5 linhas ---")
print(df.head())

# --- 2. Estatísticas Gerais ---
print("\n" + "="*60)
print("📊 ESTASTÍSTICAS GERAIS")
print("="*60)

print(f"Período da conversa: {df['date'].min()} até {df['date'].max()}")
print(f"Total de mensagens: {len(df)}")
print(f"Total de dias com mensagem: {df['date'].nunique()}")

# Participação por pessoa
participacao = df['sender'].value_counts(normalize=False)
print("\nParticipação por pessoa:")
for pessoa, total in participacao.items():
    print(f"- {pessoa}: {total} mensagens ({total / len(df) * 100:.1f}%)")

# Tipos de mensagem
tipo_msg = df['message_type'].value_counts()
print("\nTipos de mensagem:")
for tipo, total in tipo_msg.items():
    print(f"- {tipo}: {total}")

# --- 3. Análise de Horários e Dias ---
print("\n" + "="*60)
print("🕐 PADRÕES DE COMUNICAÇÃO")
print("="*60)

# Horário mais ativo
hora_ativa = df['hour'].mode()[0] if not df['hour'].mode().empty else 'N/A'
print(f"Horário mais ativo: {hora_ativa}h")

# Dia da semana mais ativo
dia_ativo = df['day_of_week'].mode()[0] if not df['day_of_week'].mode().empty else 'N/A'
print(f"Dia da semana mais ativo: {dia_ativo}")

# --- 4. Links e Conteúdo Externo ---
print("\n" + "="*60)
print("🔗 LINKS E PLANEJAMENTO")
print("="*60)

links_df = df[df['contains_link']]
print(f"Total de links compartilhados: {len(links_df)}")

if not links_df.empty:
    dominios = links_df['domain'].value_counts()
    print("\nDomínios mais compartilhados:")
    for dom, total in dominios.head(10).items():
        print(f"- {dom}: {total}")
else:
    print("Nenhum link encontrado.")

# --- 5. Mensagens Editadas e Apagadas ---
print("\n" + "="*60)
print("✏️  EDIÇÕES E APAGAMENTOS")
print("="*60)

total_edited = df['is_edited'].sum()
total_deleted = df['is_deleted'].sum()
total_minimal = df['is_minimal_reply'].sum()

print(f"Mensagens editadas: {total_edited}")
print(f"Mensagens apagadas: {total_deleted}")
print(f"Mensagens mínimas ('.'): {total_minimal}")

# --- 6. Análise de Emojis ---
print("\n" + "="*60)
print("❤️  EMOJIS E AFETO")
print("="*60)

# Contar emojis no DataFrame (só nas mensagens de texto)
df_text = df[df['message_type'] == 'text']
emoji_counts = df_text['message_clean'].apply(lambda x: len(emoji.emoji_list(str(x))) if pd.notnull(x) else 0)
total_emojis = emoji_counts.sum()
print(f"Total de emojis em mensagens de texto: {total_emojis}")
print(f"Média de emojis por mensagem de texto: {emoji_counts.mean():.2f}")

# --- 7. Visualizações Rápidas ---
print("\n" + "="*60)
print("📈 VISUALIZAÇÕES")
print("="*60)

# Gráfico 1: Participação por pessoa
plt.figure(figsize=(10, 5))
sns.countplot(data=df, x='sender', order=df['sender'].value_counts().index)
plt.title('Quantidade de Mensagens por Pessoa')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Gráfico 2: Mensagens por tipo
plt.figure(figsize=(12, 6))
sns.countplot(data=df, y='message_type', order=df['message_type'].value_counts().index)
plt.title('Tipos de Mensagens')
plt.tight_layout()
plt.show()

# Gráfico 3: Mensagens por hora do dia
plt.figure(figsize=(12, 6))
sns.histplot(df['hour'], bins=24, kde=True)
plt.title('Distribuição de Mensagens por Hora do Dia')
plt.xlabel('Hora')
plt.ylabel('Quantidade')
plt.tight_layout()
plt.show()

# Gráfico 4: Mensagens por dia da semana
plt.figure(figsize=(10, 6))
sns.countplot(data=df, x='day_of_week', order=['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'])
plt.title('Mensagens por Dia da Semana')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# --- 8. Resumo Narrativo para a Carta ---
print("\n" + "="*60)
print("💌 INSIGHTS PARA A CARTA ANALÍTICA")
print("="*60)

print(f"Durante {len(df['date'].unique())} dias, vocês trocaram {len(df)} mensagens.")
print(f"Você escreveu {participacao.iloc[0]} e {participacao.iloc[1]} escreveu {participacao.iloc[1]}.")
print(f"Vocês mais conversaram às {hora_ativa}h, no {dia_ativo}.")
if total_edited > 0:
    print(f"Você editou {total_edited} mensagem(ns) — talvez com cuidado ou carinho.")
if total_deleted > 0:
    print(f"{total_deleted} mensagem(ns) foram apagadas — talvez por arrependimento ou brincadeira.")
if total_emojis > 0:
    print(f"Vocês usaram {total_emojis} emojis — o coração do diálogo está nos símbolos também.")
if dominios.get('airbnb.com', 0) > 0:
    print(f"Vocês planejaram juntos {dominios.get('airbnb.com', 0)} vezes — o futuro é um lugar a dois.")

print("\nFim da análise exploratória.")

# Tipos de mídia que deveriam ter arquivo
tipos_midiaticos = ['audio', 'video', 'image', 'sticker', 'document']

df_midiatico = df[df['message_type'].isin(tipos_midiaticos)]
total_midiatico = len(df_midiatico)
com_arquivo = df_midiatico['file_path'].notna().sum()

print(f"\nTotal de mensagens de mídia: {total_midiatico}")
print(f"Vinculadas a arquivos reais: {com_arquivo} ({com_arquivo / total_midiatico * 100:.1f}%)")


















# Carregar DataFrame
# df = pd.read_csv('/Users/mosx/Desktop/local-workbench/whats-le/data-wrangling/data/structured_chat.csv')

# Extrair todos os timestamps dos arquivos reais
media_folder = '/Users/mosx/Desktop/local-workbench/whats-le/_sources/WhatsAppFiles'
file_timestamps = []

for filename in os.listdir(media_folder):
    if os.path.isfile(os.path.join(media_folder, filename)):
        match = re.match(r'\d+-([A-Z]+)-(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})\.', filename)
        if match:
            y, m, d, H, M, S = map(int, match.groups()[1:])
            file_timestamps.append(datetime(y, m, d, H, M, S))

media_times = pd.Series(file_timestamps).sort_values().reset_index(drop=True)

# Extrair timestamps das mensagens de mídia
mids = df[df['message_type'].isin(['audio', 'video', 'image', 'sticker', 'document'])].copy()
mids['ts'] = pd.to_datetime(mids['timestamp'])

print(f"Total de mensagens de mídia: {len(mids)}")
print(f"Total de timestamps de arquivos: {len(media_times)}")

# Ver diferença mínima para cada mensagem
def min_time_diff(ts, media_times):
    diffs = (media_times - ts).abs()
    return diffs.min().total_seconds() if not diffs.empty else None

mids['min_diff_sec'] = mids['ts'].apply(lambda x: min_time_diff(x, media_times))

# Estatísticas
print("\nDistância média (segundos) entre mensagem e arquivo mais próximo:")
print(mids['min_diff_sec'].describe())











# Mensagens que têm <attached: ...> NO CONTEÚDO BRUTO (ou seja, vieram com mídia)
attached_msgs = df[df['message'].str.contains(r'<attached:', na=False)]

# Dessas, ver quais têm texto além da tag
def has_text_besides_attached(msg):
    # Remove a tag <attached: ...> e vê se sobra algo significativo
    cleaned = re.sub(r'‎?<attached:.*?>', '', msg)
    return len(cleaned.strip()) > 0


attached_with_text = attached_msgs[
    attached_msgs['message'].apply(has_text_besides_attached)
]

print(f"Total de mensagens com <attached: ...>: {len(attached_msgs)}")
print(f"Total com texto adicional: {len(attached_with_text)}")

# Mostrar exemplos
if not attached_with_text.empty:
    print("\nExemplos de mensagens com texto + mídia:")
    for i, row in attached_with_text.head().iterrows():
        print(f"- [{row['timestamp']}] {row['sender']}: {row['message']}")