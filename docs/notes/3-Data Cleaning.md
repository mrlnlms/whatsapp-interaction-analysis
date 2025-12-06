# Data Cleaning

Limpeza e normalização do arquivo bruto

📁 Projeto: whatsapp-ds-analytics

## Data Cleaning

Com base nas descobertas documentadas no [Data Profiling](http://localhost:7860/notebooks/00-data-profiling.html), esta etapa implementa as transformações de limpeza necessárias para preparar o arquivo bruto para parsing e análise.

## Objetivo

Transformar o arquivo bruto exportado do WhatsApp em um arquivo limpo e otimizado, removendo caracteres invisíveis, linhas vazias, normalizando espaços e anonimizando participantes.

---

## Configuração do Pipeline

| Entrada | `raw-data.txt` | ~/whatsapp-ds-analytics/data/raw/export\_2024-10\_2025-10 |
| --- | --- | --- |
| Saída | `export_2024-10_2025-10` | ~/whatsapp-ds-analytics/data/interim/export\_2024-10\_2025-10 |

---

## Execução do Pipeline

| 1 | Remoção U+200E | 48,699 caracteres |
| --- | --- | --- |
| 2 | Anonimização | 91,968 substituições |
| 3 | Otimização timestamps | 91,968 timestamps |
| 4 | Normalização indentação | 3,038 espaços |
| 5 | Remoção linhas vazias | 1,156 linhas |
| 6 | Normalização espaços | 1,003 bytes |
| 7 | Remoção timestamps vazios | 39 linhas |

```
✅ Pipeline concluído!

📉 Redução: 5.04 MB → 4.10 MB (18.6%)
📄 Arquivo: raw-data_cln7.txt
```

---

## Pipeline de Transformação

### Etapa 1: Remoção U+200E

O caractere `U+200E` (Left-to-Right Mark) é um caractere de formatação invisível usado para controle de direção de texto. O WhatsApp o insere sistematicamente durante a exportação, mas não carrega informação semântica útil.

**Impacto identificado:** ~48.700 ocorrências, ~243 KB, presente em ~50% das linhas.

**Resultado:**

- Caracteres Removidos: 48,699

**Auditoria:**

| Entrada | 5.04 MB (97,333 linhas) |
| --- | --- |
| Saída | 4.81 MB (97,333 linhas) |
| Redução | 243,430 bytes (4.61%) |

### Etapa 2: Anonimização

Substitui nomes dos participantes por identificadores genéricos: - Marlon → P1 - Lê 🖤 → P2

**Resultado:**

- Marlon: 46,975
- Lê 🖤: 44,993

**Auditoria:**

| Entrada | 4.81 MB (97,333 linhas) |
| --- | --- |
| Saída | 4.37 MB (97,333 linhas) |
| Redução | 457,858 bytes (9.08%) |

### Etapa 4: Normalização indentação

Remove espaços/tabs iniciais de linhas de continuação (mensagens multilinha). Esses espaços são visuais e não carregam informação semântica.

**Resultado:**

- Espacos Removidos: 3,038

**Auditoria:**

| Entrada | 4.11 MB (97,333 linhas) |
| --- | --- |
| Saída | 4.10 MB (97,333 linhas) |
| Redução | 3,038 bytes (0.07%) |

### Etapa 5: Remoção linhas vazias

Linhas completamente vazias (apenas `\n`) aparecem entre mensagens e não carregam informação. Serão removidas preservando a formatação interna.

**Resultado:**

- Linhas Removidas: 1,156

**Auditoria:**

| Entrada | 4.10 MB (97,333 linhas) |
| --- | --- |
| Saída | 4.10 MB (96,177 linhas) |
| Redução | 1,156 bytes (0.03%) |

### Etapa 6: Normalização espaços

Normaliza espaços em branco internos: - Múltiplos espaços → espaço único - Tabs → espaço único  
\- Trailing whitespace → removido - **Preserva:** Indentação inicial

**Resultado:**

- Bytes Economizados: 1,003

**Auditoria:**

| Entrada | 4.10 MB (96,177 linhas) |
| --- | --- |
| Saída | 4.10 MB (96,177 linhas) |
| Redução | 1,003 bytes (0.02%) |

---

## Auditoria Final do Pipeline

| 📄 Original (raw-data.txt) | 97,333 | 4,846,244 | 5.04 MB | \- | \- | \- |
| --- | --- | --- | --- | --- | --- | --- |
| └─ Remoção U+200E | 97,333 | 4,797,545 | 4.81 MB | \- | \-48,699 | \-4.61% |
| └─ Anonimização | 97,333 | 4,519,659 | 4.37 MB | \- | \-277,886 | \-9.08% |
| └─ Otimização timestamps | 97,333 | 4,243,755 | 4.11 MB | \- | \-275,904 | \-6.02% |
| └─ Normalização indentação | 97,333 | 4,240,717 | 4.10 MB | \- | \-3,038 | \-0.07% |
| └─ Remoção linhas vazias | 96,177 | 4,239,561 | 4.10 MB | \-1,156 | \-1,156 | \-0.03% |
| └─ Normalização espaços | 96,177 | 4,238,560 | 4.10 MB | \- | \-1,001 | \-0.02% |
| └─ Remoção timestamps vazios | 96,138 | 4,237,702 | 4.10 MB | \-39 | \-858 | \-0.02% |

| 1️⃣ Remoção U+200E | 4.81 MB | 243,430 | \- | 48,699 | 4.61% |
| --- | --- | --- | --- | --- | --- |
| 2️⃣ Anonimização | 4.37 MB | 457,858 | \- | 277,886 | 9.08% |
| 3️⃣ Otimização timestamps | 4.11 MB | 275,904 | \- | 275,904 | 6.02% |
| 4️⃣ Normalização indentação | 4.10 MB | 3,038 | \- | 3,038 | 0.07% |
| 5️⃣ Remoção linhas vazias | 4.10 MB | 1,156 | 1,156 | 1,156 | 0.03% |
| 6️⃣ Normalização espaços | 4.10 MB | 1,003 | \- | 1,001 | 0.02% |
| 7️⃣ Remoção timestamps vazios | 4.10 MB | 858 | 39 | 858 | 0.02% |

---

## 🎯 Resultado Final

| Arquivo original | 5.04 MB |
| --- | --- |
| Arquivo final | 4.10 MB |
| Redução (bytes) | 983,247 |
| Redução (%) | 18.61% |
| Linhas removidas | 1,195 |
| Caracteres removidos | 608,542 |

✅ **Arquivo de saída:** raw-data\_cln7.txt

O arquivo limpo está pronto para a próxima etapa: **parsing e estruturação em DataFrame**.

---

## 💡 Impacto da Limpeza

**Benefícios:**

- Menos dados para armazenar
- Processamento mais rápido
- Transferências mais eficientes

---

## Arquivo de Saída

O arquivo final agora possui:

- ✅ Formato otimizado: `DD/MM/YY HH:MM:SS Remetente: Conteúdo`
- ✅ Participantes anonimizados (P1, P2)
- ✅ Sem caracteres invisíveis
- ✅ Sem linhas/timestamps vazios
- ✅ Espaços e indentação normalizados

Note 📋 Regex para parsing do arquivo limpo

```python
# Padrão para identificar início de mensagem
message_pattern = r'^(\d{2}/\d{2}/\d{2}) (\d{2}:\d{2}:\d{2}) (.+?): (.*)$'

# Grupos de captura:
# 1: Data (DD/MM/YY)
# 2: Hora (HH:MM:SS)
# 3: Remetente (P1 ou P2)
# 4: Conteúdo da mensagem
```

---

## Próximos Passos

Com o arquivo limpo, seguimos para:

1. [**Data Wrangling**](http://localhost:7860/notebooks/02-data-wrangling.html) — Parsing, agregação de multilinha, vinculação de mídia