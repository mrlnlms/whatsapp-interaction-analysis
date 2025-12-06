# Feature Engineering

Criação de variáveis derivadas

## Configuração

| Entrada | `messages.parquet` | ~/whatsapp-ds-analytics/data/processed/export\_2024-10\_2025-10 |
| --- | --- | --- |
| Saída | `messages_enriched.parquet` | ~/whatsapp-ds-analytics/data/processed/export\_2024-10\_2025-10 |

---

## Introdução

Este notebook cria **variáveis derivadas** a partir do dataset base gerado pelo wrangling.

O objetivo é enriquecer os dados com features que permitam análises mais profundas sobre padrões de comunicação.

---

## Carregamento dos Dados

| Mensagens | 91,924 |
| --- | --- |
| Colunas | 8 |
| Período | 19/10/2024 → 20/10/2025 |

| `timestamp` | datetime | Data e hora da mensagem |
| --- | --- | --- |
| `remetente` | category | Participante (P1 ou P2) |
| `tipo_mensagem` | category | Tipo específico - 21 possíveis (text\_pure, audio\_omitted, video\_attached, etc.) |
| `grupo_mensagem` | category | Categoria agrupada: TEXT, AUDIO, VID, IMG, STICKER, GIF, DOC, CONTACT, FILE, SYSTEM, CALL |
| `conteudo` | text | Conteúdo enriquecido: transcrição (se mídia transcrita) ou texto original |
| `arquivo` | text | Nome do arquivo de mídia anexado (ex: 00001-AUDIO-2024-10-21.opus), se aplicável |
| `transcricao` | bool | Indica se a mensagem possui transcrição de áudio/vídeo |
| `date_match` | bool | Indica se é mensagem órfã/sintética (transcrição sem match de timestamp) |

| 0 | 2024-10-19 13:52:51 | P1 | text\_pure | TEXT | Le? | None | False | False |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2024-10-19 13:53:25 | P2 | text\_with\_link | TEXT | https://www.localiza.com/brasil/pt-br/reservas... | None | False | False |
| 2 | 2024-10-19 13:53:25 | P1 | image\_omitted | IMG | None | None | False | False |
| 3 | 2024-10-19 13:53:41 | P2 | sticker\_omitted | STICKER | None | None | False | False |
| 4 | 2024-10-19 13:53:43 | P2 | text\_pure | TEXT | Oi | None | False | False |

---

## Features Temporais

Variáveis derivadas do timestamp.

| `ano` | int | Ano extraído do timestamp | 2024 | Comparar períodos anuais, evolução de longo prazo |
| --- | --- | --- | --- | --- |
| `trimestre` | category | Trimestre do ano (Q1, Q2, Q3, Q4) | Q3 | Análise de tendências em blocos trimestrais |
| `mes` | int | Mês numérico (1=Jan, 12=Dez) | 10 | Sazonalidade mensal, comparações entre meses |
| `data` | date | Data sem componente de hora (YYYY-MM-DD) | 2024-10-15 | Agregações diárias, contar mensagens por dia |
| `dia_semana` | category (ordered) | Dia da semana textual (Segunda...Domingo) | Sexta | Padrões por dia da semana, comparações |
| `fim_de_semana` | bool | True se Sábado ou Domingo | False | Comparar comportamento weekday vs weekend |
| `hora` | int | Hora do dia (0-23) | 14 | Identificar horários de pico, padrões de atividade |
| `periodo_dia` | category (ordered) | Madrugada (00-05h), Manhã (06-11h), Tarde (12-17h), Noite (18-23h) | Tarde | Análise de padrões por turno do dia |
| `horario_comercial` | bool | True se Seg-Sex entre 08:00-18:00 | True | Diferenciar msgs em horário de trabalho vs lazer |

**Ano**

```python
# Extrai ano
df['ano'] = df['timestamp'].dt.year
```

**Trimestre**

```python
# Extrai trimestre (Q1, Q2, Q3, Q4)
df['trimestre'] = 'Q' + df['timestamp'].dt.quarter.astype(str)
df['trimestre'] = df['trimestre'].astype('category')
```

**Mês**

```python
# Extrai mês (1-12)
df['mes'] = df['timestamp'].dt.month
```

**Data (sem hora)**

```python
# Extrai data sem componente de hora
df['data'] = df['timestamp'].dt.date
```

**Dia da Semana**

```python
# Extrai dia da semana textual (Segunda-Domingo)
dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
df['dia_semana'] = pd.Categorical(
    df['timestamp'].dt.day_name(locale='pt_BR.UTF-8'),
    categories=dias_semana,
    ordered=True
)
```

**Fim de Semana**

```python
# Identifica se é final de semana (Sábado ou Domingo)
df['fim_de_semana'] = df['timestamp'].dt.dayofweek >= 5
```

**Hora**

```python
# Extrai hora do dia (0-23)
df['hora'] = df['timestamp'].dt.hour
```

**Período do Dia**

```python
# Define período do dia baseado na hora
def classificar_periodo(hora):
    if 0 <= hora <= 5:
        return 'Madrugada'
    elif 6 <= hora <= 11:
        return 'Manhã'
    elif 12 <= hora <= 17:
        return 'Tarde'
    else:
        return 'Noite'

df['periodo_dia'] = df['hora'].apply(classificar_periodo)
df['periodo_dia'] = pd.Categorical(
    df['periodo_dia'],
    categories=['Madrugada', 'Manhã', 'Tarde', 'Noite'],
    ordered=True
)
```

**Horário Comercial**

```python
# Identifica se mensagem foi enviada em horário comercial
# Seg-Sex, 08:00-18:00
eh_dia_util = df['timestamp'].dt.dayofweek < 5  # 0=Segunda, 4=Sexta
eh_horario_comercial = (df['hora'] >= 8) & (df['hora'] < 18)
df['horario_comercial'] = eh_dia_util & eh_horario_comercial
```

## Validação

| 0 | 2024-10-19 13:52:51 | 2024 | Q4 | 10 | 2024-10-19 | Sábado | True | 13 | Tarde | False |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2024-10-19 13:53:25 | 2024 | Q4 | 10 | 2024-10-19 | Sábado | True | 13 | Tarde | False |
| 2 | 2024-10-19 13:53:25 | 2024 | Q4 | 10 | 2024-10-19 | Sábado | True | 13 | Tarde | False |
| 3 | 2024-10-19 13:53:41 | 2024 | Q4 | 10 | 2024-10-19 | Sábado | True | 13 | Tarde | False |
| 4 | 2024-10-19 13:53:43 | 2024 | Q4 | 10 | 2024-10-19 | Sábado | True | 13 | Tarde | False |

---

## Features de Texto

Variáveis derivadas do conteúdo da mensagem.

| `tamanho_caracteres` | int | Quantidade de caracteres no conteúdo | 157 | Identificar mensagens curtas vs longas, padrões de verbosidade |
| --- | --- | --- | --- | --- |
| `tamanho_palavras` | int | Quantidade de palavras (separadas por espaço) | 24 | Complexidade da mensagem, densidade de informação |
| `tem_emoji` | bool | True se a mensagem contém pelo menos um emoji | True | Identificar uso de expressões visuais, tom emocional |
| `qtd_emojis` | int | Quantidade total de emojis na mensagem | 3 | Intensidade do uso de emojis, padrões expressivos |
| `tem_link` | bool | True se contém URL (http:// ou https://) | False | Identificar compartilhamento de links, conteúdo externo |
| `tem_mencao` | bool | True se contém @ (menção/referência) | False | Detectar menções a outras pessoas ou serviços |
| `tem_interrogacao` | bool | True se a mensagem termina com? | True | Identificar perguntas, busca por informação |
| `tem_exclamacao` | bool | True se a mensagem termina com! | False | Detectar ênfase, entusiasmo ou urgência |
| `eh_caixa_alta` | bool | True se >70% das letras são maiúsculas (mínimo 3 letras) | False | Identificar mensagens enfáticas ou "gritadas" |

**Tamanho em Caracteres**

```python
# Conta caracteres no conteúdo
df['tamanho_caracteres'] = df['conteudo'].fillna('').str.len()
```

**Tamanho em Palavras**

```python
# Conta palavras (split por espaço)
df['tamanho_palavras'] = df['conteudo'].fillna('').str.split().str.len().fillna(0).astype(int)
```

**Detecção de Emoji**

```python
import re

# Padrão regex para detectar emojis (ranges Unicode comuns)
emoji_pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # símbolos e pictogramas
    "\U0001F680-\U0001F6FF"  # transporte e mapas
    "\U0001F1E0-\U0001F1FF"  # bandeiras
    "\U00002600-\U000027BF"  # símbolos diversos
    "\U0001F900-\U0001F9FF"  # símbolos suplementares
    "\U0001FA00-\U0001FA6F"  # símbolos estendidos
    "]+", 
    flags=re.UNICODE
)

# Detecta presença de emoji
df['tem_emoji'] = df['conteudo'].fillna('').apply(lambda x: bool(emoji_pattern.search(x)))

# Conta quantidade de emojis
df['qtd_emojis'] = df['conteudo'].fillna('').apply(lambda x: len(emoji_pattern.findall(x)))
```

**Detecção de Link**

```python
# Detecta URLs (http:// ou https://)
df['tem_link'] = df['conteudo'].fillna('').str.contains(r'https?://', case=False, regex=True)
```

**Detecção de Menção**

```python
# Detecta @ (menções)
df['tem_mencao'] = df['conteudo'].fillna('').str.contains(r'(?:^|\s)@\w+', regex=True)
```

**Detecção de Interrogação**

```python
# Detecta se termina com ?
df['tem_interrogacao'] = df['conteudo'].fillna('').str.strip().str.endswith('?')
```

**Detecção de Exclamação**

```python
# Detecta se termina com !
df['tem_exclamacao'] = df['conteudo'].fillna('').str.strip().str.endswith('!')
```

**Detecção de Caixa Alta**

```python
# Detecta mensagens em caixa alta (>70% maiúsculas, mínimo 3 letras)
def eh_caixa_alta(texto):
    if pd.isna(texto) or texto == '':
        return False
    
    # Extrai apenas letras
    letras = [c for c in texto if c.isalpha()]
    
    # Precisa ter no mínimo 3 letras
    if len(letras) < 3:
        return False
    
    # Calcula proporção de maiúsculas
    maiusculas = sum(1 for c in letras if c.isupper())
    proporcao = maiusculas / len(letras)
    
    return proporcao > 0.7

df['eh_caixa_alta'] = df['conteudo'].apply(eh_caixa_alta)
```

### Validação

| `tem_emoji` | 4910 | 👍🏻 |
| --- | --- | --- |
| `tem_link` | 555 | https://www.localiza.com/brasil/pt-br/reservas/passo-2 |
| `tem_mencao` | 3 | @L371c1@ |
| `tem_interrogacao` | 4883 | Le? |
| `tem_exclamacao` | 2277 | O jeep é show! |
| `eh_caixa_alta` | 2209 | HAHAHAH |

---

## Features de Conversação

Variáveis sobre o fluxo da conversa.

| `tempo_desde_ultima_msg` | float | Tempo em segundos desde a mensagem anterior (qualquer remetente) | 127.5 | Identificar ritmo da conversa, pausas, engajamento |
| --- | --- | --- | --- | --- |
| `tempo_desde_ultima_msg_mesmo_remetente` | float | Tempo em segundos desde a última mensagem do MESMO remetente | 450.0 | Analisar padrão individual, frequência de envio por pessoa |
| `eh_inicio_conversa` | bool | True se gap desde última msg > 1 hora (3600 segundos) | False | Delimitar sessões de conversa, identificar retomadas |
| `eh_resposta_rapida` | bool | True se respondeu em < 60 segundos | True | Identificar engajamento imediato, urgência, flow da conversa |
| `sequencia_mesmo_remetente` | int | Contador de mensagens consecutivas do mesmo remetente | 3 | Identificar monólogos, rajadas de mensagens, padrão de interação |
| `turno_conversa` | int | ID incremental do bloco de conversa (reseta quando eh\_inicio\_conversa) | 42 | Agrupar mensagens de uma mesma sessão, análises por conversa |
| `tempo_resposta_outro_remetente` | float | Tempo em segundos até a próxima mensagem do OUTRO remetente | 345.2 | Medir velocidade de resposta, disponibilidade, reciprocidade |

**Tempo Desde Última Mensagem (Qualquer Remetente)**

```python
# Garante ordenação por timestamp
df = df.sort_values('timestamp').reset_index(drop=True)

# Calcula tempo desde a mensagem anterior (qualquer remetente)
df['tempo_desde_ultima_msg'] = df['timestamp'].diff().dt.total_seconds()
```

**Tempo Desde Última Mensagem (Mesmo Remetente)**

```python
# Calcula tempo desde a última mensagem do mesmo remetente
df['tempo_desde_ultima_msg_mesmo_remetente'] = df.groupby('remetente')['timestamp'].diff().dt.total_seconds()
```

**Início de Conversa**

```python
# Define threshold de início de conversa (1 hora)
THRESHOLD_INICIO_CONVERSA = 3600  # 1 hora em segundos

# Marca início de conversa (gap > 1 hora OU primeira mensagem)
df['eh_inicio_conversa'] = (df['tempo_desde_ultima_msg'] > THRESHOLD_INICIO_CONVERSA) | (df['tempo_desde_ultima_msg'].isna())
```

**Resposta Rápida**

```python
# Define threshold de resposta rápida (60 segundos)
THRESHOLD_RESPOSTA_RAPIDA = 60

# Marca mensagens enviadas rapidamente (< 60 segundos)
df['eh_resposta_rapida'] = df['tempo_desde_ultima_msg'] < THRESHOLD_RESPOSTA_RAPIDA
```

**Sequência Mesmo Remetente**

```python
# Conta quantas mensagens consecutivas do mesmo remetente
# Reinicia contagem quando muda de remetente
df['sequencia_mesmo_remetente'] = df.groupby((df['remetente'] != df['remetente'].shift()).cumsum()).cumcount() + 1
```

**Turno de Conversa**

```python
# Cria ID de turno de conversa (incrementa a cada início)
df['turno_conversa'] = df['eh_inicio_conversa'].cumsum()
```

**Tempo Resposta do Outro Remetente**

```python
# Versão vetorizada usando merge_asof (MUITO mais rápida)
def calcular_tempo_resposta_outro_vetorizado(df):
    """
    Usa merge_asof para encontrar próxima mensagem do outro remetente.
    Performance: ~10-100x mais rápido que loops.
    """
    resultado = pd.Series(index=df.index, dtype='float64')
    
    remetentes = df['remetente'].unique()
    
    for rem_atual in remetentes:
        # Mensagens deste remetente
        msgs_atual = df[df['remetente'] == rem_atual][['timestamp']].copy()
        msgs_atual = msgs_atual.reset_index()
        
        # Mensagens do outro remetente
        msgs_outro = df[df['remetente'] != rem_atual][['timestamp']].copy()
        msgs_outro['timestamp_outro'] = msgs_outro['timestamp']
        msgs_outro = msgs_outro[['timestamp_outro']].reset_index(drop=True)
        
        # Merge asof: para cada msg atual, encontra próxima do outro
        merged = pd.merge_asof(
            msgs_atual.sort_values('timestamp'),
            msgs_outro.sort_values('timestamp_outro'),
            left_on='timestamp',
            right_on='timestamp_outro',
            direction='forward'  # Próxima no futuro
        )
        
        # Calcula diferença de tempo
        merged['tempo_resposta'] = (
            merged['timestamp_outro'] - merged['timestamp']
        ).dt.total_seconds()
        
        # Atribui ao índice original
        resultado.loc[merged['index']] = merged['tempo_resposta'].values
    
    return resultado

df['tempo_resposta_outro_remetente'] = calcular_tempo_resposta_outro_vetorizado(df)
```

### Validação

| `tempo_desde_ultima_msg` | 91923 | 8.0 |
| --- | --- | --- |
| `tempo_desde_ultima_msg_mesmo_remetente` | 91922 | 11.0 |
| `eh_inicio_conversa` | 1206 | 1206 inícios detectados |
| `eh_resposta_rapida` | 74390 | 74390 respostas rápidas |
| `sequencia_mesmo_remetente` | 91924 | Máx: 54 |
| `turno_conversa` | 91924 | 1206 turnos totais |
| `tempo_resposta_outro_remetente` | 91920 | 80.0 |

---

## Features de Contexto Externo

Informações agregadas de fontes externas ao dataset de mensagens.

## Encontros Presenciais

Dados sobre períodos em que estavam juntos fisicamente, enriquecendo a análise com contexto do relacionamento.

| `em_encontro` | bool | True se mensagem enviada durante encontro presencial | True | Comparar padrões de comunicação junto vs separado |
| --- | --- | --- | --- | --- |
| `encontro_id` | int | ID do encontro (1-10) ou None se separados | 3 | Identificar período/viagem específica |
| `encontro_nome` | str | Nome descritivo do encontro | BSB (Carnaval) | Contexto narrativo do período |
| `local_encontro` | str | Cidade/local do encontro | Brasília | Análise por localização |
| `tipo_encontro` | str | Quem visitou quem (Marlon @ BSB ou Letícia @ SP) | Marlon @ BSB | Padrão de deslocamento |
| `dias_desde_ultimo_encontro` | int | Dias desde término do último encontro (None durante encontro) | 15 | Medir período de separação, saudade |
| `dias_ate_proximo_encontro` | int | Dias até início do próximo encontro (None durante encontro) | 23 | Medir expectativa, ansiedade pré-encontro |
| `dia_do_encontro` | int | Qual dia dentro do encontro (1, 2, 3...) ou None | 5 | Padrões dentro do período junto (início vs fim) |
| `eh_marco_especial` | bool | True se é data de marco especial | True | Identificar datas significativas |
| `marco_nome` | str | Descrição do marco especial | 💕 1ª Vez Juntos | Contexto emocional da data |

**Carregamento dos Dados**

#### Features Básicas de Encontro

**Em Encontro**

```python
# Identifica se mensagem foi enviada durante encontro
df['em_encontro'] = False
df['encontro_id'] = None
df['encontro_nome'] = None
df['local_encontro'] = None
df['tipo_encontro'] = None

for _, encontro in encontros.iterrows():
    mask = (df['data_msg'] >= encontro['inicio'].date()) & (df['data_msg'] <= encontro['fim'].date())
    df.loc[mask, 'em_encontro'] = True
    df.loc[mask, 'encontro_id'] = encontro['encontro_id']
    df.loc[mask, 'encontro_nome'] = encontro['nome']
    df.loc[mask, 'local_encontro'] = encontro['local']
    df.loc[mask, 'tipo_encontro'] = encontro['tipo_encontro']
```

**Dia do Encontro**

```python
# Calcula qual dia do encontro (1, 2, 3...)
df['dia_do_encontro'] = None

for _, encontro in encontros.iterrows():
    mask = (df['data_msg'] >= encontro['inicio'].date()) & (df['data_msg'] <= encontro['fim'].date())
    df.loc[mask, 'dia_do_encontro'] = (
        pd.to_datetime(df.loc[mask, 'data_msg']) - encontro['inicio']
    ).dt.days + 1
```

#### Features de Marcos Especiais

**Marco Especial**

```python
# Identifica mensagens em datas de marcos especiais
df['eh_marco_especial'] = False
df['marco_nome'] = None

for _, encontro in encontros.iterrows():
    if pd.notna(encontro['marco_especial']):  # ✨ AJUSTADO
        mask = df['data_msg'] == encontro['marco_especial'].date()  # ✨ AJUSTADO
        df.loc[mask, 'eh_marco_especial'] = True
        df.loc[mask, 'marco_nome'] = encontro['marco_nome']  # ✨ Já estava certo
```

#### Features de Distância Temporal

**Dias Desde Último Encontro**

```python
# Calcula dias desde término do último encontro
df['dias_desde_ultimo_encontro'] = None

# Ordena encontros por data
encontros_ord = encontros.sort_values('inicio')

for idx, encontro in encontros_ord.iterrows():
    # Período APÓS este encontro até o próximo (ou fim do dataset)
    fim_encontro = encontro['fim'].date()
    
    # Encontra próximo encontro
    proximos = encontros_ord[encontros_ord['inicio'] > encontro['fim']]
    if len(proximos) > 0:
        inicio_proximo = proximos.iloc[0]['inicio'].date()
    else:
        inicio_proximo = df['data_msg'].max()
    
    # Mensagens no período de separação
    mask = (df['data_msg'] > fim_encontro) & (df['data_msg'] < inicio_proximo)
    df.loc[mask, 'dias_desde_ultimo_encontro'] = (
        pd.to_datetime(df.loc[mask, 'data_msg']) - pd.to_datetime(fim_encontro)
    ).dt.days

# Mensagens ANTES do primeiro encontro
primeiro_encontro = encontros_ord.iloc[0]['inicio'].date()
mask = df['data_msg'] < primeiro_encontro
df.loc[mask, 'dias_desde_ultimo_encontro'] = None  # Não tinha encontro anterior
```

**Dias Até Próximo Encontro**

```python
# Calcula dias até início do próximo encontro
df['dias_ate_proximo_encontro'] = None

# Ordena encontros por data
encontros_ord = encontros.sort_values('inicio')

for idx, encontro in encontros_ord.iterrows():
    # Encontra período ANTES deste encontro (desde o anterior)
    inicio_encontro = encontro['inicio'].date()
    
    # Encontra encontro anterior
    anteriores = encontros_ord[encontros_ord['fim'] < encontro['inicio']]
    if len(anteriores) > 0:
        fim_anterior = anteriores.iloc[-1]['fim'].date()
    else:
        fim_anterior = df['data_msg'].min()
    
    # Mensagens no período de separação antes deste encontro
    mask = (df['data_msg'] > fim_anterior) & (df['data_msg'] < inicio_encontro)
    df.loc[mask, 'dias_ate_proximo_encontro'] = (
        pd.to_datetime(inicio_encontro) - pd.to_datetime(df.loc[mask, 'data_msg'])
    ).dt.days

# Mensagens APÓS o último encontro
ultimo_encontro = encontros_ord.iloc[-1]['fim'].date()
mask = df['data_msg'] > ultimo_encontro
df.loc[mask, 'dias_ate_proximo_encontro'] = None  # Não tem próximo encontro
```

### Validação

| `em_encontro` | 13,432 msgs durante encontros | Chapada/BSB (1ª viagem) |
| --- | --- | --- |
| `dias_desde_ultimo_encontro` | 76,042 não-nulos | Mediana: 18 dias |
| `dias_ate_proximo_encontro` | 78,464 não-nulos | Mediana: 16 dias |
| `eh_marco_especial` | 114 msgs em marcos | 💕 1ª Vez Juntos |

---

## Consolidação

Verificação final de todas as features criadas.

```
📊 Dataset Enriquecido:
   • Mensagens: 91,924
   • Colunas originais: 8
   • Features criadas: 35
   • Total de colunas: 43

✅ Todas as features foram criadas com sucesso!
```

```
📋 Amostra do Dataset Enriquecido:
```

| 0 | 2024-10-19 13:52:51 | P1 | Le? | 2024 | 10 | Sábado | 13 | Tarde | 3 | 1 | False | NaN | True | False | None |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2024-10-19 13:53:25 | P2 | https://www.localiza.com/brasil/pt-br/reservas... | 2024 | 10 | Sábado | 13 | Tarde | 54 | 1 | False | 34.0 | False | False | None |
| 2 | 2024-10-19 13:53:25 | P1 | None | 2024 | 10 | Sábado | 13 | Tarde | 0 | 0 | False | 0.0 | False | False | None |
| 3 | 2024-10-19 13:53:41 | P2 | None | 2024 | 10 | Sábado | 13 | Tarde | 0 | 0 | False | 16.0 | False | False | None |
| 4 | 2024-10-19 13:53:43 | P2 | Oi | 2024 | 10 | Sábado | 13 | Tarde | 2 | 1 | False | 2.0 | False | False | None |
| 5 | 2024-10-19 13:54:34 | P1 | None | 2024 | 10 | Sábado | 13 | Tarde | 0 | 0 | False | 51.0 | False | False | None |
| 6 | 2024-10-19 13:56:05 | P1 | None | 2024 | 10 | Sábado | 13 | Tarde | 0 | 0 | False | 91.0 | False | False | None |
| 7 | 2024-10-19 13:56:37 | P2 | Arrasou | 2024 | 10 | Sábado | 13 | Tarde | 7 | 1 | False | 32.0 | False | False | None |
| 8 | 2024-10-19 13:56:49 | P2 | confortável | 2024 | 10 | Sábado | 13 | Tarde | 11 | 1 | False | 12.0 | False | False | None |
| 9 | 2024-10-19 13:56:59 | P2 | esse vai de boas | 2024 | 10 | Sábado | 13 | Tarde | 16 | 4 | False | 10.0 | False | False | None |

---

## Exportação

Salvando dataset enriquecido com todas as features.

```python
# Exporta dataset enriquecido
df.to_parquet(OUTPUT_FILE, index=False)

print(f"✅ Dataset exportado com sucesso!")
print(f"📁 Arquivo: {OUTPUT_FILE.name}")
print(f"📊 Shape: {df.shape}")
print(f"💾 Tamanho: {OUTPUT_FILE.stat().st_size / 1024 / 1024:.2f} MB")
```

```python
✅ Dataset exportado com sucesso!
📁 Arquivo: messages_enriched.parquet
📊 Shape: (91924, 43)
💾 Tamanho: 2.60 MB
```

---

## Resumo das Features

Catálogo completo de todas as features criadas neste notebook.

| Temporal | `ano` | int | Ano extraído do timestamp |
| --- | --- | --- | --- |
| Temporal | `trimestre` | category | Trimestre (Q1-Q4) |
| Temporal | `mes` | int | Mês numérico (1-12) |
| Temporal | `data` | date | Data sem hora (YYYY-MM-DD) |
| Temporal | `dia_semana` | category | Dia da semana (Segunda-Domingo) |
| Temporal | `fim_de_semana` | bool | True se Sábado ou Domingo |
| Temporal | `hora` | int | Hora do dia (0-23) |
| Temporal | `periodo_dia` | category | Período (Madrugada, Manhã, Tarde, Noite) |
| Temporal | `horario_comercial` | bool | True se Seg-Sex 08:00-18:00 |
| Texto | `tamanho_caracteres` | int | Quantidade de caracteres no conteúdo |
| Texto | `tamanho_palavras` | int | Quantidade de palavras |
| Texto | `tem_emoji` | bool | True se contém emoji |
| Texto | `qtd_emojis` | int | Quantidade de emojis |
| Texto | `tem_link` | bool | True se contém URL |
| Texto | `tem_mencao` | bool | True se contém menção (@usuario) |
| Texto | `tem_interrogacao` | bool | True se termina com? |
| Texto | `tem_exclamacao` | bool | True se termina com! |
| Texto | `eh_caixa_alta` | bool | True se >70% maiúsculas |
| Conversação | `tempo_desde_ultima_msg` | float | Segundos desde mensagem anterior |
| Conversação | `tempo_desde_ultima_msg_mesmo_remetente` | float | Segundos desde última do mesmo remetente |
| Conversação | `eh_inicio_conversa` | bool | True se gap > 1 hora |
| Conversação | `eh_resposta_rapida` | bool | True se respondeu em < 60s |
| Conversação | `sequencia_mesmo_remetente` | int | Contador de msgs consecutivas |
| Conversação | `turno_conversa` | int | ID do bloco de conversa |
| Conversação | `tempo_resposta_outro_remetente` | float | Segundos até resposta do outro |
| Contexto Externo | `em_encontro` | bool | True se durante encontro presencial |
| Contexto Externo | `encontro_id` | int | ID do encontro (1-10) |
| Contexto Externo | `encontro_nome` | str | Nome descritivo do encontro |
| Contexto Externo | `local_encontro` | str | Cidade/local do encontro |
| Contexto Externo | `tipo_encontro` | str | Quem visitou quem |
| Contexto Externo | `dias_desde_ultimo_encontro` | int | Dias desde término do último encontro |
| Contexto Externo | `dias_ate_proximo_encontro` | int | Dias até início do próximo encontro |
| Contexto Externo | `dia_do_encontro` | int | Dia dentro do encontro (1, 2, 3...) |
| Contexto Externo | `eh_marco_especial` | bool | True se data de marco especial |
| Contexto Externo | `marco_nome` | str | Descrição do marco especial |

```
📊 Estatísticas por Categoria:
```

| Contexto Externo | 10 |
| --- | --- |
| Conversação | 7 |
| Temporal | 9 |
| Texto | 9 |

---

## Próximos Passos

Com o dataset enriquecido, seguimos para:

1. [**Model-Based Features**](http://localhost:7860/notebooks/04-model-features.html) *(opcional)* — Features derivadas de ML
	- Análise de sentimento (BERT)
	- Embeddings semânticos
	- Topic modeling
2. [**Exploratory Data Analysis**](http://localhost:7860/notebooks/05-eda.html) — Análise exploratória das features criadas
	- Distribuições univariadas
	- Análises bivariadas (features vs remetente, tempo, contexto)
	- Correlações entre features
	- Visualizações temporais e padrões
	- Use `messages_with_models.parquet` se disponível
	- Ou `messages_enriched.parquet` para análise sem modelos