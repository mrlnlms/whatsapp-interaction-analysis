import pandas as pd
# import re
import emoji
# from datetime import datetime

# --- 1. Funções de classificação e enriquecimento ---

def classify_message_type(msg):
    """
    Classifica o tipo de mensagem com base no conteúdo.
    """
    # Verifica se é NaN
    if pd.isna(msg):
        return 'empty'
    
    msg_lower = msg.lower()
    if 'This message was deleted' in msg:
        return 'deleted'
    elif 'audio omitted' in msg_lower:
        return 'audio'
    elif 'video omitted' in msg_lower:
        return 'video'
    elif 'image omitted' in msg_lower:
        return 'image'
    elif 'sticker omitted' in msg_lower:
        return 'sticker'
    elif 'gif omitted' in msg_lower:
        return 'gif'
    elif 'document omitted' in msg_lower:
        return 'document'
    elif 'missed voice call' in msg_lower:
        return 'missed_voice_call'
    elif 'missed video call' in msg_lower:
        return 'missed_video_call'
    elif 'answered on other device' in msg_lower:
        if 'voice' in msg_lower:
            return 'answered_voice_call_elsewhere'
        elif 'video' in msg_lower:
            return 'answered_video_call_elsewhere'
        else:
            return 'answered_call_elsewhere'
    elif msg.startswith('http'):
        return 'link'
    elif not msg.strip():
        return 'empty'
    else:
        return 'text'

def extract_domain_from_link(link):
    """
    Extrai domínio de um link. Retorna None se não for link.
    """
    if pd.isna(link):
        return None
    if link.startswith('http'):
        import urllib.parse
        parsed = urllib.parse.urlparse(link)
        return parsed.netloc
    return None

def count_emojis(msg):
    """
    Conta emojis na mensagem.
    """
    if pd.isna(msg):
        return 0
    return len(emoji.emoji_list(msg))

def is_minimal_reply(msg):
    """
    Verifica se é uma resposta mínima (ex: '.').
    """
    if pd.isna(msg):
        return False
    return msg.strip() == '.'

# --- 2. Função principal ---

def reprocess_chat_clean(input_csv_path, output_csv_path):
    """
    Lê chat_clean.csv, faz classificação e enriquecimento, e salva o novo DataFrame.
    """
    print("🔄 Carregando dados...")
    df = pd.read_csv(input_csv_path)

    print(f"📊 Total de mensagens: {len(df)}")

    # Converter timestamp
    print("🕐 Convertendo timestamps...")
    df['timestamp'] = pd.to_datetime(df['timestamp_str'], format='%d/%m/%y, %H:%M:%S', errors='coerce')
    df['date'] = df['timestamp'].dt.date
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.day_name()
    df['is_weekend'] = df['timestamp'].dt.dayofweek.isin([5, 6])  # Sábado e domingo

    # Classificar tipo
    print("🏷️  Classificando tipo de mensagem...")
    df['message_type'] = df['message'].apply(classify_message_type)

    # Contagens
    print("📝 Calculando contagens...")
    df['word_count'] = df['message'].apply(lambda x: len(x.split()) if pd.notna(x) and 'omitted' not in x.lower() else 0)
    df['char_count'] = df['message'].apply(lambda x: len(x) if pd.notna(x) else 0)

    # Flags
    print("🚩 Adicionando flags...")
    df['contains_link'] = df['message'].apply(lambda x: x.startswith('http') if pd.notna(x) else False)
    df['contains_emoji'] = df['message'].apply(count_emojis).gt(0)
    df['is_minimal_reply'] = df['message'].apply(is_minimal_reply)
    df['emoji_count'] = df['message'].apply(count_emojis)

    # Extrair domínio de links
    df['domain'] = df['message'].apply(lambda x: extract_domain_from_link(x))

    # Outras colunas úteis
    df['is_media'] = df['message_type'].isin(['audio', 'video', 'image', 'sticker', 'gif', 'document'])
    df['is_textual'] = df['message_type'] == 'text'

    # Remover colunas intermediárias (opcional)
    df = df.drop(columns=['timestamp_str'], errors='ignore')

    print("💾 Salvando novo DataFrame...")
    df.to_csv(output_csv_path, index=False, encoding='utf-8')

    print(f"✅ Processamento concluído. Salvo em: {output_csv_path}")
    print("\n--- Info do novo DataFrame ---")
    print(df.info())

    return df

# --- Exemplo de uso ---
if __name__ == '__main__':
    input_path = '/Users/mosx/Desktop/local-workbench/whats-le/data-wrangling/data/chat_clean.csv'
    output_path = '/Users/mosx/Desktop/local-workbench/whats-le/data-wrangling/data/structured_chat_v2.csv'

    df = reprocess_chat_clean(input_path, output_path)