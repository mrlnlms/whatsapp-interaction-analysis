import pandas as pd
import os
import re
from datetime import datetime

# --- 1. Carregar o DataFrame ---
df = pd.read_csv('/Users/mosx/Desktop/local-workbench/whats-le/data-wrangling/data/structured_chat.csv')

# --- 2. Coletar timestamps dos arquivos reais ---
media_folder = '/Users/mosx/Desktop/local-workbench/whats-le/_sources/WhatsAppFiles'
file_timestamps = []

print("🔍 Extraindo timestamps dos arquivos reais...")
for filename in os.listdir(media_folder):
    full_path = os.path.join(media_folder, filename)
    if os.path.isfile(full_path):
        # Padrão: 00001233-AUDIO-2025-09-02-13-02-21.opus
        match = re.match(r'\d+-[A-Z]+-(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})\.', filename)
        if match:
            y, m, d, H, M, S = map(int, match.groups())
            file_timestamps.append(datetime(y, m, d, H, M, S))

# Converter para Series do pandas
media_series = pd.Series(file_timestamps, name='file_timestamp')
print(f"✅ Total de arquivos com timestamp válido: {len(media_series)}")

# --- 3. Período dos arquivos reais ---
if not media_series.empty:
    file_min = media_series.min()
    file_max = media_series.max()
    file_days = media_series.dt.date.nunique()
else:
    file_min = file_max = None
    file_days = 0

# --- 4. Período das mensagens de mídia no chat ---
mids = df[df['message_type'].isin(['audio', 'video', 'image', 'sticker', 'document'])].copy()
if not mids.empty:
    mids['ts'] = pd.to_datetime(mids['timestamp'])
    chat_min = mids['ts'].min()
    chat_max = mids['ts'].max()
    chat_days = mids['ts'].dt.date.nunique()
else:
    chat_min = chat_max = None
    chat_days = 0

# --- 5. Mostrar comparação ---
print("\n" + "="*60)
print("📅 COMPARAÇÃO DE PERÍODOS")
print("="*60)
print(f"📁 Arquivos reais:  {file_min} → {file_max} ({file_days} dias)")
print(f"💬 Mensagens no chat: {chat_min} → {chat_max} ({chat_days} dias)")

if file_min and chat_min:
    overlap_start = max(file_min, chat_min)
    overlap_end = min(file_max, chat_max)
    if overlap_start <= overlap_end:
        print(f"✅ Sobreposição: {overlap_start} → {overlap_end}")
    else:
        print("❌ Sem sobreposição temporal entre arquivos e chat.")
else:
    print("⚠️ Dados insuficientes para comparar.")

# --- 6. Estatísticas de cobertura ---
total_media_msgs = len(mids)
total_files = len(media_series)
print("\n📊 Cobertura:")
print(f"- Mensagens de mídia no chat: {total_media_msgs}")
print(f"- Arquivos reais disponíveis:   {total_files}")
print(f"- Cobertura teórica máxima:     {total_files / total_media_msgs * 100:.1f}%")