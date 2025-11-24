"""
Script para análise inicial dos dados brutos exportados do WhatsApp.
Este módulo faz a leitura do arquivo raw-data.txt e gera métricas básicas.
"""

import os
#from pathlib import Path
from datetime import datetime


def get_file_size_formatted(size_bytes):
    """
    Converte tamanho em bytes para formato legível (KB, MB, GB).
    
    Args:
        size_bytes (int): Tamanho em bytes
        
    Returns:
        str: Tamanho formatado com unidade apropriada
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def analyze_raw_data(file_path='raw-data.txt'):
    """
    Analisa o arquivo bruto do WhatsApp e retorna métricas básicas.
    
    Args:
        file_path (str): Caminho para o arquivo raw-data.txt
        
    Returns:
        dict: Dicionário com métricas do arquivo
    """
    # Verifica se o arquivo existe
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
    
    # Obtém informações do arquivo
    file_stats = os.stat(file_path)
    file_size_bytes = file_stats.st_size
    file_size_formatted = get_file_size_formatted(file_size_bytes)
    
    # Data de modificação do arquivo
    modification_time = datetime.fromtimestamp(file_stats.st_mtime)
    
    # Lê o arquivo e conta linhas
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    total_lines = len(lines)
    
    # Conta linhas não vazias
    # non_empty_lines = sum(1 for line in lines if line.strip())
    
    # Primeiras linhas para preview (primeiras 20 linhas não vazias)
    preview_lines = [line.strip() for line in lines if line.strip()][:20]
    
    # Retorna métricas
    metrics = {
        'file_path': file_path,
        'file_size_bytes': file_size_bytes,
        'file_size_formatted': file_size_formatted,
        'total_lines': total_lines,
        # 'non_empty_lines': non_empty_lines,
        # 'empty_lines': total_lines - non_empty_lines,
        'modification_date': modification_time.strftime('%d/%m/%Y %H:%M:%S'),
        'preview': preview_lines
    }
    
    return metrics


def print_metrics(metrics):
    """
    Imprime as métricas de forma formatada.
    
    Args:
        metrics (dict): Dicionário com métricas do arquivo
    """
    print("=" * 70)
    print("ANÁLISE INICIAL DOS DADOS BRUTOS - WHATSAPP")
    print("=" * 70)
    print()
    print(f"📁 Arquivo: {metrics['file_path']}")
    print(f"📊 Tamanho: {metrics['file_size_formatted']} ({metrics['file_size_bytes']:,} bytes)")
    print(f"📅 Última modificação: {metrics['modification_date']}")
    print()
    print(f"📝 Total de linhas: {metrics['total_lines']:,}")
    # print(f"   • Linhas com conteúdo: {metrics['non_empty_lines']:,}")
    # print(f"   • Linhas vazias: {metrics['empty_lines']:,}")
    print()
    print("📋 Preview das primeiras linhas:")
    print("-" * 70)
    for i, line in enumerate(metrics['preview'], 1):
        # Trunca linhas muito longas para melhor visualização
        display_line = line if len(line) <= 100 else line[:97] + "..."
        print(f"{i}. {display_line}")
    print("=" * 70)


def main():
    """Função principal para execução standalone."""
    try:
        metrics = analyze_raw_data('raw-data.txt')
        print_metrics(metrics)
        return metrics
    except FileNotFoundError as e:
        print(f"❌ Erro: {e}")
        print("\nCertifique-se de que o arquivo 'raw-data.txt' está no diretório atual.")
        return None
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return None


if __name__ == "__main__":
    main()