# Notas de Análise e Definições do Pipeline

## 1. Decisões Conceituais e Estratégias de Classificação

### 1.1 Sobre o Caractere Invisível `[U+200E]`

**Função:** Pode ser usado como marcador para identificar mensagens especiais (mídia, editadas, excluídas).

**Limitações importantes:** - ⚠️ Não aparece em **todas** as mensagens de mídia, editadas ou excluídas - ⚠️ Pode aparecer em outros contextos além desses - ⚠️ Confiar exclusivamente nele pode levar a erros de classificação

**Estratégia recomendada:**

-   Analisar o contexto completo da mensagem

-   Usar uma combinação de padrões para identificação precisa

-   Remover após extração das informações relevantes

### 1.2 Classificação de Mensagens de Mídia

**Hipótese:** No momento da exportação, o WhatsApp pode não baixar todos os arquivos de mídia.

**Classificação proposta:**

| Categoria | Indicador | Descrição | Exemplo |
|------------------|------------------|------------------|------------------|
| `media_omitted` | `omitted` no texto | Arquivo não foi exportado | `‎audio omitted` |
| `media_attached` | `<attached: filename>` | Arquivo foi exportado | `<attached: 00001-PHOTO-2025-08-21.jpg>` |
| `media_unknown` | Sem indicador claro | Padrão indefinido | Casos raros sem marcação |

**Simplificação alternativa:** - Unificar como `media` (tipo geral) - Usar flag `is_available` (boolean) - Usar campo `file_path` (vazio quando omitted)

### 1.3 Extração de Tipo de Mídia

**Fonte primária:** Nome do arquivo anexado

**Padrão dos nomes:**

```         
NNNNNNNN-TIPO-YYYY-MM-DD-HH-MM-SS.ext
```

**Exemplos:** - `00000001-PHOTO-2025-08-21-22-06-35.jpg` → tipo `PHOTO` - `-0000015-AUDIO-2025-08-21-21-31-39.opus` → tipo `AUDIO` - `00000298-STICKER-2025-08-25-09-10-40.webp` → tipo `STICKER` - `00001238-VIDEO-2025-09-03-13-50-07.mp4` → tipo `VIDEO` - `-0001788-Lu mãe.vcf` → tipo `CONTACT` (VCF)

**Regex sugerida:**

``` python
r'<attached:.*?-(PHOTO|AUDIO|STICKER|VIDEO|DOCUMENT)-.*?>'
```

**Tipos de mídia padronizados:** - `PHOTO` - `AUDIO` - `STICKER` - `VIDEO` - `DOCUMENT` - `CONTACT` (VCF) - `unknown`

### 1.4 Estrutura do DataFrame Final

**Colunas propostas:**

| Coluna | Tipo | Descrição | Valores possíveis |
|-----------------|-----------------|-----------------|---------------------|
| `timestamp` | datetime | Data e hora da mensagem | ISO 8601 format (timezone America/Sao_Paulo) |
| `sender` | string | Remetente | Nome do contato |
| `message` | string | Conteúdo completo da mensagem | Texto da mensagem (já com continuações agregadas) |
| `message_type` | string | Tipo da mensagem | `text`, `media`, `edited`, `deleted`, `empty` |
| `is_edited` | boolean | Mensagem foi editada? | `True`, `False` |
| `media_type` | string | Tipo de mídia (se aplicável) | `photo`, `video`, `audio`, `sticker`, `document`, `contact`, `null` |
| `media_source` | string | Origem da mídia | `attached`, `omitted`, `unknown`, `null` |
| `file_path` | string | Caminho do arquivo | Nome do arquivo ou `null` |
| `has_link` | boolean | Contém link? | `True`, `False` |
| `has_emoji` | boolean | Contém emoji? | `True`, `False` |
| `word_count` | integer | Contagem de palavras | Número |

::: callout-important
**Nota sobre continuações:** A coluna `is_continuation` não existe no DataFrame final porque as linhas de continuação são **agregadas à mensagem principal** durante o processamento da Parte 1. O campo `message` já contém o texto completo.
:::

------------------------------------------------------------------------

## 2. Pipeline de Processamento

### Parte 1: Quantificação de Mensagens Reais

**Objetivo:** Identificar quantas mensagens reais existem (considerando linhas de continuação).

**Etapas:**

1.  **Leitura do arquivo bruto**
    -   Ler `raw-data.txt` linha por linha
    -   Registrar número total de linhas
2.  **Identificação de mensagens**
    -   Identificar linhas que começam com timestamp `[DD/MM/YY, HH:MM:SS]`
    -   Marcar início de novas mensagens
3.  **Tratamento de continuações**
    -   Concatenar linhas sem timestamp à mensagem anterior
    -   Manter integridade do conteúdo
4.  **Tratamento de mensagens vazias**
    -   Identificar \~44 linhas vazias (agrupadores de attachments)
    -   Decisão: **Excluir** essas linhas (cada anexo subsequente será uma mensagem)
5.  **Contagem final**
    -   Contar número total de mensagens reais extraídas
6.  **Visualização**
    -   Gráfico funil: Linhas totais → Mensagens reais
    -   Mostrar redução percentual

**Output esperado:**

```         
Total de linhas: 90.000
Mensagens com timestamp: 45.000
Linhas de continuação: 44.500
Mensagens vazias: 44
Mensagens reais: 44.956 (linhas vazias excluídas)
```

------------------------------------------------------------------------

### Parte 2: Tipologia de Mensagens

**Objetivo:** Classificar e quantificar tipos de mensagens.

**Etapas:**

1.  **Análise do caractere invisível `[U+200E]`**
    -   Verificar se é indicador confiável de mensagens especiais
    -   Comparar com outras heurísticas de identificação
    -   Documentar limitações encontradas
2.  **Classificação por padrões**
    -   Extrair timestamp, remetente e conteúdo via regex
    -   Classificar mensagens:
        -   `text`: Mensagens de texto simples
        -   `media_attached`: Mídia com arquivo disponível
        -   `media_omitted`: Mídia sem arquivo
        -   `edited`: Mensagens editadas
        -   `deleted`: Mensagens deletadas
        -   `call`: Chamadas (voz/vídeo)
        -   `error`: Erros de exibição
        -   `empty`: Mensagens vazias
3.  **Contagem por tipo**
    -   Agregar mensagens por categoria
    -   Calcular percentuais
4.  **Visualização**
    -   Gráfico de barras: Distribuição dos tipos de mensagens
    -   Mostrar proporções relativas

**Regex críticas:**

``` python
# Timestamp e remetente
r'\[(\d{2}/\d{2}/\d{2}),\s(\d{2}:\d{2}:\d{2})\]\s([^:]+):\s?(.*)'

# Mídia omitida
r'(audio|image|video|sticker|GIF|document)\somitted'

# Mídia anexada
r'<attached:\s([^>]+)>'

# Mensagem editada
r'<This message was edited>'

# Mensagem deletada
r'This message was deleted'
```

------------------------------------------------------------------------

### Parte 3: Relacionamento com Arquivos Físicos

**Objetivo:** Cruzar attachments com arquivos reais na pasta de mídia.

**Contexto:** - Pasta de mídia: `~/Desktop/local-workbench/whats-le/_sources/WhatsappFiles` - Estrutura dos arquivos: `NNNNNNNN-TIPO-YYYY-MM-DD-HH-MM-SS.ext`

**Etapas:**

1.  **Extração de attachments**
    -   Identificar mensagens com padrão `<attached: filename>`
    -   Extrair nome completo do arquivo
2.  **Verificação de existência**
    -   Listar todos os arquivos na pasta de mídia
    -   Verificar correspondência direta por nome
3.  **Cruzamento por timestamp**
    -   Para mídias `omitted`, extrair data/hora da linha
    -   Buscar arquivos com mesma data/hora na pasta
    -   Tentar identificar se arquivo existe mas foi marcado incorretamente
4.  **Classificação de correspondências**
    -   `found`: Arquivo existe na pasta
    -   `not_found`: Arquivo não existe
    -   `ambiguous`: Múltiplos candidatos encontrados
5.  **Contagens e listas**
    -   Contar attachments com arquivos reais
    -   Contar attachments sem arquivos reais
    -   Listar arquivos órfãos (na pasta mas não referenciados)
6.  **Validação de hipótese**
    -   Confirmar se `omitted` realmente não tem arquivos
    -   Confirmar se `attached` sempre tem arquivos
    -   Documentar exceções encontradas
7.  **Visualizações**
    -   Gráfico de barras: Tipos de mídia por disponibilidade
    -   Gráfico de Venn: Arquivos referenciados vs. arquivos físicos

**Algoritmo de cruzamento:**

``` python
# Para cada mensagem de mídia omitted
if "omitted" in message:
    timestamp = extract_timestamp(line)
    media_type = extract_media_type(message)  # audio, image, etc.
    
    # Buscar na pasta por padrão
    pattern = f"*-{media_type.upper()}-{timestamp_to_filename(timestamp)}*"
    matches = find_files(media_folder, pattern)
    
    if matches:
        print(f"EXCEÇÃO: omitted encontrado - {matches}")
```

------------------------------------------------------------------------

### Parte 4: Arquivo Limpo (cleaned-data.txt)

**Objetivo:** Criar versão padronizada e reduzida do arquivo original.

#### 4.1 Padronização de Formato

**Transformações:**

1.  **Normalização de timestamps**
    -   De: `[DD/MM/YY, HH:MM:SS]`
    -   Para: `YYYY-MM-DDTHH:MM:SS-03:00` (ISO 8601 com timezone local)
2.  **Padronização de marcadores**
    -   Substituir variações de mídia por padrões consistentes:
        -   `audio omitted` → `[media-audio] omitted`
        -   `<attached: 00001-PHOTO-2025-08-21.jpg>` → `[media-image] 00001-PHOTO-2025-08-21.jpg`
    -   Substituir mensagens especiais:
        -   `<This message was edited>` → `[message-edited]`
        -   `This message was deleted` → `[message-deleted]`
        -   Chamadas → `[missed-voice-call]`, `[voice-call-answered]`
        -   Erros → `[display-error]`
3.  **Remoção de caracteres invisíveis**
    -   Remover todos os `[U+200E]` após extração das informações
4.  **Remoção de mensagens vazias**
    -   Excluir linhas vazias que precedem múltiplos attachments
    -   Manter apenas as linhas de attachments individuais

**Formato final esperado:**

```         
2023-05-12T14:23:45-03:00 Lê 🖤: Oi, tudo bem?
2023-05-12T14:25:10-03:00 Marlon: :))
2023-05-12T14:30:00-03:00 Lê 🖤: Olha que fofo esse cachorro! 🐶❤
2023-05-12T14:35:20-03:00 Marlon: 😂🤣😍
2023-05-12T15:00:00-03:00 Lê 🖤: [media-audio] omitted
2023-05-12T15:00:00-03:00 Marlon: [media-image] 00000001-PHOTO-2025-08-21-22-06-35.jpg
2023-05-12T15:00:00-03:00 Marlon: [message-edited] Sample Text....
2023-05-12T15:00:00-03:00 Marlon: [message-deleted]
2023-05-12T15:00:00-03:00 Lê 🖤: [missed-voice-call]
```

#### 4.2 Filtragem e Limpeza

**Ações:**

1.  ✅ Remover caracteres invisíveis `[U+200E]`
2.  ⚠️ Manter ou remover mensagens de sistema? (chamadas, erros)
    -   **Sugestão:** Manter com marcadores para análise posterior
3.  🔄 Padronizar nomes de remetentes (opcional)
    -   Opção: Anonimizar para `P1`, `P2`
    -   Decisão pendente: Manter nomes originais ou anonimizar?

#### 4.3 Análises Comparativas

**Métricas:**

1.  **Tamanho de arquivo**
    -   `raw-data.txt`: \~5MB
    -   `cleaned-data.txt`: ? MB
    -   Redução percentual
2.  **Contagem de linhas**
    -   `raw-data.txt`: \~90K linhas
    -   `cleaned-data.txt`: ? linhas
    -   Redução percentual
3.  **Contagem de caracteres**
    -   Total de caracteres removidos
    -   Impacto da remoção de `[U+200E]`

**Visualizações:** - Gráfico de barras comparativo: Tamanho e linhas (raw vs. cleaned) - Gráfico de pizza: Distribuição de tipos de mensagem (cleaned) - Gráfico de barras: Mensagens por remetente - Gráfico de linhas: Mensagens ao longo do tempo

------------------------------------------------------------------------

### Parte 5: DataFrame Inicial (initial_dataframe.csv)

**Objetivo:** Criar estrutura tabular com todas as informações extraídas.

**Colunas do DataFrame:**

| Coluna              | Tipo     | Descrição                            |
|---------------------|----------|--------------------------------------|
| `line_number`       | int      | Número da linha no arquivo original  |
| `raw_line`          | string   | Linha bruta sem alterações           |
| `cleaned_line`      | string   | Linha sem caracteres invisíveis      |
| `is_timestamp`      | bool     | Linha começa com timestamp?          |
| `is_continuation`   | bool     | É continuação de mensagem?           |
| `is_attachment`     | bool     | Indica attachment?                   |
| `is_media`          | bool     | É mensagem de mídia?                 |
| `is_edited`         | bool     | É mensagem editada?                  |
| `is_deleted`        | bool     | É mensagem deletada?                 |
| `is_system_message` | bool     | É mensagem de sistema?               |
| `is_empty`          | bool     | Linha vazia (múltiplos attachments)? |
| `timestamp`         | datetime | Timestamp extraído                   |
| `sender`            | string   | Remetente extraído                   |
| `message`           | string   | Conteúdo da mensagem                 |
| `message_type`      | string   | Tipo da mensagem                     |
| `media_type`        | string   | Tipo de mídia (se aplicável)         |
| `media_source`      | string   | `attached`, `omitted`, `unknown`     |
| `file_path`         | string   | Nome do arquivo (se aplicável)       |

**Etapas de criação:**

1.  Ler `raw-data.txt` linha por linha
2.  Para cada linha, extrair todas as informações possíveis
3.  Preencher colunas booleanas baseadas em padrões regex
4.  Salvar em `initial_dataframe.csv`

------------------------------------------------------------------------

### Parte 6: Redução Final para Análise Textual

**Objetivo:** Criar versão ultra-limpa focada apenas em análise de texto.

**Critérios de exclusão:**

-   ❌ Mensagens de sistema (chamadas, erros)
-   ❌ Mensagens deletadas
-   ❌ Anexos de mídia (manter apenas se houver legenda/texto)
-   ❌ Mensagens vazias

**Critérios de inclusão:**

-   ✅ Mensagens de texto puro
-   ✅ Mensagens com emojis
-   ✅ Mensagens com links
-   ✅ Mensagens editadas (manter texto final)

**Arquivo resultante:** `text_only_data.txt`

**Análises comparativas:** - Redução de linhas: `cleaned-data.txt` → `text_only_data.txt` - Redução de tamanho de arquivo - Visualização: Gráfico de barras mostrando redução progressiva

------------------------------------------------------------------------

### Parte 7: Enriquecimento e Análise Final

**Objetivo:** Adicionar features para análise exploratória.

#### 7.1 Features Adicionais

**Colunas computadas:**

| Feature         | Descrição                | Como calcular                  |
|-------------------|------------------------|------------------------------|
| `word_count`    | Número de palavras       | `len(message.split())`         |
| `char_count`    | Número de caracteres     | `len(message)`                 |
| `emoji_count`   | Número de emojis         | Biblioteca `emoji`             |
| `link_count`    | Número de links          | Regex para URLs                |
| `hour`          | Hora da mensagem         | `timestamp.hour`               |
| `day_of_week`   | Dia da semana            | `timestamp.strftime('%A')`     |
| `date`          | Data (sem hora)          | `timestamp.date()`             |
| `time_diff`     | Tempo desde msg anterior | Diferença entre timestamps     |
| `response_time` | Tempo de resposta        | Tempo até próxima msg do outro |

#### 7.2 Análises Estatísticas

**Resumo descritivo:** - Estatísticas por remetente (total de msgs, média de palavras, etc.) - Distribuição temporal (msgs por hora, dia, mês) - Padrões de comunicação (quem inicia conversas, tempos de resposta)

#### 7.3 Visualizações Propostas

**Análise Temporal:** 1. Gráfico de linha: Mensagens ao longo do tempo (timeline completo) 2. Heatmap: Mensagens por dia da semana × hora do dia 3. Gráfico de barras: Mensagens por mês/ano

**Análise de Conteúdo:** 1. WordCloud: Palavras mais frequentes (geral e por remetente) 2. Gráfico de barras: Top 20 palavras mais usadas 3. Gráfico de barras: Top emojis mais usados

**Análise de Padrões:** 1. Gráfico de barras: Distribuição de tipos de mensagem 2. Gráfico de barras: Distribuição de tipos de mídia 3. Gráfico de pizza: Proporção de mensagens por remetente

**Análise de Interação:** 1. Gráfico de linhas: Tempo médio de resposta ao longo do tempo 2. Scatter plot: Tamanho da mensagem × tempo de resposta 3. Gráfico de barras: Quem inicia mais conversas

**Análise de Sentimento (futuro):** 1. Gráfico de linha: Sentimento ao longo do tempo 2. Distribuição: Polaridade das mensagens 3. Comparativo: Sentimento por remetente

------------------------------------------------------------------------

## 3. Questões em Aberto / Decisões Pendentes

### ✅ Todas as decisões foram confirmadas!

**Hierarquia de Arquivos e Níveis de Limpeza:**

```         
┌─────────────────────────────────────────────────────────────┐
│                     raw-data.txt                            │
│  • Formato original do WhatsApp                             │
│  • ~90K linhas, ~5MB                                        │
│  • Contém: TUDO (caracteres invisíveis, linhas vazias, etc) │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
         ┌─────────────────────────────────────────┐
         │        PROCESSAMENTO                    │
         │  • Agregação de continuações           │
         │  • Extração de metadados                │
         │  • Classificação de tipos               │
         │  • Remoção de [U+200E]                  │
         └────────┬────────────────────────────────┘
                  │
                  ├──────────────────┐
                  ▼                  ▼
    ┌─────────────────────┐  ┌──────────────────────┐
    │  cleaned-data.txt   │  │ initial_dataframe.csv│
    │  • Timestamps ISO   │  │  • Todas as colunas  │
    │  • Com marcadores   │  │  • Flags booleanas   │
    │  • Sistema incluído │  │  • Análise completa  │
    │  • [message-edited] │  │  • is_edited = bool  │
    │  • [media-audio]    │  └──────────────────────┘
    │  • [missed-call]    │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ text_only_data.txt  │  (ULTRA-CLEAN)
    │  • Só texto puro    │
    │  • Sem marcadores   │
    │  • Sem sistema      │
    │  • Sem mídias       │
    │  • Sem deletadas    │
    │  • Análise textual  │
    └─────────────────────┘
```

### 3.1 Caractere Invisível

-   [x] **Remover no `cleaned-data.txt`** ✅
-   [x] **Usar como marcador durante processamento e remover no final** ✅
-   **Decisão final:** Usar durante processamento para identificar mensagens especiais, depois remover em todos os arquivos finais

### 3.2 Mensagens Editadas

-   [x] **Manter marcador `[message-edited]` no `cleaned-data.txt`** ✅
-   [x] **Remover marcador no `text_only_data.txt` (ultra-clean)** ✅
-   [x] **Preservar apenas versão editada (texto final)** ✅
-   **Decisão final:**
    -   `cleaned-data.txt`: Mantém marcador `[message-edited]` + texto final
    -   DataFrame: Coluna booleana `is_edited = True`
    -   `text_only_data.txt`: Remove marcador, mantém apenas o texto limpo
    -   **Não há como preservar o texto original** - o WhatsApp só indica que foi editada

::: callout-note
💡 O WhatsApp não exporta o conteúdo original das mensagens editadas, apenas marca com `<This message was edited>`. Preservamos apenas o texto final editado.
:::

### 3.3 Anonimização

-   [x] **Manter nomes originais por padrão** ✅
-   [x] **Implementar função de anonimização fácil (P1, P2)** ✅
-   **Decisão final:**
    -   Trabalhar com nomes reais durante desenvolvimento/testes
    -   Criar função simples para substituir nomes por `P1`, `P2` quando necessário
    -   Facilita validação visual durante desenvolvimento
    -   Permite anonimização rápida para compartilhamento público

**Sugestão de implementação:**

``` python
def anonymize_senders(df, mapping=None):
    """
    Anonimiza remetentes no DataFrame
    
    Args:
        df: DataFrame com coluna 'sender'
        mapping: dict opcional {'Nome Real': 'P1', ...}
                 Se None, cria automático
    """
    if mapping is None:
        unique_senders = df['sender'].unique()
        mapping = {name: f'P{i+1}' for i, name in enumerate(unique_senders)}
    
    df['sender_anonymized'] = df['sender'].map(mapping)
    return df, mapping
```

### 3.4 Fuso Horário

-   [x] **Manter timezone local (America/Sao_Paulo)** ✅
-   [x] **Usar offset explícito: `-03:00`** ✅
-   **Decisão final:** Manter timezone local com offset no formato ISO 8601

**Diferença UTC vs. Local:**

-   **UTC (Coordinated Universal Time):** Horário universal de referência, sem offset (ex: `2023-05-12T17:23:45Z`)

-   **Local com offset:** Horário local + diferença para UTC (ex: `2023-05-12T14:23:45-03:00`)

-   **Vantagem do local:** Preserva o contexto temporal real das conversas (ex: mensagem às 23h é noite, não 02h UTC)

**Formato adotado:** `YYYY-MM-DDTHH:MM:SS-03:00`

::: callout-tip
💡 O offset `-03:00` representa o fuso horário de Brasília (BRT/BRST). Isso facilita análises temporais contextualizadas (horário de pico, mensagens noturnas, etc).
:::

### 3.5 Mensagens de Sistema

-   [x] **Incluir no `cleaned-data.txt` com marcadores** (aqui já estarão padronizados) ✅
-   [x] **Excluir do `text_only_data.txt` (ultra-clean)** ✅
-   **Decisão final:** Progressão de limpeza em camadas

**Estrutura dos arquivos:**

| Arquivo | Mensagens de Sistema | Formato | Propósito |
|-----------------|---------------------|-----------------|-----------------|
| `raw-data.txt` | ✅ Incluídas (formato original) | Original WhatsApp | Fonte bruta |
| `cleaned-data.txt` | ✅ Incluídas com marcadores | `[missed-voice-call]` | Análise completa |
| `text_only_data.txt` | ❌ Excluídas | \- | Análise textual pura |

**Exemplos de mensagens de sistema:** - Chamadas: `[missed-voice-call]`, `[voice-call-answered]` - Erros: `[display-error]` - Mensagens deletadas: `[message-deleted]`

**Lógica:** O `cleaned-data.txt` é a versão intermediária que mantém **todos** os tipos de mensagem com marcadores padronizados, permitindo análises abrangentes. O `text_only_data.txt` é a versão final ultra-limpa focada exclusivamente em conteúdo textual, mantendo timestamp, rementente e a mensagem o conteúdo da mensagem.

------------------------------------------------------------------------

## 4. Resumo do Fluxo Completo

```         
┌─────────────────┐
│  raw-data.txt   │ (~90K linhas, ~5MB)
└────────┬────────┘
         │
         ├─► PARTE 1: Quantificação de mensagens reais
         │   └─► Output: Estatísticas + Gráfico funil
         │
         ├─► PARTE 2: Tipologia de mensagens
         │   └─► Output: Classificação + Gráfico de barras
         │
         ├─► PARTE 3: Relacionamento com arquivos
         │   └─► Output: Validação de hipótese + Gráficos
         │
         ├─► PARTE 4: Arquivo limpo
         │   └─► Output: cleaned-data.txt
         │              └─► Comparações + Visualizações
         │
         ├─► PARTE 5: DataFrame inicial
         │   └─► Output: initial_dataframe.csv
         │
         ├─► PARTE 6: Redução textual
         │   └─► Output: text_only_data.txt
         │              └─► Comparações + Visualizações
         │
         └─► PARTE 7: Enriquecimento e análise
             └─► Output: DataFrame final + Visualizações exploratórias
                        └─► WordClouds, heatmaps, sentiment, etc.
```

------------------------------------------------------------------------

## 5. Próximos Passos

1.  [ ] Revisar e validar decisões conceituais (Seção 1)
2.  [ ] Definir respostas para questões em aberto (Seção 3)
3.  [ ] Implementar Parte 1 do pipeline
4.  [ ] Implementar Partes 2-7 sequencialmente
5.  [ ] Documentar achados e exceções em cada etapa
6.  [ ] Gerar visualizações finais
7.  [ ] Escrever relatório final no QMD