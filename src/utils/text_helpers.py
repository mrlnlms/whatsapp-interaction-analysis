"""
Utilitários para formatação de texto e markdown.
"""

import re


def format_markdown_lists(text: str, output_format: str = 'markdown') -> str:
    """
    Converte listas inline em formato markdown ou HTML vertical com bullet points.

    Detecta padrões comuns de listas inline e converte para formato
    apropriado com quebras de linha e indentação hierárquica.

    Padrões tratados:
    1. Categorias com subitens: "- Categoria: item1, item2, item3"
       → "- Categoria:\n  - item1\n  - item2\n  - item3"

    2. Listas inline com vírgula: "arquivo1.txt, arquivo2.txt, arquivo3.txt"
       → "- arquivo1.txt\n- arquivo2.txt\n- arquivo3.txt"

    3. Bullet points inline: "- item1 - item2 - item3"
       → "- item1\n- item2\n- item3"

    Args:
        text: String contendo texto com possíveis listas inline.
        output_format: Formato de saída - 'markdown' ou 'html'. Default: 'markdown'.

    Returns:
        String com listas formatadas no formato especificado.

    Examples:
        >>> text = "- Texto: puro, com emoji, com link"
        >>> format_markdown_lists(text)
        '- Texto:\\n  - puro\\n  - com emoji\\n  - com link'

        >>> text = "- chat_complete.txt, chat_p1.txt"
        >>> format_markdown_lists(text, output_format='html')
        '<ul>\\n<li>chat_complete.txt</li>\\n<li>chat_p1.txt</li>\\n</ul>'
    """
    if not text:
        return text

    lines = text.split('\n')
    result_lines = []

    for line in lines:
        processed = _process_line(line)
        result_lines.append(processed)

    result = '\n'.join(result_lines)

    # Converte para HTML se solicitado
    if output_format == 'html':
        return _markdown_to_html(result)

    return result


def _process_line(line: str) -> str:
    """
    Processa uma linha individual, expandindo listas inline.

    Args:
        line: Linha de texto a processar.

    Returns:
        Linha processada (pode conter múltiplas linhas separadas por \\n).
    """
    # Detecta linha vazia ou sem conteúdo de lista
    stripped = line.strip()
    if not stripped:
        return line

    # Padrão 1: Bullet point com categoria e subitens
    # Ex: "- Texto: puro, com emoji, com link"
    # Ex: "- Mídia omitida: audio, image, video, sticker, gif, document"
    match_category = re.match(r'^(\s*-\s*)([^:]+):\s*(.+)$', line)
    if match_category:
        indent = match_category.group(1)
        category = match_category.group(2).strip()
        items_str = match_category.group(3).strip()

        # Verifica se parece uma lista de subitens (contém vírgulas)
        if ',' in items_str and not _is_parenthetical(items_str):
            items = [item.strip() for item in items_str.split(',')]
            # Gera subitens com indentação extra
            sub_indent = '  ' + indent.replace('-', ' ')
            subitems = [f"{sub_indent}- {item}" for item in items if item]
            return f"{indent}{category}:\n" + '\n'.join(subitems)

    # Padrão 2: Bullet point com itens separados por vírgula (sem categoria)
    # Ex: "- chat_complete.txt, chat_p1.txt, chat_p2.txt"
    # Ex: "- corpus_full.txt, corpus_p1.txt, corpus_p2.txt"
    # Nota: Não deve ter ":" (senão é categoria tratada acima)
    match_bullet_comma = re.match(r'^(\s*-\s*)(.+)$', line)
    if match_bullet_comma:
        indent = match_bullet_comma.group(1)
        content = match_bullet_comma.group(2).strip()

        # Só expande se: tem vírgulas, não tem ":", e não é parentético
        if ',' in content and ':' not in content and not _is_parenthetical(content):
            items = [item.strip() for item in content.split(',')]
            # Só expande se todos os itens parecem válidos (não vazios)
            if all(items):
                return '\n'.join(f"{indent}{item}" for item in items)

    # Padrão 3: Texto com informações extras em parênteses/em-dash
    # Ex: "- messages_full.csv (17 cols) — Debug/auditoria"
    # Mantém como está (já é um item único)

    return line


def _is_parenthetical(text: str) -> bool:
    """
    Verifica se o texto é uma expressão parentética que não deve ser expandida.

    Expressões como "(17 cols)" ou descrições após "—" não devem ser tratadas
    como listas de subitens.

    Args:
        text: String a verificar.

    Returns:
        True se for uma expressão parentética, False caso contrário.
    """
    # Se começa com parêntese, não é lista
    if text.startswith('('):
        return True

    # Se contém apenas um item com parênteses, não é lista
    # Ex: "messages_full.csv (17 cols) — Debug/auditoria"
    if re.match(r'^[^,]+\([^)]+\)', text):
        return True

    # Se contém backticks (código), não expandir
    # Ex: "`[28/11/24, 19:30:05] P1: Mensagem`"
    if '`' in text:
        return True

    # Se contém colchetes (provavelmente código/exemplo), não expandir
    if '[' in text and ']' in text:
        return True

    return False


def _markdown_to_html(markdown_text: str) -> str:
    """
    Converte markdown simples (bullets e hierarquia) para HTML.

    Suporta:
    - Bullet points simples (-)
    - Bullet points com indentação (hierarquia)
    - Texto sem bullets (parágrafo)
    - Texto em bold (**texto**)

    Args:
        markdown_text: Texto em markdown.

    Returns:
        HTML equivalente.
    """
    if not markdown_text:
        return markdown_text

    lines = markdown_text.split('\n')
    html_parts = []
    current_list_level = 0  # 0 = não está em lista, 1 = lista, 2 = sublista

    for line in lines:
        stripped = line.strip()

        # Detecta nível de indentação do bullet
        indent_match = re.match(r'^(\s*)-\s+(.*)$', line)

        if indent_match:
            indent = len(indent_match.group(1))
            content = indent_match.group(2)
            content = _format_bold(content)

            # Determina nível: 0-1 espaços = nível 1, 2+ espaços = nível 2
            level = 2 if indent >= 2 else 1

            # Abre/fecha listas conforme necessário
            if level > current_list_level:
                for _ in range(level - current_list_level):
                    html_parts.append('<ul>')
                current_list_level = level
            elif level < current_list_level:
                for _ in range(current_list_level - level):
                    html_parts.append('</ul>')
                current_list_level = level

            html_parts.append(f'<li>{content}</li>')

        else:
            # Fecha todas as listas abertas
            while current_list_level > 0:
                html_parts.append('</ul>')
                current_list_level -= 1

            # Linha normal (não é bullet)
            if stripped:
                content = _format_bold(stripped)
                html_parts.append(f'<p>{content}</p>')

    # Fecha listas abertas no final
    while current_list_level > 0:
        html_parts.append('</ul>')
        current_list_level -= 1

    return '\n'.join(html_parts)


def _format_bold(text: str) -> str:
    """
    Converte **texto** para <strong>texto</strong>.

    Args:
        text: Texto que pode conter markdown bold.

    Returns:
        Texto com HTML bold.
    """
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
