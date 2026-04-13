"""
Gera o grafico Timeline Ultimate do projeto WhatsApp.

Baseado no notebook original docs/archive/phase-0-exploration/notebooks/04-analises-avancadas.qmd
(label: timeline-ultimate-final-corrigido), adaptado pro schema atual.

Uso: python scripts/generate_timeline_chart.py
Saida: assets/images/timeline-ultimate.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from scipy.interpolate import make_interp_spline
from pathlib import Path

# ============================================================================
# DADOS
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
df = pd.read_parquet(PROJECT_ROOT / 'data' / 'processed' / 'export_2024-10_2025-10' / 'messages.parquet')
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Mapeia grupo_mensagem -> tipo_midia (schema antigo)
GRUPO_TO_MIDIA = {
    'TEXT': 'text', 'AUDIO': 'audio', 'VID': 'video', 'IMG': 'image',
    'STICKER': 'sticker', 'GIF': 'image', 'DOC': 'other', 'FILE': 'other',
    'CONTACT': 'other', 'CALL': 'other', 'SYSTEM': 'other',
}
df['tipo_midia'] = df['grupo_mensagem'].map(GRUPO_TO_MIDIA).fillna('other')

# Viagens (do notebook original)
viagens = [
    {'nome': 'Chapada/BSB (1a viagem)', 'inicio': '2024-12-12', 'fim': '2024-12-24', 'tipo': 'Marlon @ BSB'},
    {'nome': 'BSB (Janeiro)', 'inicio': '2025-01-23', 'fim': '2025-01-29', 'tipo': 'Marlon @ BSB'},
    {'nome': 'Leticia SP (Hostel)', 'inicio': '2025-02-06', 'fim': '2025-02-10', 'tipo': 'Leticia @ SP'},
    {'nome': 'BSB (Carnaval)', 'inicio': '2025-02-27', 'fim': '2025-03-10', 'tipo': 'Marlon @ BSB'},
    {'nome': 'BSB (Abril-Maio)', 'inicio': '2025-04-16', 'fim': '2025-05-05', 'tipo': 'Marlon @ BSB'},
    {'nome': 'Leticia Sorocaba', 'inicio': '2025-05-17', 'fim': '2025-05-24', 'tipo': 'Leticia @ Sorocaba'},
    {'nome': 'Leticia SP (Trampo)', 'inicio': '2025-07-21', 'fim': '2025-07-26', 'tipo': 'Leticia @ SP'},
    {'nome': 'BSB (2 meses!)', 'inicio': '2025-08-22', 'fim': '2025-10-11', 'tipo': 'Marlon @ BSB'},
    {'nome': 'BSB (Niver Leticia)', 'inicio': '2025-11-05', 'fim': '2025-11-19', 'tipo': 'Marlon @ BSB'},
    {'nome': 'BSB (Fim de ano!)', 'inicio': '2025-12-12', 'fim': '2026-01-04', 'tipo': 'Marlon @ BSB'},
]

viagens_df = pd.DataFrame(viagens)
viagens_df['inicio'] = pd.to_datetime(viagens_df['inicio'])
viagens_df['fim'] = pd.to_datetime(viagens_df['fim'])

# ============================================================================
# AGREGACOES
# ============================================================================

df['ano_mes'] = df['timestamp'].dt.to_period('M')
msgs_por_mes_p = df.groupby(['ano_mes', 'remetente']).size().unstack(fill_value=0)

max_viagem_date = viagens_df['fim'].max()
min_period = msgs_por_mes_p.index.min()
max_period = pd.Period(max_viagem_date, 'M')
all_periods = pd.period_range(start=min_period, end=max_period, freq='M')
msgs_por_mes_p = msgs_por_mes_p.reindex(all_periods, fill_value=0)

dates = [period.to_timestamp() for period in msgs_por_mes_p.index]
p1_values = msgs_por_mes_p['P1'].values
p2_values = msgs_por_mes_p['P2'].values
total_values = p1_values + p2_values

tipos_mes = df.groupby(['ano_mes', 'tipo_midia']).size().unstack(fill_value=0)
tipos_mes = tipos_mes.reindex(all_periods, fill_value=0)

text_values = tipos_mes.get('text', pd.Series(0, index=tipos_mes.index)).values
audio_values = tipos_mes.get('audio', pd.Series(0, index=tipos_mes.index)).values
video_values = tipos_mes.get('video', pd.Series(0, index=tipos_mes.index)).values
image_values = tipos_mes.get('image', pd.Series(0, index=tipos_mes.index)).values

data_inicio = df['timestamp'].min().date()
primeiro_dia = min(data_inicio, viagens_df['inicio'].min().date())
ultimo_dia = viagens_df['fim'].max().date()
all_dates = pd.date_range(start=primeiro_dia, end=ultimo_dia, freq='D').date

dias_juntos_set = set()
for _, viagem in viagens_df.iterrows():
    inicio = viagem['inicio'].date()
    fim = viagem['fim'].date()
    current_date = inicio
    while current_date <= fim:
        dias_juntos_set.add(current_date)
        current_date += timedelta(days=1)

total_dias_juntos = len(dias_juntos_set)
total_dias_periodo = (ultimo_dia - primeiro_dia).days + 1
pct_ano_juntos = (total_dias_juntos / total_dias_periodo * 100)

dias_df = pd.DataFrame({'data': all_dates, 'juntos': [d in dias_juntos_set for d in all_dates]})
dias_df['ano_mes'] = pd.to_datetime(dias_df['data']).dt.to_period('M')

por_mes = dias_df.groupby('ano_mes').agg({'juntos': 'sum', 'data': 'count'}).rename(
    columns={'juntos': 'dias_juntos', 'data': 'total_dias'})
por_mes['pct_juntos'] = (por_mes['dias_juntos'] / por_mes['total_dias'] * 100)
por_mes = por_mes.reindex(all_periods, fill_value=0)
por_mes['pct_juntos'] = por_mes['pct_juntos'].fillna(0)
pct_juntos_values = por_mes['pct_juntos'].values

# Spline suavizada
dates_num = mdates.date2num(dates)
spline = make_interp_spline(dates_num, pct_juntos_values, k=3)
dates_smooth_num = np.linspace(dates_num.min(), dates_num.max(), 300)
pct_smooth = np.clip(spline(dates_smooth_num), 0, 105)
dates_smooth = mdates.num2date(dates_smooth_num)

# ============================================================================
# CORES
# ============================================================================

COLORS = {
    'viagens_bg': '#f6d4a5ff', 'pct_juntos': '#f69e2cff',
    'P1': '#0A0AFF', 'P2': '#FF0080',
    'text': '#0099F6', 'audio': '#E63946', 'video': '#2ECC71', 'image': '#9C27B0',
    'total': '#74808b',
}

# ============================================================================
# FIGURA
# ============================================================================

fig = plt.figure(figsize=(22, 10))
ax2 = fig.add_subplot(111)
ax1 = ax2.twinx()
ax1.set_zorder(ax2.get_zorder() + 1)
ax1.patch.set_visible(False)

# Labels das viagens
viagens_sorted = viagens_df.sort_values('inicio').reset_index(drop=True)
labels_info = []
max_value = max(total_values)

for idx, viagem in viagens_sorted.iterrows():
    inicio = viagem['inicio']
    fim = viagem['fim']
    tipo = viagem['tipo']
    duracao_dias = (fim.date() - inicio.date()).days + 1

    if 'Marlon' in tipo or 'BSB' in viagem['nome']:
        local = 'BSB'
    elif 'Hostel' in viagem['nome']:
        local = 'SP (Hostel)'
    elif 'Trampo' in viagem['nome']:
        local = 'SP (Trabalho)'
    elif 'Sorocaba' in viagem['nome']:
        local = 'Sorocaba'
    else:
        local = 'SP'

    label_texto = f"{local} - {duracao_dias} dias"
    labels_info.append({
        'inicio': inicio, 'fim': fim,
        'inicio_num': mdates.date2num(inicio), 'fim_num': mdates.date2num(fim),
        'texto': label_texto, 'cor': '#6c6b6bff',
        'largura_dias': len(label_texto) * 2.5, 'nivel': None
    })

# Resolucao de conflitos de labels
for i, label_info in enumerate(labels_info):
    nivel_escolhido = 0
    label_x_inicio = label_info['inicio_num'] + 1
    label_x_fim = label_x_inicio + label_info['largura_dias']
    for nivel_teste in range(10):
        tem_conflito = False
        for j in range(i):
            outro = labels_info[j]
            if outro['nivel'] == nivel_teste:
                outro_x_inicio = outro['inicio_num'] + 1
                outro_x_fim = outro_x_inicio + outro['largura_dias']
                if not (label_x_fim + 5 < outro_x_inicio or label_x_inicio - 5 > outro_x_fim):
                    tem_conflito = True
                    break
        if not tem_conflito:
            nivel_escolhido = nivel_teste
            break
    labels_info[i]['nivel'] = nivel_escolhido

# Background das viagens
for _, viagem in viagens_sorted.iterrows():
    ax1.axvspan(viagem['inicio'], viagem['fim'], alpha=0.12, color=COLORS['viagens_bg'], edgecolor='none', zorder=2)

# Labels
for label_info in labels_info:
    nivel = label_info['nivel']
    y_pos = max_value * 1.10 - (nivel * max_value * 0.045)
    ax1.text(label_info['inicio'] + timedelta(days=1), y_pos, label_info['texto'],
             fontsize=10, color=label_info['cor'], rotation=0, va='bottom', ha='left', alpha=0.85, zorder=15)

# Aniversarios
ax1.axvline(x=pd.Timestamp('2024-12-16'), color='#dc2626', linestyle='-', alpha=0.7, linewidth=2, zorder=10)
ax1.axvline(x=pd.Timestamp('2025-12-16'), color='#dc2626', linestyle='-', alpha=0.7, linewidth=2, zorder=10)

# Onda % juntos
ax2.fill_between(dates_smooth, pct_smooth, alpha=0.12, color=COLORS['pct_juntos'])
ax2.plot(dates_smooth, pct_smooth, linewidth=0, color=COLORS['pct_juntos'], alpha=0.8)
ax2.scatter(dates, pct_juntos_values, s=80, color=COLORS['pct_juntos'], edgecolors='white', linewidths=0, zorder=5)

for x, y in zip(dates, pct_juntos_values):
    if y > 0:
        ax2.text(x, y + 2.5, f'{y:.0f}%', ha='center', va='bottom',
                 fontsize=13, fontweight='bold', color=COLORS['pct_juntos'])

ax2.set_ylabel('% de Dias Juntos no Mes', fontsize=13, fontweight='bold', color=COLORS['pct_juntos'])
ax2.tick_params(axis='y', labelcolor=COLORS['pct_juntos'])
ax2.set_ylim(0, 120)
ax2.grid(False)

# Linhas de volume
ax1.plot(dates, text_values, marker='o', linewidth=1, color=COLORS['text'], alpha=0.5)
ax1.plot(dates, audio_values, marker='o', linewidth=1, color=COLORS['audio'], alpha=0.5)
ax1.plot(dates, video_values, marker='o', linewidth=1, color=COLORS['video'], alpha=0.5)
ax1.plot(dates, image_values, marker='o', linewidth=1, color=COLORS['image'], alpha=0.5)
ax1.plot(dates, p1_values, linewidth=3, color=COLORS['P1'], alpha=0.95)
ax1.plot(dates, p2_values, linewidth=3, color=COLORS['P2'], alpha=0.95)
ax1.plot(dates, total_values, linewidth=1, color=COLORS['total'], alpha=0.4, linestyle='--')

ax1.set_xlabel('Mes/Ano', fontsize=13, fontweight='bold')
ax1.set_ylabel('Numero de Mensagens', fontsize=13, fontweight='bold')
ax1.set_ylim(0, max_value * 1.13)
ax1.set_title('Timeline Ultimate (Ondulada)\n"Um Ano em Dados Completos"', fontsize=17, fontweight='bold', pad=20)
ax1.grid(False)

ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b/%y'))
ax1.xaxis.set_major_locator(mdates.MonthLocator())
ax1.tick_params(axis='x', rotation=45)
ax1.minorticks_off()
ax2.minorticks_off()

# Legendas
elementos_volume = [
    Line2D([0], [0], color=COLORS['P1'], linewidth=3, label='P1 (Marlon)'),
    Line2D([0], [0], color=COLORS['P2'], linewidth=3, label='P2 (Leticia)'),
    Line2D([0], [0], color=COLORS['total'], linewidth=1, linestyle='--', label='Total'),
    Line2D([0], [0], color=COLORS['text'], linewidth=1, marker='o', label='Texto'),
    Line2D([0], [0], color=COLORS['audio'], linewidth=1, marker='o', label='Audio'),
    Line2D([0], [0], color=COLORS['video'], linewidth=1, marker='o', label='Video'),
    Line2D([0], [0], color=COLORS['image'], linewidth=1, marker='o', label='Imagem'),
]
legend1 = ax1.legend(handles=elementos_volume, loc='upper left', bbox_to_anchor=(0.01, 0.50),
                     fontsize=10, framealpha=0.95, title='$\\mathbf{Volume de Mensagens}$',
                     title_fontsize=12, edgecolor='none', facecolor='none',
                     fancybox=False, shadow=False, alignment='left')

elementos_contexto = [
    Patch(facecolor=COLORS['pct_juntos'], alpha=0.3, edgecolor=COLORS['pct_juntos'], linewidth=2, label='% Dias Juntos'),
    Patch(facecolor=COLORS['viagens_bg'], alpha=0.12, edgecolor='gray', linewidth=0, label='Periodo de Viagem'),
    Line2D([0], [0], color='#dc2626', linewidth=2, label='Aniversario Namoro'),
]
legend2 = ax1.legend(handles=elementos_contexto, loc='upper left', bbox_to_anchor=(0.01, 0.70),
                     fontsize=10, framealpha=0.95, title='$\\mathbf{Contexto Temporal}$',
                     title_fontsize=12, edgecolor='none', facecolor='none',
                     fancybox=False, shadow=False, alignment='left')

total_p1 = p1_values.sum()
total_p2 = p2_values.sum()
total_geral = total_values.sum()
total_dias_separados = total_dias_periodo - total_dias_juntos
num_viagens = len(viagens_df)

stats_lines = [
    "• $\\mathbf{Total\\ Msgs:}$ " + f"{total_geral:,}",
    "• $\\mathbf{P1:}$ " + f"{total_p1:,} ({total_p1/total_geral*100:.1f}%)",
    "• $\\mathbf{P2:}$ " + f"{total_p2:,} ({total_p2/total_geral*100:.1f}%)",
    "• $\\mathbf{Dias\\ Juntos:}$ " + f"{total_dias_juntos} ({pct_ano_juntos:.1f}%)",
    "• $\\mathbf{Dias\\ Separados:}$ " + f"{total_dias_separados} ({100-pct_ano_juntos:.1f}%)",
    "• $\\mathbf{Viagens:}$ " + f"{num_viagens}"
]
elementos_stats = [Line2D([0], [0], color='none', label=line) for line in stats_lines]
legend3 = ax1.legend(handles=elementos_stats, loc='upper left', bbox_to_anchor=(0.01, 0.99),
                     fontsize=10, framealpha=1.0, title='$\\mathbf{Estatisticas}$',
                     title_fontsize=12, edgecolor='none', facecolor='none',
                     frameon=True, fancybox=False, shadow=False,
                     handlelength=0, handletextpad=0, labelspacing=0.6, borderpad=0.8, alignment='left')

ax1.add_artist(legend1)
ax1.add_artist(legend2)

plt.tight_layout()

# Salva
output_path = PROJECT_ROOT / 'assets' / 'images' / 'timeline-ultimate.png'
output_path.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
print(f"Salvo em: {output_path}")

plt.close()
