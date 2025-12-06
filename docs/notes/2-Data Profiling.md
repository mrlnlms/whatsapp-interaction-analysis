# Data Profiling

Catalogação sistemática de padrões e edge cases

## Configuração

| Arquivo | `raw-data.txt` | ~/whatsapp-ds-analytics/data/raw/export\_2024-10\_2025-10 |
| --- | --- | --- |

---

## Data Profiling

Após a exploração inicial no [Data Discovery](http://localhost:7860/notebooks/00-data-discovery.html), chegou o momento de **sistematizar e aprofundar as descobertas**. Enquanto o Discovery ofereceu uma primeira impressão visual e métrica, esta etapa vai além: investiga **sistematicamente** cada elemento estrutural do arquivo, cataloga **todos os tipos de padrões** (não apenas os visíveis à primeira vista), e documenta **edge cases** que podem quebrar parsers ingênuos.

Esta seção cria uma referência técnica completa que fundamenta as decisões de limpeza e parsing nas etapas seguintes.

## Elementos Estruturais

### Remetentes

Após o timestamp, o nome do remetente aparece seguido de dois pontos (`:`).

| 0 | 9734 | \[04/01/25, 17:26:26\] Marlon: image omitted |
| --- | --- | --- |
| 1 | 9735 | \[04/01/25, 17:26:33\] Marlon: Vou voltar todo t... |
| 2 | 9736 | \[04/01/25, 17:26:46\] Lê 🖤: https://www.instagr... |

> Remetentes podem conter **emojis** e **caracteres especiais** (ex: `Lê 🖤`). O parser precisa considerar isso.

### Caractere Invisível U+200E

O caractere `U+200E` (Left-to-Right Mark) aparece frequentemente no export. É um caractere de controle de direção de texto.

**Estatísticas do U+200E:**

- Total de ocorrências: 48,699
- Linhas afetadas: 24,716

**Exemplos de linhas com U+200E:**

| 0 | 3 | \[19/10/24, 13:53:25\] Marlon: image omitted |
| --- | --- | --- |
| 1 | 4 | \[19/10/24, 13:53:41\] Lê 🖤: sticker omitted |
| 2 | 6 | \[19/10/24, 13:54:34\] Marlon: image omitted |
| 3 | 7 | \[19/10/24, 13:56:05\] Marlon: image omitted |
| 4 | 12 | \[19/10/24, 13:57:32\] Marlon: image omitted |

Warning Decisão de Cleaning

Este caractere será **removido** na etapa de limpeza pois:

- Não carrega informação semântica útil
- Complica o parsing com regex
- Representa ~4.6% do tamanho do arquivo

---

## Taxonomia de Mensagens

### Mensagens de Texto

#### Texto Puro

| 0 | 1 | \[19/10/24, 13:52:51\] Marlon: Le? |
| --- | --- | --- |
| 1 | 2 | \[19/10/24, 13:53:25\] Lê 🖤: https://www.localiz... |
| 2 | 5 | \[19/10/24, 13:53:43\] Lê 🖤: Oi |

#### Texto com Emojis

| 0 | 2258 | \[10/12/24, 16:28:34\] Marlon: Ta mara ❤️ bora q... |
| --- | --- | --- |
| 1 | 3883 | \[24/12/24, 14:56:55\] Marlon: Te amo ❤️ |

#### Texto com Links

| 0 | 2 | \[19/10/24, 13:53:25\] Lê 🖤: https://www.localiz... |
| --- | --- | --- |
| 1 | 26 | \[19/10/24, 14:23:23\] Marlon: https://www.airbn... |
| 2 | 209 | \[22/11/24, 17:59:35\] Lê 🖤: https://www.airbnb.... |

#### Linhas de Continuação

Mensagens longas podem ocupar múltiplas linhas. Linhas sem timestamp são continuações da mensagem anterior.

- Total de linhas sem timestamp: 29,297
- Estas são linhas de continuação de mensagens multilinha.

Warning Decisão de Wrangling

O parser deve **agregar** linhas de continuação ao conteúdo da mensagem anterior, preservando quebras de linha originais.

### Mensagens de Mídia

#### Mídias Omitidas

Quando o export não inclui os arquivos de mídia:

**Contagem de mídias omitidas:**

| audio omitted | 8,040 |
| --- | --- |
| image omitted | 3,287 |
| video omitted | 248 |
| sticker omitted | 1,869 |
| GIF omitted | 28 |
| document omitted | 38 |

**Exemplos de mídia omitida:**

| 0 | 18 | \[19/10/24, 14:11:39\] Marlon: audio omitted |
| --- | --- | --- |
| 1 | 23 | \[19/10/24, 14:17:39\] Marlon: audio omitted |

#### Mídias Anexadas

Quando o export inclui os arquivos:

- Mídias anexadas: 1,254

**Exemplos de mídia anexada:**

| 0 | 90360 | \[28/08/25, 11:52:19\] Marlon: |
| --- | --- | --- |
| 1 | 90845 | \[03/09/25, 13:50:06\] Lê 🖤: |

Warning Padrão de nomenclatura dos arquivos

`NÚMERO-TIPO-DATA-HORA.extensão`

Exemplo: `00000001-AUDIO-2025-08-21-21-31-39.opus`

### Mensagens Especiais

### Visão Consolidada

Após investigar sistematicamente todos os elementos, podemos visualizar a estrutura completa do arquivo:

**🌲 Estrutura do Arquivo WhatsApp Export**

```
Elementos Estruturais
│
├── Timestamp [DD/MM/YY, HH:MM:SS]
├── Remetente (nome + emoji)
├── Separador (:)
├── Conteúdo da mensagem
└── Caractere invisível U+200E (Left-to-Right Mark)

Taxonomia de Mensagens
│
├── Texto
│   ├── Puro (texto simples)
│   ├── Com Emoji (😂❤️🥰)
│   ├── Com Link (URLs compartilhadas)
│   └── Multilinha (linhas de continuação)
│
├── Mídia
│   ├── Omitida
│   │   ├── audio omitted
│   │   ├── image omitted
│   │   ├── video omitted
│   │   ├── sticker omitted
│   │   ├── GIF omitted
│   │   └── document omitted
│   │
│   └── Anexada
│       ├── Áudio (.opus, .mp3)
│       ├── Vídeo (.mp4)
│       ├── Imagem (.jpg, .png)
│       └── Documento (.pdf, .docx)
│
└── Especial
    ├── Editada (<This message was edited>)
    ├── Deletada (This message was deleted)
    └── Chamada (Missed/Voice/Video call)
```

---

## Resumo das Descobertas

| Caractere U+200E em ~50% das linhas | Remover todas ocorrências |
| --- | --- |
| Timestamps vazios ocasionais | Remover linhas |
| Linhas completamente vazias | Remover |
| Espaços múltiplos | Normalizar para espaço único |
| Nomes dos participantes | Anonimizar (P1, P2) |
| Formato timestamp `[DD/MM/YY, HH:MM:SS]` | Simplificar para `DD/MM/YY HH:MM:SS` |

| Linhas de continuação (multi-linha) | Agregar ao conteúdo da mensagem anterior |
| --- | --- |
| Mídias omitidas vs anexadas | Classificar em `status_midia` |
| Arquivos físicos de mídia | Vincular pelo nome do arquivo |
| Áudios e vídeos anexados | Transcrever via API (Groq/Whisper) |

```python
# Timestamp
r'^\[(\d{2}/\d{2}/\d{2}), (\d{2}:\d{2}:\d{2})\]'

# Mensagem completa (após otimização)
r'^(\d{2}/\d{2}/\d{2}) (\d{2}:\d{2}:\d{2}) (.+?): (.*)$'

# Mídia omitida
r'(audio|image|video|sticker|GIF|document) omitted'

# Mídia anexada
r'<attached: (.+?)>'
```

---

## Próximos Passos

Com o profiling completo, seguimos para:

1. [**Data Cleaning**](http://localhost:7860/notebooks/01-data-cleaning.html) — Implementar limpeza baseada nas descobertas