"""
Funções de limpeza e pipeline de transformação para dados do WhatsApp.

Uso:
    from cleaning import run_pipeline, CLEANING_STEPS
    
    result = run_pipeline(
        order=['u200e', 'empty_timestamps', 'anonymize'],
        raw_file=Path('raw-data.txt'),
        output_dir=Path('data/interim')
    )
"""

import re
from pathlib import Path
from utils import audit_transformation, audit_pipeline


# =============================================================================
# FUNÇÕES DE TRANSFORMAÇÃO
# Cada função recebe (input_file, output_file) e retorna dict com métricas
# =============================================================================

def remove_u200e(input_file, output_file):
    """
    Remove todas as ocorrências do caractere invisível U+200E.
    
    O caractere U+200E (Left-to-Right Mark) é inserido pelo WhatsApp durante
    a exportação para controle de direção de texto, mas não carrega informação
    semântica útil para análise.
    """
    invisible_char = '\u200e'
    total = 0
    
    with open(input_file, 'r', encoding='utf-8') as f_in:
        with open(output_file, 'w', encoding='utf-8') as f_out:
            for line in f_in:
                total += line.count(invisible_char)
                f_out.write(line.replace(invisible_char, ''))
    
    return {'caracteres_removidos': total}


def remove_empty_timestamps(input_file, output_file):
    """
    Remove timestamps vazios seguidos de múltiplas mídias consecutivas.
    
    Quando múltiplas mídias são enviadas simultaneamente, o WhatsApp registra
    uma linha com timestamp e remetente vazios, seguida das mídias. A primeira
    linha é redundante e pode ser removida.
    """
    timestamp_pattern = r'^\[\d{2}/\d{2}/\d{2}, \d{2}:\d{2}:\d{2}\]'
    media_patterns = [
        '<attached:', 'audio omitted', 'image omitted', 'video omitted', 
        'sticker omitted', 'GIF omitted', 'document omitted'
    ]
    
    lines = open(input_file, 'r', encoding='utf-8').readlines()
    skip = set()
    
    for i in range(len(lines) - 2):
        curr = lines[i].strip()
        next1 = lines[i + 1].strip()
        next2 = lines[i + 2].strip()
        
        if (re.match(timestamp_pattern, curr) and curr.endswith(':') and 
            re.match(timestamp_pattern, next1)):
            has_media_next = any(p in next1 for p in media_patterns)
            has_media_next2 = (re.match(timestamp_pattern, next2) and 
                               any(p in next2 for p in media_patterns))
            
            if has_media_next and has_media_next2:
                skip.add(i)
    
    cleaned = [l for i, l in enumerate(lines) if i not in skip]
    open(output_file, 'w', encoding='utf-8').writelines(cleaned)
    
    return {'linhas_removidas': len(skip)}


def remove_empty_lines(input_file, output_file):
    """
    Remove linhas completamente vazias.
    
    Linhas que contêm apenas \\n não carregam informação e podem ser removidas
    para reduzir o tamanho do arquivo.
    """
    lines = open(input_file, 'r', encoding='utf-8').readlines()
    cleaned = [l for l in lines if l != '\n']
    open(output_file, 'w', encoding='utf-8').writelines(cleaned)
    
    return {'linhas_removidas': len(lines) - len(cleaned)}


def normalize_whitespace(input_file, output_file):
    """
    Normaliza espaços em branco internos, preservando indentação.
    
    - Múltiplos espaços consecutivos → espaço único
    - Tabs → espaço único
    - Trailing whitespace → removido
    - Indentação inicial → preservada (tratada em etapa separada)
    """
    lines = open(input_file, 'r', encoding='utf-8').readlines()
    cleaned = []
    
    for line in lines:
        line = line.rstrip() + '\n'
        indent = len(line) - len(line.lstrip())
        content = line[indent:].replace('\t', ' ')
        content = re.sub(r' {2,}', ' ', content)
        cleaned.append(line[:indent] + content)
    
    open(output_file, 'w', encoding='utf-8').writelines(cleaned)
    
    orig_size = sum(len(l.encode('utf-8')) for l in lines)
    clean_size = sum(len(l.encode('utf-8')) for l in cleaned)
    
    return {'bytes_economizados': orig_size - clean_size}


def anonymize_participants(input_file, output_file):
    """
    Substitui nomes dos participantes por identificadores anônimos.
    
    Mapeamento padrão:
    - Marlon → P1
    - Lê 🖤 → P2
    """
    mapping = {'Marlon': 'P1', 'Lê 🖤': 'P2'}
    
    lines = open(input_file, 'r', encoding='utf-8').readlines()
    result = []
    counts = {k: 0 for k in mapping}
    
    for line in lines:
        for name, anon in mapping.items():
            if f'] {name}:' in line:
                line = line.replace(f'] {name}:', f'] {anon}:')
                counts[name] += 1
        result.append(line)
    
    open(output_file, 'w', encoding='utf-8').writelines(result)
    
    return {'substituicoes': counts}


def optimize_timestamps(input_file, output_file):
    """
    Remove delimitadores redundantes do timestamp.
    
    Transforma: [28/11/24, 19:30:05] P1: Mensagem
    Em:         28/11/24 19:30:05 P1: Mensagem
    
    Economiza 4 caracteres por mensagem e facilita o parsing.
    """
    pattern = r'^\[(\d{2}/\d{2}/\d{2}), (\d{2}:\d{2}:\d{2})\]'
    
    lines = open(input_file, 'r', encoding='utf-8').readlines()
    result = []
    count = 0
    
    for line in lines:
        match = re.match(pattern, line)
        if match:
            result.append(f"{match.group(1)} {match.group(2)}" + line[len(match.group(0)):])
            count += 1
        else:
            result.append(line)
    
    open(output_file, 'w', encoding='utf-8').writelines(result)
    
    return {'timestamps_otimizados': count}


def normalize_indentation(input_file, output_file):
    """
    Remove indentação de linhas de continuação.
    
    Mensagens multilinha frequentemente contêm espaços de indentação no início
    das linhas de continuação. Esses espaços são visuais e não carregam
    informação semântica.
    """
    timestamp_pattern = r'^\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}'
    
    lines = open(input_file, 'r', encoding='utf-8').readlines()
    result = []
    spaces = 0
    
    for line in lines:
        # Se NÃO começa com timestamp, é linha de continuação
        if not re.match(timestamp_pattern, line):
            orig_len = len(line)
            line = line.lstrip(' \t')
            spaces += orig_len - len(line)
        result.append(line)
    
    open(output_file, 'w', encoding='utf-8').writelines(result)
    
    return {'espacos_removidos': spaces}


# =============================================================================
# REGISTRO DE ETAPAS DISPONÍVEIS
# Cada etapa tem: id, name, function, description
# =============================================================================

CLEANING_STEPS = {
    'u200e': {
        'name': 'Remoção U+200E',
        'function': remove_u200e,
        'description': '''O caractere `U+200E` (Left-to-Right Mark) é um caractere de formatação invisível 
usado para controle de direção de texto. O WhatsApp o insere sistematicamente 
durante a exportação, mas não carrega informação semântica útil.

**Impacto identificado:** ~48.700 ocorrências, ~243 KB, presente em ~50% das linhas.'''
    },
    'empty_timestamps': {
        'name': 'Remoção timestamps vazios',
        'function': remove_empty_timestamps,
        'description': '''Quando múltiplas mídias são enviadas simultaneamente, o WhatsApp registra uma 
linha com timestamp vazio seguida das mídias. A primeira linha é redundante.'''
    },
    'empty_lines': {
        'name': 'Remoção linhas vazias',
        'function': remove_empty_lines,
        'description': '''Linhas completamente vazias (apenas `\\n`) aparecem entre mensagens e não 
carregam informação. Serão removidas preservando a formatação interna.'''
    },
    'whitespace': {
        'name': 'Normalização espaços',
        'function': normalize_whitespace,
        'description': '''Normaliza espaços em branco internos:
- Múltiplos espaços → espaço único
- Tabs → espaço único  
- Trailing whitespace → removido
- **Preserva:** Indentação inicial'''
    },
    'anonymize': {
        'name': 'Anonimização',
        'function': anonymize_participants,
        'description': '''Substitui nomes dos participantes por identificadores genéricos:
- Marlon → P1
- Lê 🖤 → P2'''
    },
    'timestamps': {
        'name': 'Otimização timestamps',
        'function': optimize_timestamps,
        'description': '''Remove delimitadores redundantes para facilitar o parsing:
- De: `[28/11/24, 19:30:05] P1: Mensagem`
- Para: `28/11/24 19:30:05 P1: Mensagem`'''
    },
    'indentation': {
        'name': 'Normalização indentação',
        'function': normalize_indentation,
        'description': '''Remove espaços/tabs iniciais de linhas de continuação (mensagens multilinha).
Esses espaços são visuais e não carregam informação semântica.'''
    },
}


# =============================================================================
# EXECUTOR DO PIPELINE
# =============================================================================

def run_pipeline(order: list, raw_file: Path, output_dir: Path, show_progress: bool = True) -> dict:
    """
    Executa pipeline de limpeza na ordem especificada.
    
    Args:
        order: Lista de IDs das etapas na ordem desejada.
                Ex: ['u200e', 'anonymize', 'timestamps']
        raw_file: Path do arquivo de entrada (raw-data.txt)
        output_dir: Path do diretório para arquivos intermediários
        show_progress: Se True, imprime progresso no console
        
    Returns:
        Dict com:
        - outputs: {step_id: Path} - Caminhos dos arquivos gerados
        - audits: {step_id: dict} - Resultados das auditorias
        - metrics: {step_id: dict} - Métricas retornadas pelas funções
        - order: list - Ordem executada
        - steps: dict - Referência para CLEANING_STEPS
        - df_audit: DataFrame - Auditoria consolidada
        - totals: dict - Totais do pipeline
        - final_output: Path - Arquivo final gerado
        
    Raises:
        ValueError: Se algum step_id não existir em CLEANING_STEPS
        
    Example:
        result = run_pipeline(
            order=['u200e', 'empty_timestamps', 'anonymize'],
            raw_file=Path('data/raw/raw-data.txt'),
            output_dir=Path('data/interim')
        )
        
        # Acessa resultados
        print(result['totals']['total_percent'])  # Redução total %
        print(result['final_output'])  # Arquivo final
    """
    # Valida IDs
    invalid_ids = [sid for sid in order if sid not in CLEANING_STEPS]
    if invalid_ids:
        raise ValueError(f"IDs de etapa inválidos: {invalid_ids}. "
                        f"Disponíveis: {list(CLEANING_STEPS.keys())}")
    
    # Garante que output_dir existe
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    raw_file = Path(raw_file)
    
    outputs = {}
    audits = {}
    metrics = {}
    
    previous = raw_file
    
    if show_progress:
        print(f"🔄 Executando pipeline com {len(order)} etapas...\n")
    
    for i, step_id in enumerate(order):
        step = CLEANING_STEPS[step_id]
        step_num = i + 1
        output_file = output_dir / f'raw-data_cln{step_num}.txt'
        
        if show_progress:
            print(f"   {step_num}. {step['name']}...", end=' ')
        
        # Executa transformação
        step_metrics = step['function'](previous, output_file)
        
        # Auditoria
        audit = audit_transformation(
            previous, 
            output_file, 
            step['name'],
            show_output=False
        )
        
        if show_progress:
            print(f"✅ (-{audit['delta_percent']:.2f}%)")
        
        # Guarda resultados
        outputs[step_id] = output_file
        audits[step_id] = audit
        metrics[step_id] = step_metrics
        
        # Próxima etapa usa este output
        previous = output_file
    
    # Auditoria final consolidada
    stages = [{'file': str(raw_file), 'name': '📄 Original (raw-data.txt)'}]
    for step_id in order:
        stages.append({
            'file': str(outputs[step_id]),
            'name': f"└─ {CLEANING_STEPS[step_id]['name']}"
        })
    
    df_audit, totals = audit_pipeline(stages, show_output=False)
    
    if show_progress:
        print(f"\n✅ Pipeline concluído!")
        print(f"   📦 Redução total: {totals['total_percent']:.2f}%")
        print(f"   📁 Arquivo final: {previous.name}")
    
    return {
        'outputs': outputs,
        'audits': audits,
        'metrics': metrics,
        'order': order,
        'steps': CLEANING_STEPS,
        'df_audit': df_audit,
        'totals': totals,
        'final_output': previous
    }


def get_available_steps() -> list:
    """
    Retorna lista de IDs de etapas disponíveis.
    
    Returns:
        Lista de strings com IDs válidos para usar em run_pipeline()
    """
    return list(CLEANING_STEPS.keys())


def get_step_info(step_id: str) -> dict:
    """
    Retorna informações sobre uma etapa específica.
    
    Args:
        step_id: ID da etapa
        
    Returns:
        Dict com name, function, description
        
    Raises:
        KeyError: Se step_id não existir
    """
    return CLEANING_STEPS[step_id]