"""
Funções de Data Profiling para investigação de arquivos brutos.

Este módulo fornece ferramentas para explorar e entender a estrutura
de arquivos de texto antes de iniciar o processo de limpeza.
"""

import re
import os
import pandas as pd
from typing import Optional

from whatsapp.pipeline.utils.file_helpers import format_bytes, get_file_overview


def get_lines_at_position(file_path: str, position: int = 0, n: int = 5) -> pd.DataFrame:
    """
    Retorna n linhas de uma posição percentual do arquivo.
    
    Args:
        file_path: Caminho do arquivo
        position: Posição percentual (0-100)
        n: Número de linhas a retornar
        
    Returns:
        DataFrame com número da linha e conteúdo
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    total_lines = len(lines)
    start_idx = int((position / 100) * total_lines)
    
    # Ajusta para não ultrapassar o final
    start_idx = min(start_idx, total_lines - n)
    start_idx = max(0, start_idx)
    
    result = []
    for i in range(start_idx, min(start_idx + n, total_lines)):
        result.append({
            'linha': i + 1,
            'conteudo': lines[i].rstrip('\n')
        })
    
    return pd.DataFrame(result)


def get_lines_containing(file_path: str, substring: str, n: int = 5) -> pd.DataFrame:
    """
    Retorna n linhas que contêm o substring especificado.
    
    Args:
        file_path: Caminho do arquivo
        substring: Texto a buscar
        n: Número máximo de linhas a retornar
        
    Returns:
        DataFrame com número da linha e conteúdo
    """
    matches = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if substring in line:
                matches.append({
                    'linha': i,
                    'conteudo': line.rstrip('\n')
                })
                if len(matches) >= n:
                    break
    
    if not matches:
        print(f"⚠️ Nenhuma linha encontrada contendo: '{substring}'")
        return pd.DataFrame(columns=['linha', 'conteudo'])
    
    return pd.DataFrame(matches)


def get_lines_matching(file_path: str, pattern: str, n: int = 5) -> pd.DataFrame:
    """
    Retorna n linhas que casam com o padrão regex.
    
    Args:
        file_path: Caminho do arquivo
        pattern: Padrão regex
        n: Número máximo de linhas a retornar
        
    Returns:
        DataFrame com número da linha e conteúdo
    """
    matches = []
    regex = re.compile(pattern)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if regex.search(line):
                matches.append({
                    'linha': i,
                    'conteudo': line.rstrip('\n')
                })
                if len(matches) >= n:
                    break
    
    if not matches:
        print(f"⚠️ Nenhuma linha encontrada com padrão: '{pattern}'")
        return pd.DataFrame(columns=['linha', 'conteudo'])
    
    return pd.DataFrame(matches)


def count_pattern(file_path: str, pattern: str) -> dict:
    """
    Conta ocorrências de um padrão no arquivo.
    
    Args:
        file_path: Caminho do arquivo
        pattern: Padrão regex ou string literal
        
    Returns:
        Dict com total de ocorrências e linhas afetadas
    """
    total = 0
    lines_with = 0
    
    # Tenta compilar como regex, senão usa como string literal
    try:
        regex = re.compile(pattern)
        use_regex = True
    except re.error:
        use_regex = False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if use_regex:
                found = len(regex.findall(line))
            else:
                found = line.count(pattern)
            
            total += found
            if found > 0:
                lines_with += 1
    
    return {
        'total_ocorrencias': total,
        'linhas_com_pattern': lines_with
    }


def multi_position_preview(file_path: str, 
                           n_lines: int = 5, 
                           positions: list = [0, 25, 50, 75, 100]) -> pd.DataFrame:
    """
    Retorna preview do arquivo em múltiplas posições percentuais.
    
    Args:
        file_path: Caminho do arquivo
        n_lines: Linhas por posição
        positions: Lista de posições percentuais
        
    Returns:
        DataFrame consolidado com separadores entre posições
    """
    all_previews = []
    
    for pos in positions:
        preview = get_lines_at_position(file_path, position=pos, n=n_lines)
        preview['posicao'] = f"{pos}%"
        all_previews.append(preview)
        
        # Adiciona linha separadora (exceto após última posição)
        if pos != positions[-1]:
            separator = pd.DataFrame([{
                'linha': '...',
                'conteudo': '─' * 50,
                'posicao': ''
            }])
            all_previews.append(separator)
    
    return pd.concat(all_previews, ignore_index=True)


def analyze_line_patterns(file_path: str) -> dict:
    """
    Analisa padrões gerais das linhas do arquivo.
    
    Returns:
        Dict com estatísticas de padrões encontrados
    """
    patterns = {
        'com_timestamp': 0,
        'sem_timestamp': 0,
        'vazias': 0,
        'com_midia_omitida': 0,
        'com_midia_anexada': 0,
        'com_emoji': 0,
        'com_link': 0
    }
    
    timestamp_pattern = re.compile(r'^\[?\d{2}/\d{2}/\d{2}')
    media_omitted = re.compile(r'(audio|image|video|sticker|GIF|document) omitted')
    media_attached = re.compile(r'<attached:')
    url_pattern = re.compile(r'https?://')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            
            if not stripped:
                patterns['vazias'] += 1
                continue
            
            if timestamp_pattern.match(line):
                patterns['com_timestamp'] += 1
            else:
                patterns['sem_timestamp'] += 1
            
            if media_omitted.search(line):
                patterns['com_midia_omitida'] += 1
            
            if media_attached.search(line):
                patterns['com_midia_anexada'] += 1
            
            if url_pattern.search(line):
                patterns['com_link'] += 1
            
            # Emoji: caracteres com ord > 127 (simplificado)
            if any(ord(c) > 127 for c in line):
                patterns['com_emoji'] += 1
    
    return patterns


def print_pattern_summary(file_path: str):
    """
    Imprime resumo formatado dos padrões encontrados.
    """
    patterns = analyze_line_patterns(file_path)
    
    total = patterns['com_timestamp'] + patterns['sem_timestamp'] + patterns['vazias']
    
    print("=" * 60)
    print("📊 RESUMO DE PADRÕES DO ARQUIVO")
    print("=" * 60)
    print(f"\n📝 Estrutura de linhas:")
    print(f"   • Com timestamp: {patterns['com_timestamp']:,} ({patterns['com_timestamp']/total*100:.1f}%)")
    print(f"   • Sem timestamp (continuação): {patterns['sem_timestamp']:,} ({patterns['sem_timestamp']/total*100:.1f}%)")
    print(f"   • Vazias: {patterns['vazias']:,} ({patterns['vazias']/total*100:.1f}%)")
    
    print(f"\n📎 Mídias:")
    print(f"   • Omitidas: {patterns['com_midia_omitida']:,}")
    print(f"   • Anexadas: {patterns['com_midia_anexada']:,}")
    
    print(f"\n🔗 Conteúdo especial:")
    print(f"   • Com links: {patterns['com_link']:,}")
    print(f"   • Com emoji/caracteres especiais: {patterns['com_emoji']:,}")
    print("=" * 60)
