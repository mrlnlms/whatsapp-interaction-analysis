"""
Funções de auditoria para comparação entre estágios do pipeline.
"""

import os
import pandas as pd
from pathlib import Path

from whatsapp.pipeline.utils.file_helpers import format_bytes


def get_file_stats(file_path: str) -> dict:
    """
    Retorna estatísticas básicas de um arquivo.
    
    Args:
        file_path: Caminho do arquivo
        
    Returns:
        Dict com path, name, size_bytes, size_formatted, total_lines, total_chars
    """
    file_path = str(file_path)
    size_bytes = os.path.getsize(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.splitlines()
    total_chars = len(content)
    
    return {
        'path': file_path,
        'name': Path(file_path).name,
        'size_bytes': size_bytes,
        'size_formatted': format_bytes(size_bytes),
        'total_lines': len(lines),
        'total_chars': total_chars
    }


def audit_transformation(
    input_file: str, 
    output_file: str, 
    transformation_name: str,
    show_output: bool = True
) -> dict:
    """
    Audita uma transformação individual entre dois arquivos.
    
    Args:
        input_file: Arquivo de entrada
        output_file: Arquivo de saída
        transformation_name: Nome da transformação realizada
        show_output: Se True, imprime relatório
        
    Returns:
        Dict com métricas da transformação
    """
    before = get_file_stats(input_file)
    after = get_file_stats(output_file)
    
    delta_lines = before['total_lines'] - after['total_lines']
    delta_bytes = before['size_bytes'] - after['size_bytes']
    delta_chars = before['total_chars'] - after['total_chars']
    delta_pct = (delta_bytes / before['size_bytes'] * 100) if before['size_bytes'] > 0 else 0
    
    result = {
        'transformation': transformation_name,
        'input': before,
        'output': after,
        'delta_lines': delta_lines,
        'delta_bytes': delta_bytes,
        'delta_chars': delta_chars,
        'delta_percent': delta_pct,
        'lines_match': before['total_lines'] == after['total_lines']
    }
    
    if show_output:
        print(f"\n{'─'*75}")
        print(f"🔍 AUDITORIA: {transformation_name}")
        print(f"{'─'*75}")
        print(f"📄 Entrada:  {before['name']} ({before['size_formatted']}, {before['total_lines']:,} linhas, {before['total_chars']:,} chars)")
        print(f"📄 Saída:    {after['name']} ({after['size_formatted']}, {after['total_lines']:,} linhas, {after['total_chars']:,} chars)")
        print(f"📉 Redução:  {delta_bytes:,} bytes | {delta_lines:,} linhas | {delta_chars:,} chars ({delta_pct:.2f}%)")
        print(f"{'─'*75}")
    
    return result


def audit_pipeline(
    stages: list,
    show_output: bool = True
) -> tuple:
    """
    Audita um pipeline completo de transformações.
    
    Args:
        stages: Lista de dicts com {'file': path, 'name': nome_do_estágio}
        show_output: Se True, imprime relatório completo
        
    Returns:
        Tuple (DataFrame com métricas, dict com totais)
        
    Example:
        stages = [
            {'file': 'raw-data.txt', 'name': 'Original'},
            {'file': 'raw-data_cln1.txt', 'name': 'Sem U+200E'},
        ]
        df_audit, totals = audit_pipeline(stages)
    """
    # Coleta métricas de cada arquivo
    stats = [get_file_stats(s['file']) for s in stages]
    
    # Monta dados para DataFrame
    rows = []
    for i, (stage, stat) in enumerate(zip(stages, stats)):
        row = {
            'Estágio': stage['name'],
            'Arquivo': stat['name'],
            'Linhas': stat['total_lines'],
            'Chars': stat['total_chars'],
            'Tamanho': stat['size_formatted'],
            'Tamanho_bytes': stat['size_bytes'],
            'Δ Linhas': 0,
            'Δ Chars': 0,
            'Δ Bytes': 0,
            'Δ %': 0.0
        }
        
        if i > 0:
            prev = stats[i-1]
            row['Δ Linhas'] = prev['total_lines'] - stat['total_lines']
            row['Δ Chars'] = prev['total_chars'] - stat['total_chars']
            row['Δ Bytes'] = prev['size_bytes'] - stat['size_bytes']
            row['Δ %'] = (row['Δ Bytes'] / prev['size_bytes'] * 100) if prev['size_bytes'] > 0 else 0
        
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Calcula totais
    total_lines = stats[0]['total_lines'] - stats[-1]['total_lines']
    total_chars = stats[0]['total_chars'] - stats[-1]['total_chars']
    total_bytes = stats[0]['size_bytes'] - stats[-1]['size_bytes']
    total_pct = (total_bytes / stats[0]['size_bytes'] * 100) if stats[0]['size_bytes'] > 0 else 0
    
    # Guarda tamanhos original e final para projeções
    totals = {
        'total_lines': total_lines,
        'total_chars': total_chars,
        'total_bytes': total_bytes,
        'total_percent': total_pct,
        'total_formatted': format_bytes(total_bytes),
        'original_bytes': stats[0]['size_bytes'],
        'final_bytes': stats[-1]['size_bytes'],
        'original_formatted': stats[0]['size_formatted'],
        'final_formatted': stats[-1]['size_formatted']
    }
    
    if show_output:
        print("\n" + "="*105)
        print("📊 AUDITORIA DO PIPELINE DE TRANSFORMAÇÃO")
        print("="*105 + "\n")
        
        # Cabeçalho
        print(f"{'Estágio':<42} {'Linhas':>10} {'Chars':>12} {'Tamanho':>10} {'Δ Linhas':>10} {'Δ %':>10}")
        print("-"*105)
        
        for _, row in df.iterrows():
            delta_l = f"-{row['Δ Linhas']:,}" if row['Δ Linhas'] > 0 else "-"
            delta_p = f"-{row['Δ %']:.2f}%" if row['Δ %'] > 0 else "-"
            print(f"{row['Estágio']:<42} {row['Linhas']:>10,} {row['Chars']:>12,} {row['Tamanho']:>10} {delta_l:>10} {delta_p:>10}")
        
        print("-"*105)
        print(f"{'🎯 TOTAL REDUZIDO':<42} {f'-{total_lines:,}':>10} {f'-{total_chars:,}':>12} {format_bytes(total_bytes):>10} {'-':>10} {f'-{total_pct:.2f}%':>10}")
        print("="*105 + "\n")
    
    return df, totals


def format_audit_table(df_audit: pd.DataFrame, include_chars: bool = True) -> pd.DataFrame:
    """
    Formata DataFrame de auditoria para exibição no Quarto.
    
    Args:
        df_audit: DataFrame retornado por audit_pipeline()
        include_chars: Se True, inclui coluna de caracteres
        
    Returns:
        DataFrame formatado para exibição
    """
    if include_chars:
        df_display = df_audit[['Estágio', 'Linhas', 'Chars', 'Tamanho', 'Δ Linhas', 'Δ Chars', 'Δ %']].copy()
    else:
        df_display = df_audit[['Estágio', 'Linhas', 'Tamanho', 'Δ Linhas', 'Δ %']].copy()
    
    # Formata valores
    df_display['Δ %'] = df_audit['Δ %'].apply(lambda x: f"-{x:.2f}%" if x > 0 else "-")
    df_display['Δ Linhas'] = df_audit['Δ Linhas'].apply(lambda x: f"-{x:,}" if x > 0 else "-")
    df_display['Linhas'] = df_audit['Linhas'].apply(lambda x: f"{x:,}")
    
    if include_chars:
        df_display['Chars'] = df_audit['Chars'].apply(lambda x: f"{x:,}")
        df_display['Δ Chars'] = df_audit['Δ Chars'].apply(lambda x: f"-{x:,}" if x > 0 else "-")
    
    return df_display


def format_summary_table(audits: list) -> pd.DataFrame:
    """
    Cria tabela de resumo por etapa com headers claros.
    
    Args:
        audits: Lista de dicts retornados por audit_transformation()
        
    Returns:
        DataFrame formatado
    """
    emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    
    data = []
    for i, audit in enumerate(audits):
        emoji = emojis[i] if i < len(emojis) else f"{i+1}."
        data.append({
            'Etapa': f"{emoji} {audit['transformation']}",
            'Tamanho Após': audit['output']['size_formatted'],
            'Bytes Removidos': f"{audit['delta_bytes']:,}",
            'Linhas Removidas': f"{audit['delta_lines']:,}" if audit['delta_lines'] > 0 else "-",
            'Chars Removidos': f"{audit['delta_chars']:,}" if audit['delta_chars'] > 0 else "-",
            'Redução %': f"{audit['delta_percent']:.2f}%"
        })
    
    return pd.DataFrame(data)


def generate_impact_analysis(totals: dict, enrichment_factor: float = 8.0) -> dict:
    """
    Gera análise de impacto e projeções para dataset enriquecido.
    
    Args:
        totals: Dict retornado por audit_pipeline()
        enrichment_factor: Fator de multiplicação estimado para dataset enriquecido
        
    Returns:
        Dict com métricas de impacto
    """
    original_mb = totals['original_bytes'] / (1024 * 1024)
    final_mb = totals['final_bytes'] / (1024 * 1024)
    
    projected_original = original_mb * enrichment_factor
    projected_optimized = final_mb * enrichment_factor
    projected_savings = projected_original - projected_optimized
    
    return {
        'original_mb': original_mb,
        'final_mb': final_mb,
        'reduction_pct': totals['total_percent'],
        'enrichment_factor': enrichment_factor,
        'projected_original_mb': projected_original,
        'projected_optimized_mb': projected_optimized,
        'projected_savings_mb': projected_savings
    }