"""
Funções de auditoria para transformações de dados.

Este módulo fornece ferramentas para comparar arquivos antes/depois
de transformações, garantindo rastreabilidade do pipeline.
"""

import os
import pandas as pd
from typing import Optional


def get_file_metadata(file_path: str) -> dict:
    """
    Obtém metadados básicos de um arquivo.
    
    Args:
        file_path: Caminho do arquivo
        
    Returns:
        Dict com métricas do arquivo
    """
    size_bytes = os.path.getsize(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    return {
        'path': file_path,
        'size_bytes': size_bytes,
        'size_formatted': format_bytes(size_bytes),
        'total_lines': len(lines)
    }


def format_bytes(size: int) -> str:
    """Formata bytes para unidade legível."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"


def audit_transformation(before_file: str, 
                         after_file: str, 
                         description: str) -> dict:
    """
    Compara dois arquivos e retorna métricas da transformação.
    
    Args:
        before_file: Caminho do arquivo antes da transformação
        after_file: Caminho do arquivo após a transformação
        description: Nome/descrição da etapa
        
    Returns:
        Dict com métricas de mudança
    """
    meta_before = get_file_metadata(before_file)
    meta_after = get_file_metadata(after_file)
    
    delta_lines = meta_before['total_lines'] - meta_after['total_lines']
    delta_bytes = meta_before['size_bytes'] - meta_after['size_bytes']
    delta_pct = (delta_bytes / meta_before['size_bytes'] * 100) if meta_before['size_bytes'] > 0 else 0
    
    return {
        'etapa': description,
        'antes_arquivo': before_file,
        'depois_arquivo': after_file,
        'antes_linhas': meta_before['total_lines'],
        'depois_linhas': meta_after['total_lines'],
        'antes_bytes': meta_before['size_bytes'],
        'depois_bytes': meta_after['size_bytes'],
        'delta_lines': delta_lines,
        'delta_bytes': delta_bytes,
        'delta_pct': round(delta_pct, 2)
    }


def audit_pipeline(stages: list[tuple[str, str, str]]) -> list[dict]:
    """
    Audita pipeline completo de transformações.
    
    Args:
        stages: Lista de tuplas (arquivo_antes, arquivo_depois, descrição)
        
    Returns:
        Lista de dicts com auditorias de cada etapa
        
    Example:
        stages = [
            ('data/raw/raw-data.txt', 'data/interim/cln1.txt', 'Remoção U+200E'),
            ('data/interim/cln1.txt', 'data/interim/cln2.txt', 'Timestamps vazios'),
        ]
        audits = audit_pipeline(stages)
    """
    return [
        audit_transformation(before, after, desc) 
        for before, after, desc in stages
    ]


def print_audit_report(audits: list[dict], show_files: bool = False):
    """
    Imprime relatório formatado das auditorias.
    
    Args:
        audits: Lista de dicts de auditoria
        show_files: Se True, mostra nomes dos arquivos
    """
    print("=" * 80)
    print("📊 RELATÓRIO DE AUDITORIA DO PIPELINE")
    print("=" * 80)
    
    total_bytes = 0
    total_lines = 0
    
    for i, a in enumerate(audits, 1):
        print(f"\n{i}. {a['etapa']}")
        if show_files:
            print(f"   📁 {a['antes_arquivo']} → {a['depois_arquivo']}")
        print(f"   📝 Linhas: {a['antes_linhas']:,} → {a['depois_linhas']:,} ({a['delta_lines']:+,})")
        print(f"   💾 Bytes:  {a['delta_bytes']:+,} ({a['delta_pct']:+.2f}%)")
        
        total_bytes += a['delta_bytes']
        total_lines += a['delta_lines']
    
    print("\n" + "-" * 80)
    print(f"📦 TOTAL ACUMULADO:")
    print(f"   📝 Linhas removidas: {total_lines:+,}")
    print(f"   💾 Bytes removidos: {total_bytes:+,} ({format_bytes(total_bytes)})")
    print("=" * 80)


def audit_to_dataframe(audits: list[dict]) -> pd.DataFrame:
    """
    Converte lista de auditorias para DataFrame.
    
    Args:
        audits: Lista de dicts de auditoria
        
    Returns:
        DataFrame formatado para visualização
    """
    df = pd.DataFrame(audits)
    
    # Seleciona e renomeia colunas para visualização
    df_display = df[[
        'etapa', 
        'antes_linhas', 
        'depois_linhas', 
        'delta_lines',
        'delta_bytes',
        'delta_pct'
    ]].copy()
    
    df_display.columns = [
        'Etapa',
        'Linhas (antes)',
        'Linhas (depois)',
        'Δ Linhas',
        'Δ Bytes',
        'Δ %'
    ]
    
    return df_display


def audit_dataframe_transformation(df_before: pd.DataFrame,
                                   df_after: pd.DataFrame,
                                   description: str) -> dict:
    """
    Audita transformação entre dois DataFrames.
    
    Args:
        df_before: DataFrame antes
        df_after: DataFrame depois
        description: Descrição da transformação
        
    Returns:
        Dict com métricas de mudança
    """
    return {
        'etapa': description,
        'antes_linhas': len(df_before),
        'depois_linhas': len(df_after),
        'antes_colunas': len(df_before.columns),
        'depois_colunas': len(df_after.columns),
        'delta_linhas': len(df_before) - len(df_after),
        'delta_colunas': len(df_after.columns) - len(df_before.columns),
        'colunas_novas': list(set(df_after.columns) - set(df_before.columns)),
        'colunas_removidas': list(set(df_before.columns) - set(df_after.columns))
    }


def print_dataframe_audit(audit: dict):
    """
    Imprime auditoria de transformação de DataFrame.
    """
    print("=" * 60)
    print(f"📊 {audit['etapa']}")
    print("=" * 60)
    print(f"📝 Linhas: {audit['antes_linhas']:,} → {audit['depois_linhas']:,} ({audit['delta_linhas']:+,})")
    print(f"📋 Colunas: {audit['antes_colunas']} → {audit['depois_colunas']} ({audit['delta_colunas']:+})")
    
    if audit['colunas_novas']:
        print(f"\n✅ Colunas adicionadas:")
        for col in audit['colunas_novas']:
            print(f"   • {col}")
    
    if audit['colunas_removidas']:
        print(f"\n❌ Colunas removidas:")
        for col in audit['colunas_removidas']:
            print(f"   • {col}")
    
    print("=" * 60)
