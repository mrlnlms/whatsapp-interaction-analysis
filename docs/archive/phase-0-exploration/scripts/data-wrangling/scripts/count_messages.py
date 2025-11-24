import re

# Caminho do arquivo
file_path = '/Users/mosx/Desktop/local-workbench/whats-le/data-wrangling/data/raw-data.txt'

# Regex para capturar timestamps no formato: [DD/MM/YY, HH:MM:SS]
# Aceita um caractere invisível (LTR/U+200E) no início
timestamp_pattern = re.compile(r'‎?\[(\d{2}/\d{2}/\d{2}, \d{1,2}:\d{2}:\d{2})\]')

# Contagem
message_count = 0
sample_timestamps = []

# Contar linhas
line_count = 0

with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
        line_count += 1
        match = timestamp_pattern.search(line)
        if match:
            message_count += 1
            if len(sample_timestamps) < 5:
                sample_timestamps.append(match.group(1))

# Resultado
print(f"📊 Total de linhas no arquivo: {line_count}")
print(f"✅ Total de mensagens reais detectadas: {message_count}")
print(f"💡 Diferença (linhas - mensagens): {line_count - message_count}")

print("\nExemplos de timestamps encontrados:")
for ts in sample_timestamps:
    print(f"  - {ts}")