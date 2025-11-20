import pandas as pd
import re
import os
from datetime import datetime
import emoji

# --- 1. Funções de Parsing e Normalização ---

def parse_whatsapp_lines(lines):
    """
    Parseia linhas do export do WhatsApp, lidando com quebras de linha.
    Retorna uma lista de dicionários com raw_line, sender, message, timestamp_str.
    """
    pattern = r'\[(\d{2}/\d{2}/\d{2},? \d{1,2}:\d{2}:\d{2})\]\s+([^:]+):\s*(.*)'
    
    data = []
    current_msg = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = re.match(pattern, line)

        if match:
            # Nova mensagem
            if current_msg:
                data.append(current_msg)
            timestamp_str, sender, content = match.groups()
            current_msg = {
                'raw_line': line,
                'sender': sender.strip(),
                'message': content,
                'timestamp_str': timestamp_str,
                'is_continuation': False
            }
        else:
            # Continuação de mensagem anterior (se não for timestamp)
            if current_msg and not line.startswith('['):
                current_msg['message'] += " " + line
                current_msg['is_continuation'] = True
            else:
                # Linha sem timestamp que não é continuação? Pode ser erro ou chamada.
                # Adiciona como mensagem separada com timestamp anterior
                if current_msg:
                    data.append(current_msg)
                current_msg = {
                    'raw_line': line,
                    'sender': 'System',  # ou None, se não tiver remetente
                    'message': line,
                    'timestamp_str': current_msg['timestamp_str'], # Repete o último
                    'is_continuation': True
                }

    if current_msg:
        data.append(current_msg)

    return data

def normalize_message_content(msg):
    """
    Normaliza placeholders de mídia para um formato consistente.
    """
    msg = msg.strip()
    if '<attached:' in msg:
        if 'AUDIO' in msg:
            return '‎audio omitted'
        elif 'VIDEO' in msg:
            return '‎video omitted'
        elif 'PHOTO' in msg:
            return '‎image omitted'
        elif 'STICKER' in msg:
            return '‎sticker omitted'
        elif msg.endswith('.pdf') or msg.endswith('.xlsx'):
            return '‎document omitted'
        else:
            return '‎media omitted' # para outros tipos
    elif 'This message was deleted' in msg:
        return '‎This message was deleted.'
    elif '<This message was edited>' in msg:
        # Remove a tag, mas conteúdo permanece para outras análises
        return msg.replace('‎<This message was edited>', '').strip()
    return msg

def classify_message_type(msg):
    """
    Classifica o tipo de mensagem.
    """
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
    elif msg == '.':
        return 'text' # mas marcaremos is_minimal_reply
    elif not msg.strip():
        return 'empty'
    else:
        return 'text'

def extract_domain_from_link(link):
    """
    Extrai domínio de um link. Retorna None se não for link.
    """
    if link.startswith('http'):
        import urllib.parse
        parsed = urllib.parse.urlparse(link)
        return parsed.netloc
    return None

def parse_media_filename(filename):
    """
    Extrai tipo e timestamp do nome do arquivo de mídia.
    """
    pattern = r'(\d+)-([A-Z]+)-(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})\..+'
    match = re.match(pattern, filename)
    if match:
        _, media_type, y, m, d, H, M, S = match.groups()
        ts = datetime(int(y), int(m), int(d), int(H), int(M), int(S))
        return {
            'file_name': filename,
            'media_type': media_type.lower(),
            'media_timestamp': ts,
            'file_path': os.path.join('WhatsApp Media', filename)
        }
    return None

# --- 2. Função Principal ---

def wrangle_whatsapp_export(chat_file_path, media_folder_path=None):
    """
    Lê o export do WhatsApp e gera o DataFrame estruturado.
    """
    # Ler arquivo
    with open(chat_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Parsear linhas
    parsed_data = parse_whatsapp_lines(lines)

    # Criar DataFrame
    df = pd.DataFrame(parsed_data)

    # Converter timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp_str'], format='%d/%m/%y, %H:%M:%S', errors='coerce')
    df['date'] = df['timestamp'].dt.date
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.day_name()

    # Normalizar conteúdo
    df['message_clean'] = df['message'].apply(normalize_message_content)

    # Classificar tipo
    df['message_type'] = df['message_clean'].apply(classify_message_type)

    # Contagens
    df['word_count'] = df['message_clean'].apply(lambda x: len(x.split()) if x != '‎This message was deleted.' and 'omitted' not in x else 0)
    df['char_count'] = df['message_clean'].apply(lambda x: len(x))

    # Flags
    df['contains_link'] = df['message_clean'].str.startswith('http')
    df['contains_emoji'] = df['message_clean'].apply(lambda x: bool(emoji.emoji_list(x)))
    df['is_edited'] = df['message'].str.contains('<This message was edited>', na=False)
    df['is_deleted'] = df['message_type'] == 'deleted'
    df['is_minimal_reply'] = df['message_clean'] == '.'

    # Extrair domínio de links
    df['domain'] = df['message_clean'].apply(lambda x: extract_domain_from_link(x) if x.startswith('http') else None)

    # --- Integração com arquivos de mídia ---
    if media_folder_path and os.path.isdir(media_folder_path):
        media_files = [f for f in os.listdir(media_folder_path) if f.endswith(('.opus', '.mp4', '.jpg', '.webp', '.pdf', '.xlsx'))]
        media_records = [parse_media_filename(f) for f in media_files if parse_media_filename(f)]
        if media_records:
            media_df = pd.DataFrame(media_records)
            if not media_df.empty:
                # Arredondar timestamps para minuto mais próximo
                df['ts_rounded'] = df['timestamp'].dt.floor('min')
                media_df['ts_rounded'] = media_df['media_timestamp'].dt.floor('min')

                # Fazer merge
                df = pd.merge_asof(
                    df.sort_values('ts_rounded'),
                    media_df[['ts_rounded', 'file_path']].sort_values('ts_rounded'),
                    on='ts_rounded',
                    direction='nearest',
                    tolerance=pd.Timedelta('1min')
                )
                df = df.drop(columns=['ts_rounded'])

    # --- Coluna opcional para transcrição futura ---
    df['transcription'] = None # ou df['transcription'] = ''

    # Remover colunas intermediárias
    df = df.drop(columns=['timestamp_str', 'raw_line'], errors='ignore')

    return df

# --- Exemplo de uso ---
if __name__ == '__main__':
    # Substitua pelos caminhos reais
    chat_file = '/Users/mosx/Desktop/local-workbench/whats-le/data-wrangling/data/raw-data.txt'
    media_folder = '/Users/mosx/Desktop/local-workbench/whats-le/_sources/WhatsAppFiles' # Pasta com os arquivos de mídia

    df = wrangle_whatsapp_export(chat_file, media_folder)

    print(df.head(10))
    print("\n--- Info do DataFrame ---")
    print(df.info())

    # Salvar
    df.to_csv('/Users/mosx/Desktop/local-workbench/whats-le/data-wrangling/data/structured_chat.csv', index=False, encoding='utf-8')
    print("\nDataFrame salvo como 'structured_chat.csv'.")
