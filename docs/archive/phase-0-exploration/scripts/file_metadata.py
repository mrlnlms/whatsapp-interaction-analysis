"""
Módulo para análise de metadados de arquivos.
Fornece informações básicas sobre o arquivo sem processar seu conteúdo.
"""

import os
from datetime import datetime
from pathlib import Path


def get_file_size_formatted(size_bytes):
    """
    Converte tamanho em bytes para formato legível.
    
    Args:
        size_bytes (int): Tamanho em bytes
        
    Returns:
        str: Tamanho formatado (B, KB, MB, GB, TB)
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def count_lines_fast(file_path):
    """
    Conta linhas do arquivo de forma eficiente.
    
    Args:
        file_path (str): Caminho do arquivo
        
    Returns:
        int: Número total de linhas
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f)


def get_file_metadata(file_path='raw-data.txt'):
    """
    Extrai metadados básicos do arquivo sem processar seu conteúdo.
    
    Args:
        file_path (str): Caminho para o arquivo
        
    Returns:
        dict: Dicionário com metadados do arquivo
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
    
    # Informações do sistema de arquivos
    file_stats = os.stat(file_path)
    path_obj = Path(file_path)
    
    # Datas
    creation_time = datetime.fromtimestamp(file_stats.st_ctime)
    modification_time = datetime.fromtimestamp(file_stats.st_mtime)
    access_time = datetime.fromtimestamp(file_stats.st_atime)
    
    # Tamanhos
    size_bytes = file_stats.st_size
    size_formatted = get_file_size_formatted(size_bytes)
    
    # Contagem de linhas
    total_lines = count_lines_fast(file_path)
    
    metadata = {
        'file_name': path_obj.name,
        'file_path': str(path_obj.absolute()),
        'file_extension': path_obj.suffix,
        'size_bytes': size_bytes,
        'size_formatted': size_formatted,
        'total_lines': total_lines,
        'creation_date': creation_time.strftime('%d/%m/%Y %H:%M:%S'),
        'modification_date': modification_time.strftime('%d/%m/%Y %H:%M:%S'),
        'last_access_date': access_time.strftime('%d/%m/%Y %H:%M:%S'),
    }
    
    return metadata


def calculate_line_statistics(file_path='raw-data.txt'):
    """
    Calcula estatísticas sobre o tamanho das linhas do arquivo.
    
    Args:
        file_path (str): Caminho para o arquivo
        
    Returns:
        dict: Estatísticas de tamanho por linha
    """
    import statistics
    
    line_sizes = []
    line_bytes = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line_sizes.append(len(line))
            line_bytes.append(len(line.encode('utf-8')))
    
    # Calcula estatísticas
    stats = {
        'mean': statistics.mean(line_sizes),
        'median': statistics.median(line_sizes),
        'mode': statistics.mode(line_sizes) if line_sizes else 0,
        'min': min(line_sizes) if line_sizes else 0,
        'max': max(line_sizes) if line_sizes else 0,
        'total_chars': sum(line_sizes),
        'bytes_mean': statistics.mean(line_bytes),
        'bytes_median': statistics.median(line_bytes),
        'bytes_mode': statistics.mode(line_bytes) if line_bytes else 0,
    }
    
    return stats


def print_file_overview(file_path='raw-data.txt'):
    """
    Imprime visão geral do arquivo com metadados e estatísticas básicas.
    
    Args:
        file_path (str): Caminho para o arquivo
    """
    try:
        metadata = get_file_metadata(file_path)
        line_stats = calculate_line_statistics(file_path)
        
        print("=" * 70)
        print("OVERVIEW DO ARQUIVO - METADADOS")
        print("=" * 70)
        print()
        print(f"📁 Nome do arquivo: {metadata['file_name']}")
        print(f"📂 Caminho completo: {metadata['file_path']}")
        print(f"📝 Extensão: {metadata['file_extension']}")
        print()
        print(f"📊 Tamanho: {metadata['size_formatted']} ({metadata['size_bytes']:,} bytes)")
        print(f"📏 Total de linhas: {metadata['total_lines']:,}")
        print()
        print(f"📅 Data de criação: {metadata['creation_date']}")
        print(f"📅 Última modificação: {metadata['modification_date']}")
        print(f"📅 Último acesso: {metadata['last_access_date']}")
        print()
        print("=" * 70)
        print("ESTATÍSTICAS DE DENSIDADE POR LINHA")
        print("=" * 70)
        print()
        print(f"📈 Caracteres totais: {line_stats['total_chars']:,}")
        print(f"📊 Média de caracteres/linha: {line_stats['mean']:.2f}")
        print(f"📊 Mediana de caracteres/linha: {line_stats['median']:.2f}")
        print(f"📊 Moda de caracteres/linha: {line_stats['mode']:.0f}")
        print()
        print(f"⬇️  Linha mais curta: {line_stats['min']} caracteres")
        print(f"⬆️  Linha mais longa: {line_stats['max']} caracteres")
        print()
        
        # Cálculos derivados
        avg_bytes_per_line = metadata['size_bytes'] / metadata['total_lines']
        print(f"💾 Média de bytes/linha: {avg_bytes_per_line:.2f}")
        print(f"💾 Mediana de bytes/linha: {line_stats['bytes_median']:.2f}")
        print(f"💾 Moda de bytes/linha: {line_stats['bytes_mode']:.0f}")
        
        print("=" * 70)
        
        return metadata, line_stats
        
    except FileNotFoundError as e:
        print(f"❌ Erro: {e}")
        return None, None
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def interpret_statistics(metadata, line_stats):
    """
    Fornece interpretação contextual das estatísticas.
    
    Args:
        metadata (dict): Metadados do arquivo
        line_stats (dict): Estatísticas de linha
    """
    print("\n💡 INTERPRETAÇÃO DOS DADOS")
    print("=" * 70)
    
    # Análise de tamanho
    size_mb = metadata['size_bytes'] / (1024 * 1024)
    if size_mb < 1:
        print("• Arquivo relativamente pequeno (< 1MB)")
    elif size_mb < 10:
        print("• Arquivo de tamanho médio (1-10MB)")
    else:
        print("• Arquivo grande (> 10MB) - processamento pode demorar")
    
    # Análise de densidade
    avg_chars = line_stats['mean']
    if avg_chars < 50:
        print("• Linhas curtas em média - muitas mensagens breves ou linhas vazias")
    elif avg_chars < 100:
        print("• Linhas de tamanho moderado - mensagens típicas de chat")
    else:
        print("• Linhas longas em média - mensagens extensas ou multilinha")
    
    # Variabilidade
    variance = line_stats['max'] - line_stats['min']
    if variance > 500:
        print("• Alta variabilidade no tamanho das linhas")
        print("  → Indica mensagens muito heterogêneas (de curtas a muito longas)")
    
    # Densidade vs tamanho total
    density_ratio = line_stats['mean'] / avg_chars if avg_chars > 0 else 0
    
    print(f"\n• Densidade de informação: {line_stats['mean']:.0f} caracteres/linha")
    print(f"• Eficiência de armazenamento: {(metadata['total_lines'] / metadata['size_bytes'] * 1000):.2f} linhas/KB")
    
    print("=" * 70)


def get_metadata_for_quarto(file_path='raw-data.txt'):
    """
    Retorna metadados e estatísticas formatados para uso no Quarto.
    
    Args:
        file_path (str): Caminho do arquivo
        
    Returns:
        tuple: (dict_info_geral, dict_densidade)
    """
    metadata = get_file_metadata(file_path)
    line_stats = calculate_line_statistics(file_path)
    
    # Informações gerais do arquivo
    info_geral = {
        'Propriedade': ['Nome do arquivo', 'Extensão', 'Tamanho', 'Total de linhas', 
                       'Data de criação', 'Última modificação'],
        'Valor': [
            metadata['file_name'],
            metadata['file_extension'],
            metadata['size_formatted'],
            f"{metadata['total_lines']:,}",
            metadata['creation_date'],
            metadata['modification_date']
        ]
    }
    
    # Estatísticas de densidade
    avg_bytes_per_line = metadata['size_bytes'] / metadata['total_lines']
    
    densidade = {
        'Métrica': [
            'Caracteres totais',
            'Média caracteres/linha', 
            'Mediana caracteres/linha',
            'Moda caracteres/linha',
            'Linha mais curta',
            'Linha mais longa',
            'Média bytes/linha',
            'Mediana bytes/linha',
            'Moda bytes/linha'
        ],
        'Valor': [
            f"{line_stats['total_chars']:,}",
            f"{line_stats['mean']:.2f}",
            f"{line_stats['median']:.2f}",
            f"{line_stats['mode']:.0f}",
            f"{line_stats['min']} caracteres",
            f"{line_stats['max']} caracteres",
            f"{avg_bytes_per_line:.2f}",
            f"{line_stats['bytes_median']:.2f}",
            f"{line_stats['bytes_mode']:.0f}"
        ]
    }
    
    return info_geral, densidade


if __name__ == "__main__":
    metadata, line_stats = print_file_overview('raw-data.txt')
    if metadata and line_stats:
        interpret_statistics(metadata, line_stats)