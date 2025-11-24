"""
Configurações centralizadas do projeto WhatsApp DS Analytics.

Lê configurações do arquivo .env na raiz do projeto

Este módulo contém todas as constantes, paths e thresholds usados
ao longo do pipeline, facilitando ajustes e manutenção.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# =============================================================================
# 🔧 PATHS (lidos do .env)
# =============================================================================

PROJECT_ROOT = Path(os.getenv('PROJECT_ROOT'))
DATA_FOLDER = os.getenv('DATA_FOLDER')

# =============================================================================
# PATHS DERIVADOS (não precisa mexer)
# =============================================================================

PATHS = {
    'src': PROJECT_ROOT / 'src',
    'raw': PROJECT_ROOT / 'data' / 'raw' / DATA_FOLDER / 'raw-data.txt',
    'media': PROJECT_ROOT / 'data' / 'raw' / DATA_FOLDER / 'media',
    'interim': PROJECT_ROOT / 'data' / 'interim' / DATA_FOLDER,
    'processed': PROJECT_ROOT / 'data' / 'processed' / DATA_FOLDER,
    'integrated': PROJECT_ROOT / 'data' / 'integrated',
    'analysis': PROJECT_ROOT / 'analysis',
}

# =============================================================================
# PARTICIPANTES
# =============================================================================

PARTICIPANTES = {
    'P1': {
        'nome': 'Marlon',
        'cor': '#2E86AB',
        'cor_light': '#A8D5E5'
    },
    'P2': {
        'nome': 'Letícia', 
        'cor': '#E84855',
        'cor_light': '#F5A8AE'
    }
}

# Mapeamento para anonimização (nomes originais → P1/P2)
# Ajuste conforme necessário
NOME_PARA_ANONIMO = {
    'Marlon': 'P1',
    'Lê 🖤': 'P2',
    # Adicione variações se houver
}

# =============================================================================
# THRESHOLDS PARA FEATURES
# =============================================================================

THRESHOLDS = {
    # Tempo de resposta rápida (em segundos)
    'reply_quick_seconds': 300,  # 5 minutos
    
    # Gap para considerar nova conversa (em horas)
    'conversation_gap_hours': 2,
    
    # Categorização de tamanho de mensagem (por word_count)
    'msg_size': {
        'vazia': 0,
        'curta': 10,      # 1-10 palavras
        'media': 30,      # 11-30 palavras
        'longa': 100,     # 31-100 palavras
        # > 100 = 'muito_longa'
    },
    
    # Mínimo de letras para considerar ALL_CAPS
    'min_letters_all_caps': 3
}


# =============================================================================
# PERÍODOS DO DIA
# =============================================================================

PERIODOS_DIA = {
    'Madrugada': (0, 6),   # 00:00 - 05:59
    'Manhã': (6, 12),      # 06:00 - 11:59
    'Tarde': (12, 18),     # 12:00 - 17:59
    'Noite': (18, 24)      # 18:00 - 23:59
}


# =============================================================================
# DIAS DA SEMANA
# =============================================================================

DIAS_SEMANA = {
    0: 'Segunda',
    1: 'Terça',
    2: 'Quarta',
    3: 'Quinta',
    4: 'Sexta',
    5: 'Sábado',
    6: 'Domingo'
}

MESES = {
    1: 'Janeiro',
    2: 'Fevereiro', 
    3: 'Março',
    4: 'Abril',
    5: 'Maio',
    6: 'Junho',
    7: 'Julho',
    8: 'Agosto',
    9: 'Setembro',
    10: 'Outubro',
    11: 'Novembro',
    12: 'Dezembro'
}


# =============================================================================
# PADRÕES REGEX
# =============================================================================

REGEX_PATTERNS = {
    # Timestamp original: [DD/MM/YY, HH:MM:SS]
    'timestamp_original': r'^\[(\d{2}/\d{2}/\d{2}), (\d{2}:\d{2}:\d{2})\]',
    
    # Timestamp otimizado: DD/MM/YY HH:MM:SS
    'timestamp_otimizado': r'^(\d{2}/\d{2}/\d{2}) (\d{2}:\d{2}:\d{2})',
    
    # Mensagem completa (após otimização)
    'mensagem_completa': r'^(\d{2}/\d{2}/\d{2}) (\d{2}:\d{2}:\d{2}) (.+?): (.*)$',
    
    # Mídia omitida
    'midia_omitida': r'(audio|image|video|sticker|GIF|document|video note) omitted',
    
    # Mídia anexada
    'midia_anexada': r'<attached: (.+?)>',
    
    # URL
    'url': r'https?://[^\s]+',
    
    # Caractere invisível
    'u200e': '\u200e',
    
    # Mensagem editada
    'editada': r'<This message was edited>',
    
    # Mensagem deletada
    'deletada': r'This message was deleted'
}


# =============================================================================
# TIPOS DE MÍDIA
# =============================================================================

TIPOS_MIDIA = {
    'text': 'Texto',
    'audio': 'Áudio',
    'video': 'Vídeo',
    'image': 'Imagem',
    'sticker': 'Sticker',
    'GIF': 'GIF',
    'document': 'Documento',
    'contact': 'Contato',
    'video note': 'Vídeo Note'
}

STATUS_MIDIA = {
    '-': 'Texto (sem mídia)',
    'omitted': 'Mídia omitida',
    'attached': 'Mídia anexada',
    'transcribed': 'Mídia transcrita'
}


# =============================================================================
# CONFIGURAÇÕES DE VISUALIZAÇÃO
# =============================================================================

VIZ_CONFIG = {
    'figsize_default': (12, 8),
    'figsize_wide': (16, 8),
    'figsize_square': (10, 10),
    
    'font_title': 16,
    'font_label': 12,
    'font_tick': 10,
    
    'dpi': 100,
    'style': 'seaborn-v0_8-whitegrid'
}


# =============================================================================
# MÁXIMOS TEÓRICOS PARA NORMALIZAÇÃO (Radar Chart)
# =============================================================================

RADAR_MAXIMOS = {
    'Verbosidade': 100,       # char_count médio máximo esperado
    'Expressividade': 0.5,    # % de msgs com emoji
    'Intensidade': 0.15,      # % de msgs com !
    'Curiosidade': 0.15,      # % de msgs com ?
    'Rapidez': 1.0,           # % de respostas rápidas
    'Iniciativa': 0.05,       # % de inícios de conversa
    'Positividade': 4.0,      # sentiment_score ajustado (range -2 a 2 → 0 a 4)
    'Mídia variada': 0.5      # % de msgs que não são texto
}
