"""
Funções auxiliares para manipulação de DataFrames.
"""

import pandas as pd


def multi_position_preview_dataframe(file_path, n_lines=5, 
                                     positions=[0, 50, 100], 
                                     insert_separator=True):
    """
    Retorna preview em múltiplas posições como um único DataFrame consolidado.
    
    Args:
        file_path (str): Caminho do arquivo
        n_lines (int): Número de linhas por posição
        positions (list): Lista de posições percentuais a visualizar (0-100)
        insert_separator (bool): Se True, insere linha '...' entre seções
        
    Returns:
        pd.DataFrame: DataFrame consolidado com todas as posições
        
    Example:
        >>> df = multi_position_preview_dataframe('data.txt', n_lines=5, positions=[0, 50, 100])
    """
    dfs = []
    
    # Lê o arquivo uma vez pra contar linhas
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    total_lines = len(lines)
    
    for i, position in enumerate(positions):
        # Calcula índice inicial baseado na posição percentual
        start_idx = int((position / 100) * total_lines)
        start_idx = max(0, min(start_idx, total_lines - n_lines))
        
        # Extrai linhas
        position_lines = []
        for j in range(start_idx, min(start_idx + n_lines, total_lines)):
            position_lines.append({
                'Posição': f'{position}%',
                'Linha': j + 1,
                'Conteúdo': lines[j].rstrip('\n')
            })
        
        df_position = pd.DataFrame(position_lines)
        dfs.append(df_position)
        
        # Adiciona separador entre posições (exceto após a última)
        if insert_separator and i < len(positions) - 1:
            separator = pd.DataFrame({
                'Posição': ['...'],
                'Linha': ['...'],
                'Conteúdo': ['.........']
            })
            dfs.append(separator)
    
    # Concatena todos os DataFrames
    df_final = pd.concat(dfs, ignore_index=True)
    
    return df_final




def format_file_overview_table(overview: dict) -> pd.DataFrame:
    """
    Formata o output de get_file_overview como DataFrame para exibição no Quarto.
    
    Args:
        overview: Dict retornado por get_file_overview()
        
    Returns:
        pd.DataFrame: Tabela formatada para exibição
    """
    data = [
        {'📊 Métrica': '📄&nbsp;Arquivo', 'Valor': overview['arquivo']},
        {'📊 Métrica': '💾&nbsp;Tamanho', 'Valor': f"{overview['tamanho_formatted']} ({overview['tamanho_bytes']:,} bytes)"},
        {'📊 Métrica': '📝&nbsp;Total&nbsp;de&nbsp;linhas', 'Valor': f"{overview['total_linhas']:,}"},
        {'📊 Métrica': '⚪&nbsp;Linhas&nbsp;vazias', 'Valor': f"{overview['linhas_vazias']:,}"},
        {'📊 Métrica': '✅&nbsp;Linhas&nbsp;não&nbsp;vazias', 'Valor': f"{overview['linhas_nao_vazias']:,}"},
        {'📊 Métrica': '🔤&nbsp;Total&nbsp;de&nbsp;caracteres', 'Valor': f"{overview['total_caracteres']:,}"},
        {'📊 Métrica': '📏&nbsp;Média&nbsp;chars/linha', 'Valor': f"{overview['media_chars_por_linha']:.1f}"},
    ]
    
    return pd.DataFrame(data)


def format_density_stats_table(density_stats: dict) -> pd.DataFrame:
    """
    Formata estatísticas de densidade como DataFrame para exibição.
    
    Args:
        density_stats: Dict retornado por get_file_density_stats()
        
    Returns:
        pd.DataFrame: Tabela formatada
    """
    data = [
        {'📊 Métrica': '🔤&nbsp;Caracteres&nbsp;totais', 'Valor': f"{density_stats['total_caracteres']:,}"},
        {'📊 Métrica': '📊&nbsp;Média chars/linha', 'Valor': f"{density_stats['media_chars_linha']:.2f}"},
        {'📊 Métrica': '📊&nbsp;Mediana chars/linha', 'Valor': f"{density_stats['mediana_chars_linha']:.2f}"},
        {'📊 Métrica': '📊&nbsp;Moda&nbsp;chars/linha', 'Valor': f"{density_stats['moda_chars_linha']:.0f}"},
        {'📊 Métrica': '⬇️&nbsp;Linha&nbsp;mais&nbsp;curta', 'Valor': f"{density_stats['linha_mais_curta']} caracteres"},
        {'📊 Métrica': '⬆️&nbsp;Linha&nbsp;mais&nbsp;longa', 'Valor': f"{density_stats['linha_mais_longa']} caracteres"},
        {'📊 Métrica': '💾&nbsp;Média&nbsp;bytes/linha', 'Valor': f"{density_stats['media_bytes_linha']:.2f}"},
        {'📊 Métrica': '💾&nbsp;Mediana&nbsp;bytes/linha', 'Valor': f"{density_stats['mediana_bytes_linha']:.2f}"},
        {'📊 Métrica': '💾&nbsp;Moda&nbsp;bytes/linha', 'Valor': f"{density_stats['moda_bytes_linha']:.0f}"},
    ]
    
    return pd.DataFrame(data)