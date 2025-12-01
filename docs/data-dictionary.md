# Dicionário de Dados

Documentação completa das variáveis do dataset enriquecido.

------------------------------------------------------------------------

## Visão Geral

O dataset `messages_enriched.parquet` contém **43 colunas** organizadas em 5 categorias:

1.  **Colunas Originais** (8) - Dados base do WhatsApp
2.  **Features Temporais** (9) - Variáveis derivadas de timestamp
3.  **Features de Texto** (9) - Características do conteúdo
4.  **Features de Conversação** (7) - Dinâmica da interação
5.  **Features de Contexto Externo** (10) - Dados de encontros presenciais

**Total:** 43 colunas \| \~95.000 mensagens \| 14 meses de conversas

O dataset opcional `messages_with_models.parquet` adiciona **5+ colunas** de features baseadas em ML:

6.  **Features de Modelos** (5 implementadas + futuras) - Análise de sentimento, embeddings, tópicos

------------------------------------------------------------------------

## 1. Colunas Originais

Dados base extraídos e processados do export do WhatsApp.

| Coluna | Tipo | Descrição |
|-----------------------|------------------|-------------------------------|
| `timestamp` | datetime | Data e hora da mensagem |
| `remetente` | category | Participante (P1 ou P2) |
| `tipo_mensagem` | category | Tipo específico (text_pure, audio_omitted, video_attached, etc.) |
| `grupo_mensagem` | category | Categoria agrupada (TEXT, AUDIO, VID, IMG, STICKER, GIF, DOC, CONTACT, FILE, SYSTEM, CALL) |
| `conteudo` | text | Conteúdo enriquecido (transcrição ou texto original) |
| `arquivo` | text | Nome do arquivo de mídia anexado (se aplicável) |
| `transcricao` | bool | Indica se possui transcrição de áudio/vídeo |
| `date_match` | bool | Indica se é mensagem órfã/sintética |

------------------------------------------------------------------------

## 2. Features Temporais

Variáveis derivadas do timestamp para análise de padrões temporais.

| Feature | Tipo | Descrição | Exemplo |
|-----------------|-----------------|---------------------|-----------------|
| `ano` | int | Ano extraído do timestamp | 2024 |
| `trimestre` | category | Trimestre do ano (Q1-Q4) | Q3 |
| `mes` | int | Mês numérico (1-12) | 10 |
| `data` | date | Data sem hora (YYYY-MM-DD) | 2024-10-15 |
| `dia_semana` | category (ordered) | Dia da semana (Segunda-Domingo) | Sexta |
| `fim_de_semana` | bool | True se Sábado ou Domingo | False |
| `hora` | int | Hora do dia (0-23) | 14 |
| `periodo_dia` | category (ordered) | Madrugada (00-05h), Manhã (06-11h), Tarde (12-17h), Noite (18-23h) | Tarde |
| `horario_comercial` | bool | True se Seg-Sex entre 08:00-18:00 | True |

------------------------------------------------------------------------

## 3. Features de Texto

Características do conteúdo textual das mensagens.

| Feature              | Tipo | Descrição                               | Exemplo |
|-----------------|-----------------|---------------------|-----------------|
| `tamanho_caracteres` | int  | Quantidade de caracteres no conteúdo    | 157     |
| `tamanho_palavras`   | int  | Quantidade de palavras                  | 24      |
| `tem_emoji`          | bool | True se contém emoji                    | True    |
| `qtd_emojis`         | int  | Quantidade de emojis                    | 3       |
| `tem_link`           | bool | True se contém URL (http/https)         | False   |
| `tem_mencao`         | bool | True se contém menção (@usuario)        | False   |
| `tem_interrogacao`   | bool | True se termina com ?                   | True    |
| `tem_exclamacao`     | bool | True se termina com !                   | False   |
| `eh_caixa_alta`      | bool | True se \>70% das letras são maiúsculas | False   |

------------------------------------------------------------------------

## 4. Features de Conversação

Dinâmica e fluxo da interação entre participantes.

| Feature | Tipo | Descrição | Exemplo |
|-----------------|-----------------|---------------------|-----------------|
| `tempo_desde_ultima_msg` | float | Segundos desde mensagem anterior (qualquer remetente) | 127.5 |
| `tempo_desde_ultima_msg_mesmo_remetente` | float | Segundos desde última do mesmo remetente | 450.0 |
| `eh_inicio_conversa` | bool | True se gap \> 1 hora (3600 segundos) | False |
| `eh_resposta_rapida` | bool | True se respondeu em \< 60 segundos | True |
| `sequencia_mesmo_remetente` | int | Contador de mensagens consecutivas do mesmo remetente | 3 |
| `turno_conversa` | int | ID do bloco de conversa (incrementa a cada início) | 42 |
| `tempo_resposta_outro_remetente` | float | Segundos até próxima mensagem do outro remetente | 345.2 |

------------------------------------------------------------------------

## 5. Features de Contexto Externo

Informações de encontros presenciais agregadas de fonte externa.

| Feature | Tipo | Descrição | Exemplo |
|-----------------|-----------------|---------------------|-----------------|
| `em_encontro` | bool | True se durante encontro presencial | True |
| `encontro_id` | int | ID do encontro (1-10) ou None | 3 |
| `encontro_nome` | str | Nome descritivo do encontro | BSB (Carnaval) |
| `local_encontro` | str | Cidade/local do encontro | Brasília |
| `tipo_encontro` | str | Quem visitou quem | Marlon \@ BSB |
| `dias_desde_ultimo_encontro` | int | Dias desde término do último encontro | 15 |
| `dias_ate_proximo_encontro` | int | Dias até início do próximo encontro | 23 |
| `dia_do_encontro` | int | Dia dentro do encontro (1, 2, 3...) | 5 |
| `eh_marco_especial` | bool | True se data de marco especial | True |
| `marco_nome` | str | Descrição do marco especial | 1ª Vez Juntos |

------------------------------------------------------------------------

## 6. Features de Modelos (Opcional)

Features derivadas de modelos de Machine Learning. Disponíveis em `messages_with_models.parquet`.

### Análise de Sentimento (BERT)

| Feature | Tipo | Descrição | Exemplo |
|-----------------|-----------------|---------------------|-----------------|
| `sentimento_label` | category | Classificação do sentimento (positivo, neutro, negativo) | positivo |
| `sentimento_score` | float | Score de confiança (-1 a 1) | 0.87 |
| `sentimento_positivo` | float | Probabilidade de ser positivo (0-1) | 0.92 |
| `sentimento_neutro` | float | Probabilidade de ser neutro (0-1) | 0.05 |
| `sentimento_negativo` | float | Probabilidade de ser negativo (0-1) | 0.03 |

### Embeddings (Planejado)

| Feature             | Tipo  | Descrição                       | Status       |
|---------------------|-------|---------------------------------|--------------|
| `embedding_vector`  | array | Vetor semântico (384 dimensões) | ⏸️ Planejado |
| `embedding_cluster` | int   | Cluster semântico após K-means  | ⏸️ Planejado |

### Topic Modeling (Planejado)

| Feature             | Tipo  | Descrição                         | Status       |
|------------------|-----------------|----------------------|-----------------|
| `topic_id`          | int   | ID do tópico identificado         | ⏸️ Planejado |
| `topic_name`        | str   | Nome/descrição do tópico          | ⏸️ Planejado |
| `topic_probability` | float | Confiança na atribuição do tópico | ⏸️ Planejado |

### Named Entity Recognition (Planejado)

| Feature           | Tipo | Descrição                    | Status       |
|-------------------|------|------------------------------|--------------|
| `tem_pessoa`      | bool | True se menciona pessoa      | ⏸️ Planejado |
| `tem_lugar`       | bool | True se menciona lugar       | ⏸️ Planejado |
| `tem_organizacao` | bool | True se menciona organização | ⏸️ Planejado |

------------------------------------------------------------------------

## Tipos de Mensagem (`tipo_mensagem`)

| Categoria         | Valores            | Descrição                   |
|-------------------|--------------------|-----------------------------|
| **Texto**         | `text_pure`        | Texto sem emoji nem link    |
|                   | `text_with_emoji`  | Texto com emoji             |
|                   | `text_with_link`   | Texto com URL               |
| **Mídia Omitida** | `audio_omitted`    | Áudio não anexado no export |
|                   | `image_omitted`    | Imagem não anexada          |
|                   | `video_omitted`    | Vídeo não anexado           |
|                   | `sticker_omitted`  | Sticker não anexado         |
|                   | `gif_omitted`      | GIF não anexado             |
|                   | `document_omitted` | Documento não anexado       |
| **Mídia Anexada** | `audio_attached`   | Áudio presente no export    |
|                   | `image_attached`   | Imagem presente             |
|                   | `video_attached`   | Vídeo presente              |
|                   | `sticker_attached` | Sticker presente            |
|                   | `contact_attached` | Contato compartilhado       |
| **Sistema**       | `message_deleted`  | Mensagem apagada            |
|                   | `message_edited`   | Mensagem editada            |
|                   | `voice_call`       | Chamada de voz              |
|                   | `missed_call`      | Chamada perdida             |
|                   | `system_message`   | Mensagem do sistema         |

------------------------------------------------------------------------

## Grupos de Mensagem (`grupo_mensagem`)

| Grupo     | Descrição                              |
|-----------|----------------------------------------|
| `TEXT`    | Mensagens de texto (puro, emoji, link) |
| `AUDIO`   | Áudios (omitidos ou anexados)          |
| `VID`     | Vídeos (omitidos ou anexados)          |
| `IMG`     | Imagens (omitidas ou anexadas)         |
| `STICKER` | Stickers                               |
| `GIF`     | GIFs                                   |
| `DOC`     | Documentos                             |
| `CONTACT` | Contatos compartilhados                |
| `FILE`    | Arquivos genéricos                     |
| `SYSTEM`  | Mensagens do sistema                   |
| `CALL`    | Chamadas de voz/vídeo                  |

------------------------------------------------------------------------

## Estatísticas do Dataset

-   **Total de mensagens:** \~95.000
-   **Período:** 14 meses
-   **Participantes:** 2 (P1 e P2)
-   **Encontros presenciais:** 10 viagens
-   **Features criadas:** 35 (além das 8 originais)
-   **Features de modelos:** 5 implementadas + 8 planejadas
-   **Arquivos:**
    -   `data/processed/messages_enriched.parquet` (43 colunas)
    -   `data/processed/messages_with_models.parquet` (48+ colunas, opcional)

------------------------------------------------------------------------

## Notas de Implementação

### Thresholds Configurados

| Parâmetro          | Valor       | Descrição                             |
|--------------------|-------------|---------------------------------------|
| Início de conversa | 3600 seg    | Gap \> 1 hora define novo turno       |
| Resposta rápida    | 60 seg      | Mensagem enviada em \< 1 minuto       |
| Caixa alta         | 70%         | Proporção mínima de letras maiúsculas |
| Horário comercial  | 08:00-18:00 | Segunda a Sexta                       |

### Fonte de Dados Externos

-   `data/external/encontros.csv` - Metadados de encontros presenciais com colunas:
    -   `encontro_id`, `nome`, `local`, `tipo_encontro`
    -   `inicio`, `fim` (datas do período junto)
    -   `marco_especial`, `marco_nome` (data e descrição de marco)

### Processamento

Todas as features estruturais foram criadas em `03-feature-engineering.qmd` usando: - Pandas para manipulação de dados - Operações vetorizadas para performance - `pd.merge_asof` para cálculo eficiente de tempo de resposta

### Features de Modelos

Features de ML são criadas em `04-model-features.qmd` usando: - BERT pré-treinado em português para análise de sentimento - Script: `scripts/sentiment_analysis.py` - Modelo: `neuralmind/bert-base-portuguese-cased` (ou similar) - **Nota:** Execução opcional, computacionalmente custosa

------------------------------------------------------------------------

## Arquivos de Corpus

Arquivos TXT para análises de NLP.

| Arquivo             | Descrição                                 |
|---------------------|-------------------------------------------|
| `chat_complete.txt` | Todas mensagens com timestamp e remetente |
| `chat_p1.txt`       | Só mensagens de P1                        |
| `chat_p2.txt`       | Só mensagens de P2                        |
| `corpus_full.txt`   | Só conteúdo (sem metadados)               |
| `corpus_p1.txt`     | Só conteúdo de P1                         |
| `corpus_p2.txt`     | Só conteúdo de P2                         |

------------------------------------------------------------------------

*Última atualização: Dezembro 2025*