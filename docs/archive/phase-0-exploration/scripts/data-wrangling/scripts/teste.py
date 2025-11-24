# teste.py (versão corrigida)
import re
import pandas as pd

def robust_parse_whatsapp(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex permissivo
    pattern = r'\[(\d{2}/\d{2}/\d{2},? ?\d{1,2}:\d{2}:\d{2})\]\s*([^:]+?):\s*(.*?)(?=\[\d{2}/\d{2}/\d{2}|$)'
    
    matches = re.findall(pattern, content, re.DOTALL)

    data = []
    for timestamp_str, sender, message in matches:
        message = re.sub(r'\s+', ' ', message).strip()  # limpa quebras
        data.append({
            'timestamp_str': timestamp_str,
            'sender': sender.strip(),
            'message': message
        })
    
    return pd.DataFrame(data)

# Parsear e salvar
df_clean = robust_parse_whatsapp('/Users/mosx/Desktop/local-workbench/whats-le/data-wrangling/data/raw-data.txt')
print("✅ Mensagens parseadas:", len(df_clean))
print("\nExemplo:")
print(df_clean.head())

# Salvar CSV limpo
df_clean.to_csv('/Users/mosx/Desktop/local-workbench/whats-le/data-wrangling/data/chat_clean.csv', index=False)
print("\n✅ Salvo como 'chat_clean.csv'")