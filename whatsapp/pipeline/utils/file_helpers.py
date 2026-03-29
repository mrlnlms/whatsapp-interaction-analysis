"""
Funções auxiliares para análise de arquivos.
"""

import os
import statistics


def format_bytes(size: int) -> str:
    """Formata bytes para unidade legível."""
    if size < 0:
        return f"-{format_bytes(-size)}"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"


def get_file_overview(file_path: str) -> dict:
    """
    Retorna visão geral do arquivo com metadados básicos.
    
    Args:
        file_path: Caminho do arquivo
        
    Returns:
        Dict com métricas do arquivo
    """
    size_bytes = os.path.getsize(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    total_lines = len(lines)
    total_chars = sum(len(line) for line in lines)
    non_empty_lines = sum(1 for line in lines if line.strip())
    
    # Estatísticas de comprimento de linha
    line_lengths = [len(line) for line in lines]
    avg_line_length = sum(line_lengths) / len(line_lengths) if line_lengths else 0
    
    result = {
        'arquivo': file_path,
        'tamanho_bytes': size_bytes,
        'tamanho_formatted': format_bytes(size_bytes),
        'total_linhas': total_lines,
        'linhas_nao_vazias': non_empty_lines,
        'linhas_vazias': total_lines - non_empty_lines,
        'total_caracteres': total_chars,
        'media_chars_por_linha': round(avg_line_length, 1)
    }
    
    # Print formatado
    print("=" * 60)
    print("📊 VISÃO GERAL DO ARQUIVO")
    print("=" * 60)
    print(f"📄 Arquivo: {file_path}")
    print(f"💾 Tamanho: {result['tamanho_formatted']} ({size_bytes:,} bytes)")
    print(f"📝 Linhas: {total_lines:,} (vazias: {result['linhas_vazias']:,})")
    print(f"🔤 Caracteres: {total_chars:,}")
    print(f"📏 Média chars/linha: {avg_line_length:.1f}")
    print("=" * 60)
    
    return result


def get_file_density_stats(file_path: str) -> dict:
    """
    Calcula estatísticas de densidade do arquivo.
    
    Args:
        file_path: Caminho do arquivo
        
    Returns:
        Dict com estatísticas de densidade
    """
    line_sizes = []
    line_bytes = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line_sizes.append(len(line))
            line_bytes.append(len(line.encode('utf-8')))
    
    # Metadados básicos
    size_bytes = os.path.getsize(file_path)
    total_lines = len(line_sizes)
    total_chars = sum(line_sizes)
    
    # Estatísticas de caracteres
    stats = {
        'total_caracteres': total_chars,
        'media_chars_linha': statistics.mean(line_sizes) if line_sizes else 0,
        'mediana_chars_linha': statistics.median(line_sizes) if line_sizes else 0,
        'moda_chars_linha': statistics.mode(line_sizes) if line_sizes else 0,
        'linha_mais_curta': min(line_sizes) if line_sizes else 0,
        'linha_mais_longa': max(line_sizes) if line_sizes else 0,
        'media_bytes_linha': size_bytes / total_lines if total_lines > 0 else 0,
        'mediana_bytes_linha': statistics.median(line_bytes) if line_bytes else 0,
        'moda_bytes_linha': statistics.mode(line_bytes) if line_bytes else 0,
    }
    
    # Print formatado
    print("=" * 60)
    print("📊 ESTATÍSTICAS DE DENSIDADE")
    print("=" * 60)
    print(f"🔤 Caracteres totais: {stats['total_caracteres']:,}")
    print(f"📊 Média chars/linha: {stats['media_chars_linha']:.2f}")
    print(f"📊 Mediana chars/linha: {stats['mediana_chars_linha']:.2f}")
    print(f"📊 Moda chars/linha: {stats['moda_chars_linha']:.0f}")
    print(f"⬇️  Linha mais curta: {stats['linha_mais_curta']} caracteres")
    print(f"⬆️  Linha mais longa: {stats['linha_mais_longa']} caracteres")
    print(f"💾 Média bytes/linha: {stats['media_bytes_linha']:.2f}")
    print(f"💾 Mediana bytes/linha: {stats['mediana_bytes_linha']:.2f}")
    print(f"💾 Moda bytes/linha: {stats['moda_bytes_linha']:.0f}")
    print("=" * 60)
    
    return stats