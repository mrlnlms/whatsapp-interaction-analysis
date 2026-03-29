"""
Funções de parsing, processamento de mídia e enriquecimento para dados do WhatsApp.

Uso:
    from wrangling import run_wrangling_pipeline, WRANGLING_STEPS
    
    result = run_wrangling_pipeline(
        order=['parse', 'classify', 'media', 'transcriptions', 'enrich', 'export'],
        input_file=Path('data/interim/raw-data_cln7.txt'),
        output_dir=Path('data/processed'),
        media_dir=Path('data/raw/export_2024-10_2025-10/media'),
        transcription_file=Path('transcriptions.csv')
    )
"""

import re
import os
import pandas as pd
from pathlib import Path
from datetime import datetime


# =============================================================================
# FASE 1: PARSING - TXT → DataFrame
# =============================================================================

def parse_to_dataframe(input_file: Path) -> pd.DataFrame:
    """
    Converte arquivo TXT limpo em DataFrame estruturado.
    
    Formato esperado: DD/MM/YY HH:MM:SS Remetente: Conteúdo
    Linhas sem timestamp são agregadas à mensagem anterior (multilinha).
    
    Args:
        input_file: Path do arquivo TXT limpo
        
    Returns:
        DataFrame com colunas: linha_original, data, hora, timestamp, remetente, conteudo
    """
    message_pattern = r'^(\d{2}/\d{2}/\d{2}) (\d{2}:\d{2}:\d{2}) (.+?): (.*)$'
    
    lines = open(input_file, 'r', encoding='utf-8').readlines()
    
    messages = []
    current_message = None
    
    for line_num, line in enumerate(lines, start=1):
        line = line.rstrip('\n')
        match = re.match(message_pattern, line)
        
        if match:
            # Salva mensagem anterior
            if current_message:
                messages.append(current_message)
            
            # Nova mensagem
            current_message = {
                'linha_original': line_num,
                'data': match.group(1),
                'hora': match.group(2),
                'remetente': match.group(3),
                'conteudo': match.group(4)
            }
        else:
            # Linha de continuação
            if current_message:
                current_message['conteudo'] += '\n' + line
    
    # Última mensagem
    if current_message:
        messages.append(current_message)

    if not messages:
        return pd.DataFrame(columns=[
            'linha_original', 'data', 'hora', 'remetente', 'conteudo', 'timestamp'
        ])

    df = pd.DataFrame(messages)

    # Cria timestamp datetime
    df['timestamp'] = pd.to_datetime(
        df['data'] + ' ' + df['hora'],
        format='%d/%m/%y %H:%M:%S'
    )

    return df


# =============================================================================
# FASE 2: CLASSIFICAÇÃO DE MENSAGENS
# =============================================================================

def classify_message_type(content: str) -> str:
    """
    Classifica o tipo de mensagem baseado no conteúdo.
    
    Tipos:
    - text_pure, text_with_emoji, text_with_link
    - audio_omitted, image_omitted, video_omitted, etc.
    - audio_attached, image_attached, video_attached, etc.
    - message_deleted, message_edited, voice_call, system_message
    """
    content_lower = content.lower().strip()
    
    # Mensagens deletadas/editadas
    if 'this message was deleted' in content_lower:
        return 'message_deleted'
    if '<this message was edited>' in content_lower:
        return 'message_edited'
    
    # Chamadas
    if 'voice call' in content_lower or 'video call' in content_lower:
        if 'missed' in content_lower:
            return 'missed_call'
        return 'voice_call'
    
    # Sistema
    if "this message can't be displayed" in content_lower:
        return 'system_message'
    
    # Mídias omitidas
    omitted_types = {
        'audio omitted': 'audio_omitted',
        'image omitted': 'image_omitted',
        'video omitted': 'video_omitted',
        'video note omitted': 'video_note_omitted',
        'sticker omitted': 'sticker_omitted',
        'gif omitted': 'gif_omitted',
        'document omitted': 'document_omitted',
    }
    
    for pattern, msg_type in omitted_types.items():
        if content_lower == pattern or pattern in content_lower:
            return msg_type
    
    # Mídias anexadas
    if '<attached:' in content_lower:
        if 'audio' in content_lower or '.opus' in content_lower or '.mp3' in content_lower:
            return 'audio_attached'
        elif 'photo' in content_lower or '.jpg' in content_lower or '.png' in content_lower:
            return 'image_attached'
        elif 'video' in content_lower or '.mp4' in content_lower:
            return 'video_attached'
        elif 'sticker' in content_lower or '.webp' in content_lower:
            return 'sticker_attached'
        elif '.vcf' in content_lower:
            return 'contact_attached'
        else:
            return 'file_attached'
    
    # Texto
    url_pattern = r'https?://[^\s]+'
    if re.search(url_pattern, content):
        return 'text_with_link'
    
    # Emoji (caracteres Unicode > 127, exceto acentos comuns)
    if any(ord(char) > 0x1F600 for char in content):  # Range de emojis
        return 'text_with_emoji'
    
    return 'text_pure'


def add_message_classification(df: pd.DataFrame) -> pd.DataFrame:
    """Adiciona coluna 'tipo_mensagem' ao DataFrame."""
    df = df.copy()
    df['tipo_mensagem'] = df['conteudo'].apply(classify_message_type)
    return df


# =============================================================================
# FASE 3: INVENTÁRIO E VINCULAÇÃO DE MÍDIA
# =============================================================================

def extract_filename_from_content(content: str) -> str:
    """Extrai nome do arquivo de uma mensagem com mídia anexada."""
    pattern = r'<attached:\s*(.+?)>'
    match = re.search(pattern, content)
    if not match:
        return None
    filename = match.group(1)
    # Security: prevent path traversal
    if '..' in filename or filename.startswith('/'):
        return None
    return filename


def extract_media_type_from_filename(filename: str) -> str:
    """Extrai tipo de mídia do nome do arquivo (AUDIO, VIDEO, PHOTO, etc.)."""
    if not filename:
        return None
    parts = filename.split('-')
    if len(parts) >= 2:
        return parts[1].upper()
    return None


def inventory_media_files(media_dir: Path) -> pd.DataFrame:
    """
    Lista todos os arquivos de mídia no diretório.
    
    Args:
        media_dir: Diretório com arquivos de mídia
        
    Returns:
        DataFrame com: filename, path, extension, size_bytes, media_type
    """
    media_dir = Path(media_dir)
    
    if not media_dir.exists():
        print(f"⚠️ Diretório não encontrado: {media_dir}")
        return pd.DataFrame()
    
    files = []
    for file_path in media_dir.iterdir():
        if file_path.is_file():
            files.append({
                'filename': file_path.name,
                'path': str(file_path),
                'extension': file_path.suffix.lower(),
                'size_bytes': file_path.stat().st_size,
                'media_type': extract_media_type_from_filename(file_path.name)
            })
    
    return pd.DataFrame(files)


def link_media_to_messages(df: pd.DataFrame, media_dir: Path) -> pd.DataFrame:
    """
    Vincula arquivos de mídia às mensagens correspondentes.
    
    Adiciona colunas: arquivo, extensao, tipo_arquivo, arquivo_existe, arquivo_path
    """
    df = df.copy()
    
    # Extrai nome do arquivo de mensagens anexadas
    df['arquivo'] = df['conteudo'].apply(extract_filename_from_content)
    
    # Inventário de arquivos físicos
    df_inventory = inventory_media_files(media_dir)
    existing_files = set(df_inventory['filename'].values) if not df_inventory.empty else set()
    
    # Verifica existência
    df['arquivo_existe'] = df['arquivo'].apply(lambda x: x in existing_files if x else False)
    
    # Extrai metadados
    df['extensao'] = df['arquivo'].apply(lambda x: Path(x).suffix.lower() if x else None)
    df['tipo_arquivo'] = df['arquivo'].apply(extract_media_type_from_filename)
    
    # Path completo
    df['arquivo_path'] = df.apply(
        lambda row: str(media_dir / row['arquivo']) if row['arquivo_existe'] else None,
        axis=1
    )
    
    return df


# =============================================================================
# FASE 4: TRANSCRIÇÃO
# =============================================================================

def load_transcriptions(transcription_file: Path) -> pd.DataFrame:
    """
    Carrega arquivo CSV com transcrições existentes.
    
    Esperado: file_path, transcription, transcription_status, is_synthetic
    """
    if not transcription_file or not Path(transcription_file).exists():
        print(f"⚠️ Arquivo de transcrições não encontrado: {transcription_file}")
        return pd.DataFrame()
    
    df = pd.read_csv(transcription_file)
    
    # Normaliza nome do arquivo (remove path, mantém só filename)
    if 'file_path' in df.columns:
        df['filename'] = df['file_path'].apply(lambda x: Path(x).name if pd.notna(x) else None)
    
    return df


def transcribe_media_groq(file_path: str, api_key: str = None) -> dict:
    """
    Transcreve arquivo de áudio/vídeo usando Groq Whisper API.
    
    Args:
        file_path: Caminho do arquivo
        api_key: Chave da API Groq (ou usa GROQ_API_KEY do ambiente)
        
    Returns:
        Dict com: transcription, status, language, error
        
    NOTA: Requer instalação: pip install groq
    """
    try:
        from groq import Groq
    except ImportError:
        return {
            'transcription': None,
            'status': 'error',
            'language': None,
            'error': 'Groq não instalado. Execute: pip install groq'
        }
    
    api_key = api_key or os.getenv('GROQ_API_KEY')
    
    if not api_key:
        return {
            'transcription': None,
            'status': 'error',
            'language': None,
            'error': 'GROQ_API_KEY não configurada'
        }
    
    try:
        client = Groq(api_key=api_key)
        
        with open(file_path, 'rb') as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(Path(file_path).name, audio_file.read()),
                model="whisper-large-v3",
                response_format="verbose_json"
            )
        
        return {
            'transcription': transcription.text,
            'status': 'completed',
            'language': getattr(transcription, 'language', 'unknown'),
            'error': None
        }
        
    except Exception as e:
        return {
            'transcription': None,
            'status': 'error',
            'language': None,
            'error': str(e)
        }


def merge_transcriptions(df: pd.DataFrame, df_transcriptions: pd.DataFrame) -> pd.DataFrame:
    """
    Faz merge das transcrições com o DataFrame de mensagens.
    
    Adiciona: tem_transcricao, transcricao, transcription_status, is_synthetic
    """
    df = df.copy()
    
    if df_transcriptions.empty:
        df['tem_transcricao'] = False
        df['transcricao'] = None
        df['transcription_status'] = None
        df['is_synthetic'] = False
        return df
    
    # Cria lookup por filename
    trans_lookup = df_transcriptions.set_index('filename').to_dict('index')
    
    def get_transcription_data(arquivo):
        if not arquivo or arquivo not in trans_lookup:
            return {
                'tem_transcricao': False,
                'transcricao': None,
                'transcription_status': None,
                'is_synthetic': False
            }
        
        data = trans_lookup[arquivo]
        return {
            'tem_transcricao': True,
            'transcricao': data.get('transcription'),
            'transcription_status': data.get('transcription_status'),
            'is_synthetic': data.get('is_synthetic', False)
        }
    
    # Aplica lookup
    trans_data = df['arquivo'].apply(get_transcription_data)
    
    df['tem_transcricao'] = trans_data.apply(lambda x: x['tem_transcricao'])
    df['transcricao'] = trans_data.apply(lambda x: x['transcricao'])
    df['transcription_status'] = trans_data.apply(lambda x: x['transcription_status'])
    df['is_synthetic'] = trans_data.apply(lambda x: x['is_synthetic'])
    
    return df


# =============================================================================
# FASE 5: ENRIQUECIMENTO
# =============================================================================

def enrich_content(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enriquece conteúdo e adiciona coluna de grupo de mensagem.
    
    Cria duas colunas:
    1. grupo_mensagem: Categoria limpa (AUDIO, VID, IMG, TEXT, etc.)
    2. conteudo_enriquecido: Transcrição pura OU conteúdo original
    
    Categorias:
    - TEXT: Mensagens de texto (puro, com emoji, com link)
    - AUDIO: Áudios
    - VID: Vídeos (inclui video_note)
    - IMG: Imagens
    - STICKER: Stickers
    - GIF: GIFs
    - DOC: Documentos
    - CONTACT: Contatos
    - FILE: Outros arquivos
    - SYSTEM: Mensagens do sistema
    - CALL: Chamadas (voz/vídeo/perdida)
    """
    df = df.copy()
    
    # Mapeamento tipo_mensagem → grupo_mensagem
    TAG_MAPPING = {
        # Áudio
        'audio_omitted': 'AUDIO',
        'audio_attached': 'AUDIO',
        
        # Vídeo (UNIFICADO)
        'video_omitted': 'VID',
        'video_attached': 'VID',
        'video_note_omitted': 'VID',
        
        # Imagem
        'image_omitted': 'IMG',
        'image_attached': 'IMG',
        
        # Sticker
        'sticker_omitted': 'STICKER',
        'sticker_attached': 'STICKER',
        
        # GIF
        'gif_omitted': 'GIF',
        
        # Documento
        'document_omitted': 'DOC',
        
        # Contato
        'contact_attached': 'CONTACT',
        
        # Arquivo genérico
        'file_attached': 'FILE',
        
        # Texto
        'text_pure': 'TEXT',
        'text_with_emoji': 'TEXT',
        'text_with_link': 'TEXT',
        
        # Sistema
        'message_deleted': 'SYSTEM',
        'message_edited': 'SYSTEM',
        'voice_call': 'CALL',
        'video_call': 'CALL',
        'missed_call': 'CALL',
        'system_message': 'SYSTEM',
    }
    
    def build_enriched_data(row):
        tipo = row['tipo_mensagem']
        grupo = TAG_MAPPING.get(tipo, 'OTHER')  # Fallback se tipo desconhecido
        
        # Define conteúdo baseado no grupo
        if grupo in ['AUDIO', 'VID', 'IMG', 'STICKER', 'GIF', 'DOC', 'CONTACT', 'FILE']:
            # É mídia → verifica se tem transcrição
            if row.get('tem_transcricao') and pd.notna(row.get('transcricao')):
                conteudo = row['transcricao']
            else:
                conteudo = None  # Mídia sem transcrição
        else:
            # Texto, sistema, chamadas → mantém conteúdo original
            conteudo = row['conteudo']
        
        return {'grupo_mensagem': grupo, 'conteudo_enriquecido': conteudo}
    
    # Aplica enriquecimento
    enriched_data = df.apply(build_enriched_data, axis=1)
    
    df['grupo_mensagem'] = enriched_data.apply(lambda x: x['grupo_mensagem'])
    df['conteudo_enriquecido'] = enriched_data.apply(lambda x: x['conteudo_enriquecido'])
    
    return df



# =============================================================================
# FASE 6: EXPORTAÇÃO
# =============================================================================

def export_to_csv(df: pd.DataFrame, output_path: Path, columns: list = None) -> Path:
    """Exporta DataFrame para CSV."""
    output_path = Path(output_path)
    
    if columns:
        df[columns].to_csv(output_path, index=False, encoding='utf-8')
    else:
        df.to_csv(output_path, index=False, encoding='utf-8')
    
    return output_path


def export_corpus_files(df: pd.DataFrame, output_dir: Path, use_enriched: bool = True) -> dict:
    """
    Exporta arquivos TXT de corpus.
    
    Gera:
    - chat_complete.txt: Todas as mensagens
    - chat_p1.txt: Só mensagens de P1
    - chat_p2.txt: Só mensagens de P2
    - corpus_full.txt: Apenas conteúdo (sem timestamp/remetente)
    
    Args:
        df: DataFrame com mensagens
        output_dir: Diretório de saída
        use_enriched: Se True, usa conteudo_enriquecido (com transcrições)
        
    Returns:
        Dict com paths dos arquivos gerados
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    content_col = 'conteudo_enriquecido' if use_enriched and 'conteudo_enriquecido' in df.columns else 'conteudo'
    
    files = {}
    
    # Chat completo (com timestamp e remetente)
    chat_complete = output_dir / 'chat_complete.txt'
    with open(chat_complete, 'w', encoding='utf-8') as f:
        for _, row in df.iterrows():
            data = row['timestamp'].strftime('%d/%m/%y')
            hora = row['timestamp'].strftime('%H:%M:%S')
            f.write(f"{data} {hora} {row['remetente']}: {row[content_col]}\n")
    files['chat_complete'] = chat_complete
    
    # Corpus full (só conteúdo)
    corpus_full = output_dir / 'corpus_full.txt'
    with open(corpus_full, 'w', encoding='utf-8') as f:
        for conteudo in df[content_col]:
            f.write(f"{conteudo}\n")
    files['corpus_full'] = corpus_full
    
    # Por remetente
    for remetente in df['remetente'].unique():
        df_rem = df[df['remetente'] == remetente]
        
        # Chat com timestamp
        chat_file = output_dir / f'chat_{remetente.lower()}.txt'
        with open(chat_file, 'w', encoding='utf-8') as f:
            for _, row in df_rem.iterrows():
                data = row['timestamp'].strftime('%d/%m/%y')
                hora = row['timestamp'].strftime('%H:%M:%S')
                f.write(f"{data} {hora} {row['remetente']}: {row[content_col]}\n")
        files[f'chat_{remetente.lower()}'] = chat_file
        
        # Corpus só conteúdo
        corpus_file = output_dir / f'corpus_{remetente.lower()}.txt'
        with open(corpus_file, 'w', encoding='utf-8') as f:
            for conteudo in df_rem[content_col]:
                f.write(f"{conteudo}\n")
        files[f'corpus_{remetente.lower()}'] = corpus_file
    
    return files


# =============================================================================
# COLUNAS PARA EXPORTAÇÃO
# =============================================================================

# Todas as colunas (debug/auditoria)
COLUMNS_FULL = [
    'linha_original',
    'data',
    'hora',
    'timestamp',
    'remetente',
    'conteudo',
    'tipo_mensagem',
    'arquivo',
    'arquivo_existe',
    'extensao',
    'tipo_arquivo',
    'arquivo_path',
    'tem_transcricao',
    'transcricao',
    'transcription_status',
    'is_synthetic',
    'conteudo_enriquecido',
]

# Colunas essenciais para análise
COLUMNS_CORE = [
    'timestamp',
    'remetente',
    'tipo_mensagem',
    'grupo_mensagem',      # NOVA: tags padronizadas
    'conteudo_enriquecido', # Será renomeada para 'conteudo' no export
    'arquivo',
    'tem_transcricao',      # Será renomeada para 'transcricao' (bool)
    'is_synthetic',         # Será renomeada para 'date_match'
]

# Todas as colunas (debug/auditoria) - MANTÉM conteudo original
COLUMNS_FULL = [
    'linha_original',
    'data',
    'hora',
    'timestamp',
    'remetente',
    'conteudo',             # ORIGINAL (com tags inline se quiser)
    'tipo_mensagem',
    'grupo_mensagem',       # NOVA
    'conteudo_enriquecido', # LIMPO
    'arquivo',
    'arquivo_existe',
    'extensao',
    'tipo_arquivo',
    'arquivo_path',
    'tem_transcricao',
    'transcricao',
    'transcription_status',
    'is_synthetic',
]

# Colunas mínimas (só o essencial)
COLUMNS_MINIMAL = [
    'timestamp',
    'remetente',
    'tipo_mensagem',
    'conteudo_enriquecido',
]


def export_optimized(
    df: pd.DataFrame, 
    output_dir: Path, 
    formats: list = None,
    show_progress: bool = True
) -> dict:
    """
    Exporta DataFrame em múltiplos formatos otimizados com renomeação de colunas.
    
    Renomeações aplicadas no dataset CORE/MINIMAL:
    - conteudo_enriquecido → conteudo
    - tem_transcricao → transcricao
    - is_synthetic → date_match
    """
    if formats is None:
        formats = ['csv_full', 'csv_core', 'parquet']
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    outputs = {}
    
    # Mapeamento de renomeação
    RENAME_MAP = {
        'conteudo_enriquecido': 'conteudo',
        'tem_transcricao': 'transcricao',
        'is_synthetic': 'date_match'
    }
    
    # Verifica pyarrow
    parquet_available = True
    try:
        import pyarrow
    except ImportError:
        parquet_available = False
        if any('parquet' in f for f in formats):
            print("⚠️ pyarrow não instalado. Parquet será ignorado.")
    
    if show_progress:
        print("📦 Exportando datasets otimizados...\n")
    
    def optimize_dtypes(df_subset):
        df_opt = df_subset.copy()
        
        if 'timestamp' in df_opt.columns and df_opt['timestamp'].dtype == 'object':
            df_opt['timestamp'] = pd.to_datetime(df_opt['timestamp'])
        
        # Booleans
        bool_cols = ['transcricao', 'date_match', 'arquivo_existe']  # RENOMEADOS
        for col in bool_cols:
            if col in df_opt.columns:
                df_opt[col] = df_opt[col].astype(bool)
        
        # Categorias
        cat_cols = ['remetente', 'tipo_mensagem', 'grupo_mensagem', 'tipo_arquivo', 'extensao']
        for col in cat_cols:
            if col in df_opt.columns:
                df_opt[col] = df_opt[col].astype('category')
        
        return df_opt
    
    def filter_columns(columns):
        return [c for c in columns if c in df.columns]
    
    for fmt in formats:
        if 'parquet' in fmt and not parquet_available:
            continue
            
        if fmt == 'csv_full':
            # Full: MANTÉM nomes originais + conteudo original
            path = output_dir / 'messages_full.csv'
            cols = filter_columns(COLUMNS_FULL)
            df[cols].to_csv(path, index=False, encoding='utf-8')
            
        elif fmt == 'csv_core':
            # Core: RENOMEIA colunas
            path = output_dir / 'messages.csv'
            cols = filter_columns(COLUMNS_CORE)
            df_export = df[cols].copy()
            df_export = df_export.rename(columns=RENAME_MAP)
            df_export.to_csv(path, index=False, encoding='utf-8')
            
        elif fmt == 'csv_minimal':
            path = output_dir / 'messages_minimal.csv'
            cols = filter_columns(COLUMNS_MINIMAL)
            df_export = df[cols].copy()
            df_export = df_export.rename(columns=RENAME_MAP)
            df_export.to_csv(path, index=False, encoding='utf-8')
            
        elif fmt == 'parquet':
            # Parquet: RENOMEIA colunas + otimiza tipos
            path = output_dir / 'messages.parquet'
            cols = filter_columns(COLUMNS_CORE)
            df_export = df[cols].copy()
            df_export = df_export.rename(columns=RENAME_MAP)
            df_opt = optimize_dtypes(df_export)
            df_opt.to_parquet(path, index=False, engine='pyarrow')
            
        elif fmt == 'parquet_minimal':
            path = output_dir / 'messages_minimal.parquet'
            cols = filter_columns(COLUMNS_MINIMAL)
            df_export = df[cols].copy()
            df_export = df_export.rename(columns=RENAME_MAP)
            df_opt = optimize_dtypes(df_export)
            df_opt.to_parquet(path, index=False, engine='pyarrow')
        
        else:
            continue
        
        size_bytes = path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        
        outputs[fmt] = {
            'path': path,
            'size_bytes': size_bytes,
            'size_mb': round(size_mb, 2),
            'columns': len(cols)
        }
        
        if show_progress:
            print(f"   ✅ {path.name:<30} {size_mb:>6.2f} MB ({len(cols)} cols)")
    
    if show_progress:
        print(f"\n📊 Comparação de tamanhos:")
        if 'csv_full' in outputs and 'parquet' in outputs:
            ratio = outputs['csv_full']['size_mb'] / outputs['parquet']['size_mb']
            print(f"   • CSV Full / Parquet: {ratio:.1f}x maior")
    
    return outputs


def get_export_summary(outputs: dict) -> pd.DataFrame:
    """
    Gera DataFrame com resumo dos arquivos exportados.
    
    Args:
        outputs: Dict retornado por export_optimized()
        
    Returns:
        DataFrame com: formato, arquivo, tamanho_mb, colunas
    """
    rows = []
    for fmt, info in outputs.items():
        rows.append({
            'formato': fmt,
            'arquivo': info['path'].name,
            'tamanho_mb': info['size_mb'],
            'colunas': info['columns']
        })
    
    return pd.DataFrame(rows)


# =============================================================================
# REGISTRO DE ETAPAS DO PIPELINE
# =============================================================================

WRANGLING_STEPS = {
    'parse': {
        'name': 'Parsing TXT → DataFrame',
        'description': '''Converte arquivo TXT limpo em DataFrame estruturado.
Agrega linhas de continuação (mensagens multilinha) e cria timestamp datetime.'''
    },
    'classify': {
        'name': 'Classificação de mensagens',
        'description': 'Classifica cada mensagem por tipo (21 tipos possíveis).'
    },
    'media': {
        'name': 'Vinculação de mídia',
        'description': '''Vincula arquivos físicos de mídia às mensagens.
Verifica existência, extrai metadados (extensão, tipo, tamanho).'''
    },
    'transcriptions': {
        'name': 'Integração de transcrições',
        'description': '''Carrega transcrições existentes e faz merge com mensagens.
Suporta transcrições via Groq/Whisper API ou CSV pré-existente.'''
    },
    'enrich': {
        'name': 'Enriquecimento de conteúdo',
        'description': '''Cria coluna `grupo_mensagem` com categorias padronizadas e enriquece conteúdo.

    **Categorias:** `TEXT`, `AUDIO`, `VID`, `IMG`, `STICKER`, `GIF`, `DOC`, `CONTACT`, `FILE`, `SYSTEM`, `CALL`

    **Regras:**
    - Mídia com transcrição → transcrição no conteúdo
    - Mídia sem transcrição → conteúdo vazio
    - Texto/sistema → conteúdo original'''
    },
    'export': {
        'name': 'Exportação de arquivos',
        'description': 'Exporta datasets em múltiplos formatos (CSV, Parquet, TXT).'
    },
}


# =============================================================================
# EXECUTOR DO PIPELINE
# =============================================================================

def run_wrangling_pipeline(
    order: list,
    input_file: Path,
    output_dir: Path,
    media_dir: Path = None,
    transcription_file: Path = None,
    show_progress: bool = True
) -> dict:
    """
    Executa pipeline de wrangling na ordem especificada.
    
    Args:
        order: Lista de IDs das etapas. 
               Ex: ['parse', 'classify', 'media', 'transcriptions', 'enrich', 'export']
        input_file: Path do arquivo TXT limpo (saída do cleaning)
        output_dir: Path do diretório para outputs
        media_dir: Path do diretório com arquivos de mídia
        transcription_file: Path do CSV com transcrições existentes
        show_progress: Se True, imprime progresso
        
    Returns:
        Dict com:
        - df: DataFrame final
        - outputs: Dict com paths dos arquivos gerados
        - stats: Estatísticas do processamento
    """
    # Valida IDs
    invalid = [s for s in order if s not in WRANGLING_STEPS]
    if invalid:
        raise ValueError(f"Etapas inválidas: {invalid}. Disponíveis: {list(WRANGLING_STEPS.keys())}")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    df = None
    outputs = {}
    stats = {}
    
    if show_progress:
        print(f"🔄 Executando pipeline de wrangling com {len(order)} etapas...\n")
    
    for i, step_id in enumerate(order):
        step = WRANGLING_STEPS[step_id]
        step_num = i + 1
        
        if show_progress:
            print(f"   {step_num}. {step['name']}...", end=' ')
        
        # Executa etapa
        if step_id == 'parse':
            df = parse_to_dataframe(input_file)
            stats['total_linhas_txt'] = sum(1 for _ in open(input_file, 'r', encoding='utf-8'))
            stats['total_mensagens'] = len(df)
            if show_progress:
                print(f"✅ ({stats['total_mensagens']:,} mensagens)")
        
        elif step_id == 'classify':
            df = add_message_classification(df)
            stats['tipos_mensagem'] = df['tipo_mensagem'].value_counts().to_dict()
            if show_progress:
                print(f"✅ ({df['tipo_mensagem'].nunique()} tipos)")
        
        elif step_id == 'media':
            if media_dir:
                df = link_media_to_messages(df, Path(media_dir))
                stats['midias_anexadas'] = df['arquivo'].notna().sum()
                stats['midias_existentes'] = df['arquivo_existe'].sum()
                if show_progress:
                    print(f"✅ ({stats['midias_existentes']:,} arquivos encontrados)")
            else:
                if show_progress:
                    print("⏭️ (sem diretório de mídia)")
        
        elif step_id == 'transcriptions':
            if transcription_file:
                trans_path = Path(transcription_file)
                
                if trans_path.exists():
                    # Arquivo existe — carrega e faz merge
                    df_trans = load_transcriptions(trans_path)
                    df = merge_transcriptions(df, df_trans)
                    stats['com_transcricao'] = df['tem_transcricao'].sum()
                    if show_progress:
                        print(f"✅ ({stats['com_transcricao']:,} transcrições)")
                else:
                    # Arquivo configurado mas não existe — orienta o usuário
                    if show_progress:
                        print(f"⚠️ Arquivo não encontrado")
                        print(f"\n   ┌─────────────────────────────────────────────────────┐")
                        print(f"   │  Para transcrever os áudios/vídeos:                 │")
                        print(f"   │  1. Execute: python scripts/transcribe_media.py    │")
                        print(f"   │  2. Aguarde o processamento (~40 min)              │")
                        print(f"   │  3. Rode este notebook novamente                   │")
                        print(f"   └─────────────────────────────────────────────────────┘")
                        print(f"   Esperado em: {trans_path}\n")
                    
                    # Continua sem transcrições
                    df['tem_transcricao'] = False
                    df['transcricao'] = None
                    df['transcription_status'] = None
                    df['is_synthetic'] = False
                    stats['com_transcricao'] = 0
            else:
                df['tem_transcricao'] = False
                df['transcricao'] = None
                df['transcription_status'] = None
                df['is_synthetic'] = False
                if show_progress:
                    print("⏭️ (sem arquivo de transcrições)")
        
        elif step_id == 'enrich':
            df = enrich_content(df)
            stats['mensagens_enriquecidas'] = (df['conteudo'] != df['conteudo_enriquecido']).sum()
            if show_progress:
                print(f"✅ ({stats['mensagens_enriquecidas']:,} enriquecidas)")
        
        elif step_id == 'export':
            # Datasets otimizados (CSV + Parquet)
            optimized_outputs = export_optimized(
                df, output_dir, 
                formats=['csv_full', 'csv_core', 'parquet'],
                show_progress=False
            )
            for fmt, info in optimized_outputs.items():
                outputs[fmt] = info['path']
            
            # Arquivos de corpus (TXTs)
            corpus_files = export_corpus_files(df, output_dir, use_enriched=True)
            outputs.update(corpus_files)
            
            stats['export_summary'] = optimized_outputs
            
            if show_progress:
                print(f"✅ ({len(outputs)} arquivos)")
    
    if show_progress:
        print(f"\n✅ Pipeline concluído!")
        print(f"   📊 Total de mensagens: {len(df):,}")
        if 'com_transcricao' in stats:
            print(f"   🎙️ Com transcrição: {stats['com_transcricao']:,}")
        print(f"   📁 Arquivos gerados: {len(outputs)}")
        
        # Mostra comparação de tamanhos
        if 'export_summary' in stats:
            print(f"\n   📦 Tamanhos:")
            for fmt, info in stats['export_summary'].items():
                print(f"      • {info['path'].name}: {info['size_mb']:.2f} MB")
    
    return {
        'df': df,
        'outputs': outputs,
        'stats': stats,
        'order': order
    }


def get_available_steps() -> list:
    """Retorna lista de IDs de etapas disponíveis."""
    return list(WRANGLING_STEPS.keys())