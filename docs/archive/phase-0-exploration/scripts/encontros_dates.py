# ============================================================
# 📅 viagens.py - Definição e criação do DataFrame de viagens
# ============================================================
# Execute uma vez para gerar: output_files/viagens.csv
# Depois é só carregar: pd.read_csv('output_files/viagens.csv')
# ============================================================

import pandas as pd
#from datetime import datetime

# ============================================================================
# DATAS PRECISAS DAS VIAGENS
# ============================================================================

viagens = [
    {
        'nome': 'Chapada/BSB (1ª viagem)',
        'inicio': '2024-12-12',
        'fim': '2024-12-24',
        'tipo': 'Marlon @ BSB',
        'marco_especial': '2024-12-16',
        'marco_nome': '💕 1ª Vez Juntos'
    },
    {
        'nome': 'BSB (Janeiro)',
        'inicio': '2025-01-23',
        'fim': '2025-01-29',
        'tipo': 'Marlon @ BSB',
        'marco_especial': None,
        'marco_nome': None
    },
    {
        'nome': 'Letícia SP (Hostel)',
        'inicio': '2025-02-06',
        'fim': '2025-02-10',
        'tipo': 'Letícia @ SP',
        'marco_especial': None,
        'marco_nome': None
    },
    {
        'nome': 'BSB (Carnaval)',
        'inicio': '2025-02-27',
        'fim': '2025-03-10',
        'tipo': 'Marlon @ BSB',
        'marco_especial': None,
        'marco_nome': '🦷 Arrancou dente'
    },
    {
        'nome': 'BSB (Abril-Maio)',
        'inicio': '2025-04-16',
        'fim': '2025-05-05',
        'tipo': 'Marlon @ BSB',
        'marco_especial': None,
        'marco_nome': None
    },
    {
        'nome': 'Letícia Sorocaba',
        'inicio': '2025-05-17',
        'fim': '2025-05-24',
        'tipo': 'Letícia @ Sorocaba',
        'marco_especial': None,
        'marco_nome': None
    },
    {
        'nome': 'Letícia SP (Trampo)',
        'inicio': '2025-07-21',
        'fim': '2025-07-26',
        'tipo': 'Letícia @ SP',
        'marco_especial': None,
        'marco_nome': None
    },
    {
        'nome': 'BSB (2 meses!)',
        'inicio': '2025-08-22',
        'fim': '2025-10-11',
        'tipo': 'Marlon @ BSB',
        'marco_especial': None,
        'marco_nome': '🏠 2 meses juntos'
    },
    {
        'nome': 'BSB (Niver Letícia)',
        'inicio': '2025-11-05',
        'fim': '2025-11-19',
        'tipo': 'Marlon @ BSB',
        'marco_especial': '2025-11-04',
        'marco_nome': '🎂 Aniversário Letícia'
    },
    {
        'nome': 'BSB (Fim de ano!)',
        'inicio': '2025-12-12',
        'fim': '2026-01-04',
        'tipo': 'Marlon @ BSB',
        'marco_especial': None,
        'marco_nome': None
    }
]

# ============================================================================
# CRIAR DATAFRAME
# ============================================================================

def criar_viagens_df():
    """Cria e retorna o DataFrame de viagens."""
    df = pd.DataFrame(viagens)
    df['inicio'] = pd.to_datetime(df['inicio'])
    df['fim'] = pd.to_datetime(df['fim'])
    df['marco_especial'] = pd.to_datetime(df['marco_especial'])
    df['duracao_dias'] = (df['fim'] - df['inicio']).dt.days + 1
    return df

def gerar_datas_juntos(viagens_df):
    """Gera lista de todas as datas em que estavam juntos."""
    datas = []
    for _, row in viagens_df.iterrows():
        periodo = pd.date_range(row['inicio'], row['fim'], freq='D')
        datas.extend(periodo.tolist())
    return sorted(set(datas))

def criar_contexto_relacional(viagens_df, dias_pre=7, dias_pos=7):
    """
    Cria dicionário de contexto para cada data.
    Retorna: {data: 'juntos' | 'pre_viagem' | 'pos_viagem' | 'rotina'}
    """
    contexto = {}
    
    for _, row in viagens_df.iterrows():
        # Dias JUNTOS
        for d in pd.date_range(row['inicio'], row['fim'], freq='D'):
            contexto[d.date()] = 'juntos'
        
        # Dias PRE-VIAGEM
        pre_inicio = row['inicio'] - pd.Timedelta(days=dias_pre)
        for d in pd.date_range(pre_inicio, row['inicio'] - pd.Timedelta(days=1), freq='D'):
            if d.date() not in contexto:
                contexto[d.date()] = 'pre_viagem'
        
        # Dias POS-VIAGEM
        pos_fim = row['fim'] + pd.Timedelta(days=dias_pos)
        for d in pd.date_range(row['fim'] + pd.Timedelta(days=1), pos_fim, freq='D'):
            if d.date() not in contexto:
                contexto[d.date()] = 'pos_viagem'
    
    return contexto

# ============================================================================
# EXECUÇÃO E SALVAMENTO
# ============================================================================

if __name__ == '__main__':
    import os
    
    print("="*60)
    print("📅 GERANDO DATAFRAME DE VIAGENS")
    print("="*60)
    
    # Cria pasta se não existir
    os.makedirs('output_files', exist_ok=True)
    
    # Cria DataFrame
    viagens_df = criar_viagens_df()
    
    # Mostra resumo
    print(f"\n✅ {len(viagens_df)} viagens registradas\n")
    print(viagens_df[['nome', 'inicio', 'fim', 'duracao_dias', 'tipo']].to_string(index=False))
    
    # Estatísticas
    total_dias_juntos = viagens_df['duracao_dias'].sum()
    print("\n📊 Resumo:")
    print(f"   • Total de dias juntos: {total_dias_juntos} dias")
    print(f"   • Viagem mais longa: {viagens_df['duracao_dias'].max()} dias")
    print(f"   • Viagem mais curta: {viagens_df['duracao_dias'].min()} dias")
    
    # Salva CSV
    viagens_df.to_csv('output_files/viagens.csv', index=False)
    print("\n💾 Salvo: output_files/viagens.csv")
    
    # Gera e salva datas juntos
    datas_juntos = gerar_datas_juntos(viagens_df)
    datas_juntos_df = pd.DataFrame({'data': datas_juntos})
    datas_juntos_df.to_csv('output_files/datas_juntos.csv', index=False)
    print(f"💾 Salvo: output_files/datas_juntos.csv ({len(datas_juntos)} datas)")
    
    print("\n✅ Concluído!")