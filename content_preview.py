"""
Módulo para visualização e inspeção do conteúdo de arquivos.
Permite preview flexível em diferentes posições do arquivo.
"""

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


def get_file_lines(file_path='raw-data.txt'):
    """
    Lê todas as linhas do arquivo.
    
    Args:
        file_path (str): Caminho do arquivo
        
    Returns:
        list: Lista com todas as linhas do arquivo
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.readlines()


def calculate_position_index(total_lines, position):
    """
    Calcula o índice da linha baseado na posição percentual.
    
    Args:
        total_lines (int): Total de linhas no arquivo
        position (int): Posição percentual (0, 25, 50, 75, 100)
        
    Returns:
        int: Índice da linha correspondente
    """
    if position == 0:
        return 0
    elif position == 100:
        return max(0, total_lines - 1)
    else:
        return int((position / 100) * total_lines)


def preview_content(file_path='raw-data.txt', n_lines=5, position=0, 
                   show_line_numbers=True, truncate_at=150):
    """
    Exibe preview do conteúdo do arquivo em diferentes posições.
    
    Args:
        file_path (str): Caminho do arquivo
        n_lines (int): Número de linhas a exibir
        position (int): Posição no arquivo (0=início, 25=25%, 50=meio, 75=75%, 100=final)
        show_line_numbers (bool): Se deve mostrar números de linha
        truncate_at (int): Truncar linhas maiores que este valor (0 = sem truncar)
        
    Returns:
        dict: Informações sobre o preview realizado
    """
    if position not in [0, 25, 50, 75, 100]:
        raise ValueError("position deve ser um dos valores: 0, 25, 50, 75, 100")
    
    lines = get_file_lines(file_path)
    total_lines = len(lines)
    
    # Calcula índice inicial baseado na posição
    start_idx = calculate_position_index(total_lines, position)
    
    # Para posição 100 (final), queremos as últimas n_lines
    if position == 100:
        start_idx = max(0, total_lines - n_lines)
    
    # Ajusta se ultrapassar o final do arquivo
    end_idx = min(start_idx + n_lines, total_lines)
    
    # Extrai as linhas
    selected_lines = lines[start_idx:end_idx]
    
    # Prepara informações do preview
    preview_info = {
        'total_lines': total_lines,
        'position': position,
        'start_line': start_idx + 1,  # +1 para exibição (linhas começam em 1)
        'end_line': end_idx,
        'lines_shown': len(selected_lines)
    }
    
    # Monta a posição descritiva
    position_desc = {
        0: 'INÍCIO',
        25: 'PRIMEIRO QUARTIL (25%)',
        50: 'MEIO (50%)',
        75: 'TERCEIRO QUARTIL (75%)',
        100: 'FINAL'
    }
    
    # Imprime header
    print()
    print("=" * 70)
    print(f"PREVIEW DO CONTEÚDO - {position_desc[position]}")
    print("=" * 70)
    print(f"📍 Posição: Linhas {preview_info['start_line']} a {preview_info['end_line']} "
          f"de {preview_info['total_lines']:,} totais")
    print("-" * 70)
    print()
    
    # Imprime as linhas
    for i, line in enumerate(selected_lines, start=start_idx + 1):
        # Remove \n do final
        line_content = line.rstrip('\n')
        
        # Trunca se necessário
        if truncate_at > 0 and len(line_content) > truncate_at:
            line_content = line_content[:truncate_at - 3] + "..."
        
        # Exibe com ou sem número de linha
        if show_line_numbers:
            # Calcula padding baseado no total de linhas
            padding = len(str(total_lines))
            print(f"{i:>{padding}} │ {line_content}")
        else:
            print(line_content)
    
    print()
    print("=" * 70)
    
    return preview_info


def multi_position_preview(file_path='raw-data.txt', n_lines=3, 
                          positions=[0, 50, 100], truncate_at=150):
    """
    Exibe preview em múltiplas posições do arquivo.
    
    Args:
        file_path (str): Caminho do arquivo
        n_lines (int): Número de linhas por posição
        positions (list): Lista de posições a visualizar
        truncate_at (int): Truncar linhas maiores que este valor
        
    Returns:
        list: Lista com informações de cada preview
    """
    print("\n" + "=" * 70)
    print("VISUALIZAÇÃO MULTI-POSIÇÃO DO ARQUIVO")
    print("=" * 70)
    
    preview_infos = []
    
    for position in positions:
        info = preview_content(
            file_path=file_path,
            n_lines=n_lines,
            position=position,
            show_line_numbers=True,
            truncate_at=truncate_at
        )
        preview_infos.append(info)
    
    return preview_infos


def analyze_content_complexity(file_path='raw-data.txt', sample_size=100):
    """
    Analisa a complexidade do conteúdo do arquivo.
    
    Args:
        file_path (str): Caminho do arquivo
        sample_size (int): Número de linhas a amostrar
        
    Returns:
        dict: Métricas de complexidade
    """
    lines = get_file_lines(file_path)
    total_lines = len(lines)
    
    # Amostra aleatória ou todas as linhas se menor que sample_size
    import random
    sample = random.sample(lines, min(sample_size, total_lines))
    
    # Métricas
    empty_lines = sum(1 for line in lines if not line.strip())
    lines_with_emoji = sum(1 for line in sample if any(ord(c) > 127 for c in line))
    lines_with_special_chars = sum(1 for line in sample if any(c in line for c in ['<', '>', '[', ']']))
    
    # Contagem de palavras
    word_counts = [len(line.split()) for line in sample if line.strip()]
    avg_words = sum(word_counts) / len(word_counts) if word_counts else 0
    
    complexity = {
        'total_lines': total_lines,
        'empty_lines': empty_lines,
        'empty_line_ratio': (empty_lines / total_lines * 100) if total_lines > 0 else 0,
        'lines_with_emoji': lines_with_emoji,
        'emoji_ratio': (lines_with_emoji / len(sample) * 100) if sample else 0,
        'lines_with_special_chars': lines_with_special_chars,
        'special_char_ratio': (lines_with_special_chars / len(sample) * 100) if sample else 0,
        'avg_words_per_line': avg_words,
        'sample_size': len(sample)
    }
    
    return complexity


def print_complexity_analysis(file_path='raw-data.txt'):
    """
    Imprime análise de complexidade do conteúdo.
    
    Args:
        file_path (str): Caminho do arquivo
    """
    complexity = analyze_content_complexity(file_path)
    
    print("\n" + "=" * 70)
    print("ANÁLISE DE COMPLEXIDADE DO CONTEÚDO")
    print("=" * 70)
    print()
    print(f"📊 Linhas analisadas: {complexity['sample_size']} de {complexity['total_lines']:,}")
    print()
    print(f"🔹 Linhas vazias: {complexity['empty_lines']:,} ({complexity['empty_line_ratio']:.1f}%)")
    print(f"🔹 Linhas com emoji/caracteres especiais: {complexity['lines_with_emoji']} ({complexity['emoji_ratio']:.1f}%)")
    print(f"🔹 Linhas com estrutura especial ([], <>, etc): {complexity['lines_with_special_chars']} ({complexity['special_char_ratio']:.1f}%)")
    print()
    print(f"📝 Média de palavras por linha: {complexity['avg_words_per_line']:.1f}")
    print()
    
    # Interpretação
    print("💡 INTERPRETAÇÃO:")
    if complexity['empty_line_ratio'] > 10:
        print("   • Alto índice de linhas vazias - pode indicar quebras de mensagem")
    if complexity['emoji_ratio'] > 30:
        print("   • Uso frequente de emojis - conversação informal")
    if complexity['special_char_ratio'] > 20:
        print("   • Muitos caracteres especiais - provável formato estruturado")
    if complexity['avg_words_per_line'] < 5:
        print("   • Mensagens curtas predominam")
    elif complexity['avg_words_per_line'] > 15:
        print("   • Mensagens mais longas e elaboradas")
    
    print("=" * 70)
    
    return complexity


def preview_content_dataframe(file_path='raw-data.txt', n_lines=5, position=0):
    """
    Retorna preview do conteúdo como DataFrame do pandas.
    
    Args:
        file_path (str): Caminho do arquivo
        n_lines (int): Número de linhas a exibir
        position (int): Posição no arquivo (0=início, 25=25%, 50=meio, 75=75%, 100=final)
        
    Returns:
        pd.DataFrame: DataFrame com colunas ['posicao', 'linha', 'conteudo']
    """
    if not PANDAS_AVAILABLE:
        raise ImportError("pandas não está instalado. Execute: pip install pandas")
    
    if position not in [0, 25, 50, 75, 100]:
        raise ValueError("position deve ser um dos valores: 0, 25, 50, 75, 100")
    
    lines = get_file_lines(file_path)
    total_lines = len(lines)
    
    # Calcula índice inicial baseado na posição
    start_idx = calculate_position_index(total_lines, position)
    
    # Para posição 100 (final), queremos as últimas n_lines
    if position == 100:
        start_idx = max(0, total_lines - n_lines)
    
    # Ajusta se ultrapassar o final do arquivo
    end_idx = min(start_idx + n_lines, total_lines)
    
    # Extrai as linhas
    selected_lines = lines[start_idx:end_idx]
    
    # Monta o DataFrame
    position_desc = {
        0: 'INÍCIO',
        25: '25%',
        50: '50%',
        75: '75%',
        100: 'FINAL'
    }
    
    data = {
        'posicao': [position_desc[position]] * len(selected_lines),
        'linha': range(start_idx + 1, end_idx + 1),
        'conteudo': [line.rstrip('\n') for line in selected_lines]
    }
    
    df = pd.DataFrame(data)
    return df


def multi_position_preview_dataframe(file_path='raw-data.txt', n_lines=5, 
                                     positions=[0, 50, 100], insert_separator=True):
    """
    Retorna preview em múltiplas posições como um único DataFrame consolidado.
    
    Args:
        file_path (str): Caminho do arquivo
        n_lines (int): Número de linhas por posição
        positions (list): Lista de posições a visualizar
        insert_separator (bool): Se True, insere linha '...' entre seções
        
    Returns:
        pd.DataFrame: DataFrame consolidado com todas as posições
    """
    if not PANDAS_AVAILABLE:
        raise ImportError("pandas não está instalado. Execute: pip install pandas")
    
    dfs = []
    
    for i, position in enumerate(positions):
        # Obtém DataFrame para esta posição
        df_position = preview_content_dataframe(file_path, n_lines, position)
        dfs.append(df_position)
        
        # Adiciona separador entre posições (exceto após a última)
        if insert_separator and i < len(positions) - 1:
            separator = pd.DataFrame({
                'posicao': ['...'],
                'linha': ['...'],
                'conteudo': ['...']
            })
            dfs.append(separator)
    
    # Concatena todos os DataFrames
    df_final = pd.concat(dfs, ignore_index=True)
    
    return df_final


def print_dataframe_preview(df, title="PREVIEW DO CONTEÚDO"):
    """
    Imprime um DataFrame de preview de forma formatada.
    
    Args:
        df (pd.DataFrame): DataFrame a ser exibido
        title (str): Título da visualização
    """
    if not PANDAS_AVAILABLE:
        raise ImportError("pandas não está instalado. Execute: pip install pandas")
    
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)
    print()
    
    # Configura pandas para exibir mais linhas e colunas completas
    with pd.option_context('display.max_rows', None, 
                           'display.max_columns', None,
                           'display.width', None,
                           'display.max_colwidth', 100):
        print(df.to_string(index=False))
    
    print()
    print("=" * 100)


if __name__ == "__main__":
    # Exemplo de uso
    print("\n🔍 INSPEÇÃO AVANÇADA DO ARQUIVO")
    
    # Preview em múltiplas posições (versão texto)
    multi_position_preview(
        file_path='raw-data.txt',
        n_lines=3,
        positions=[0, 50, 100],
        truncate_at=120
    )
    
    # Análise de complexidade
    print_complexity_analysis('raw-data.txt')
    
    # Se pandas estiver disponível, mostra versão DataFrame
    if PANDAS_AVAILABLE:
        print("\n" + "=" * 100)
        print("📊 VERSÃO DATAFRAME (PANDAS)")
        print("=" * 100)
        
        # DataFrame consolidado
        df = multi_position_preview_dataframe(
            file_path='raw-data.txt',
            n_lines=3,
            positions=[0, 50, 100],
            insert_separator=True
        )
        
        print_dataframe_preview(df, title="PREVIEW MULTI-POSIÇÃO (DATAFRAME)")
        
        print("\n💡 Para usar em análises:")
        print("   df = multi_position_preview_dataframe('raw-data.txt', n_lines=5, positions=[0, 50, 100])")
        print("   df.head()  # Ou qualquer operação pandas")