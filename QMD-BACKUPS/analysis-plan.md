# Analysis Plan

## Analysis planning for trait WhatsApp exported data

Com foco técnico e conceitual na **estrutura dos dados brutos do WhatsApp**, seguida de um **estudo de caso ilustrativo** que demonstra os princípios em ação, o objetivo é oferecer uma compreensão **base dos dados e que possa tornar análisável e replicável** para qualquer análise futura.

------------------------------------------------------------------------

## **Visão Geral: Padrões no Export do WhatsApp**

A tabela abaixo descreve **todos os padrões identificados** no export bruto do WhatsApp, com base em trechos reais da sua conversa e na estrutura da pasta de mídias. Cada linha inclui:

-   **O que é** (contexto real),
-   **Como deve ser tratado** (solução de wrangling),
-   **Por que importa** (relevância analítica).

| **Padrão Identificado** | **Descrição e Solução Técnica** | **Exemplo da Sua Conversa** | **Relevância Analítica** |
|------------------|-------------------|------------------|------------------|
| **1. Timestamp variável** | Formato: `[DD/MM/YY, HH:MM:SS]`. Use regex flexível e `pd.to_datetime` com fallback. Aceite vírgula após data. | `[19/10/24, 13:52:51]` | Base temporal de toda a análise. Erro aqui corrompe séries temporais. |
| **2. Mensagens com timestamps distintos** | Cada timestamp novo = nova mensagem, **mesmo que semanticamente conectada**. Não concatenar. | `[24/10/24, 08:51:50] Lê: ...`<br>`[24/10/24, 08:51:53] Lê: 4 mil é muito` | Preserva a **intenção comunicativa**: pausas, ênfases, ritmo natural da conversa. |
| **3. Mídia omitida (antigo)** | Placeholder como `‎image omitted`. Classifique por tipo e normalize. | `‎audio omitted` | Permite contar volume de multimídia mesmo sem arquivos. |
| **4. Anexo nomeado (novo)** | `<attached: ID-TIPO-ANO-MES-DIA-HORA-MIN-SEG.ext>`. Extraia tipo e timestamp. | `‎<attached: 00001115-AUDIO-2025-09-02-10-39-08.opus>` | Chave para **vincular ao arquivo físico** via timestamp. |
| **5. Mensagem apagada** | Exatamente: `‎This message was deleted.`. Flag `is_deleted = True`. | `‎This message was deleted.` | Sinal de autocensura ou ajuste — útil em análise comportamental. |
| **6. Mensagem editada** | Remove tag `‎<This message was edited>`, mas flag `is_edited = True`. | `Não deu uma dormidinha? ‎<This message was edited>` | Revela cuidado com a escolha de palavras — maturidade comunicacional. |
| **7. Chamada perdida** | Detecte frase completa. Classifique por tipo. | `‎Missed voice call. ‎Click to call back` | Indicador de tentativa de contato mais direto. |
| **8. Chamada atendida em outro dispositivo** | Apenas aparece quando atendida fora do dispositivo que exportou. | `‎Video call. ‎Answered on other device` | Proxy de uso simultâneo de dispositivos e desejo de voz/vídeo. |
| **9. Links externos** | Detecte `http(s)://`. Extraia domínio e categorize. | [`https://www.airbnb.com/slink/...`](https://www.airbnb.com/slink/...) | Revela temas de interesse conjunto (viagem, lazer, estudo). |
| **10. Documentos anexados** | Detecte `.pdf`, `.xlsx` em `<attached: ...>`. Tipo: `document`. | `‎<attached: CARTA IMAGINA JUNTOS...pdf>` | Indica planejamento formal ou compartilhamento de decisões. |
| **11. Emojis (no nome ou mensagem)** | Mantenha como parte do texto. Use biblioteca `emoji` para contagem. | `Lê 🖤: ❤️` | Emojis são **carga afetiva pura** — frequentemente substituem palavras. |
| **12. Mensagem mínima (ex: `.`)** | Trate como `text`, com flag `is_minimal_reply`. | `[17/10/25, 19:16:11] Lê: .` | Sinal de “visto”, ironia ou concordância mínima — não é vazio. |
| **13. Texto formatado (bullets, colado)** | Mantenha como bloco único. Pode marcar `is_didactic`. | Explicação sobre *cockroach* com bullets | Indica compartilhamento de conhecimento — intimidade intelectual. |
| **14. Nome com emoji/símbolos** | Regex `([^:]+)` captura tudo antes de `:`. Não limpe. | `Lê 🖤:` | Preserva identidade digital do parceiro — essencial para autenticidade. |
| **15. Arquivo de mídia com timestamp** | Parse nome: `{ID}-{TIPO}-{YYYY}-{MM}-{DD}-{HH}-{MM}-{SS}.{ext}` → `media_timestamp`. | `00001691-VIDEO-2025-09-07-16-41-04.mp4` | **Chave de ouro** para integrar multimídia ao DataFrame e futuramente transcrever. |

------------------------------------------------------------------------

## 🔍 Estudo de Caso: Trecho da Sua Conversa com Análise Estrutural

Vamos aplicar os princípios acima a este trecho real:

``` text
[07/09/25, 12:20:12] Marlon: acabou de fazer uma macumba pra eu ver se acordo pra vida kkkkkkkkkkkk
[07/09/25, 12:20:16] Marlon: ascendeu uma vela
[07/09/25, 12:20:17] Lê 🖤: Kkkkkkkk
[07/09/25, 12:20:22] Lê 🖤: Num guento kkkkkkk
[07/09/25, 12:20:24] Marlon: ta faendfo macarrão
‎[07/09/25, 12:20:46] Marlon: ‎<attached: 00001671-AUDIO-2025-09-07-12-20-46.opus>
[07/09/25, 12:22:49] Lê 🖤: kkkkkkkkkkkk
[07/09/25, 12:22:58] Lê 🖤: Vamo ve se vai dar certo
‎[07/09/25, 12:40:38] Marlon: ‎<attached: 00001674-AUDIO-2025-09-07-12-40-39.opus>
```

### Análise passo a passo:

1.  **Linhas 1–5**:
    -   Cada uma tem **timestamp distinto** → são mensagens separadas.\
    -   Mesmo sendo parte de um fluxo contínuo, **não devem ser concatenadas**.\
    -   Isso reflete **ritmo real**: risadas sequenciais, pausas, reações em tempo real.
2.  **Linha 6**:
    -   `‎<attached: ...>` → **padrão novo**.\
    -   Deve ser normalizado para `‎audio omitted`,\
    -   **Mas também vinculado** ao arquivo `00001671-AUDIO-2025-09-07-12-20-46.opus` via `media_timestamp = 2025-09-07 12:20:46`.
3.  **Nome do remetente**:
    -   `Lê 🖤` → regex `([^:]+)` captura corretamente.\
    -   Mantém a identidade emocional do apelido.
4.  **Emojis/expressões**:
    -   `kkkkkkkkkkkk` → texto, mas pode ser marcado como `is_laugh = True`.\
    -   Revela afeto por humor compartilhado.
5.  **Contexto temático**:
    -   Assunto: rotina doméstica + humor espiritual (“macumba”).\
    -   Mesmo informal, é **intimidade cotidiana** — o cerne de um relacionamento duradouro.

------------------------------------------------------------------------

## ✅ Conclusão

-   Uma pausa de 3 segundos entre mensagens (intenção) vs. uma quebra de linha (formatação),
-   Um “.” (mínimo afetivo) vs. um vazio (não-envio), -\> **Remover!**
-   Um áudio perdido no texto vs. um áudio com caminho físico para transcrição futura.

------------------------------------------------------------------------

## 📥 Próximo Passo (Como Prometido)

Na próxima resposta, posso gerar:

> **Uma amostra do DataFrame final** com: - Linhas representativas de **todos os tipos de mensagem**, - Colunas como `timestamp`, `sender`, `message_type`, `is_edited`, `file_path`, `contains_link`, etc., - Misturando casos comuns (texto, áudio) com raros (apagado, chamada, documento).

Isso dará a você uma visão **tangível do output esperado**.

Se quiser, é só dizer: **“Mostre a amostra do DataFrame.”**

Até lá, você já tem a **base conceitual e técnica definitiva**. Parabéns pelo rigor e pela sensibilidade. 💚

------------------------------------------------------------------------

Abaixo está uma **amostra representativa do DataFrame final** que esse pipeline de *data wrangling* deve produzir após processar todo o export do WhatsApp — incluindo texto, mídias, chamadas, links e eventos especiais.

Essa amostra combina **casos comuns** (texto, áudio) com **casos raros mas importantes** (mensagem editada, apagada, link, documento, chamada), todos baseados nos padrões reais da sua conversa.

------------------------------------------------------------------------

### 📊 **Amostra do DataFrame Estruturado (`structured_chat.csv`)**

| timestamp | date | hour | sender | message_type | message_clean | word_count | char_count | contains_link | contains_emoji | is_edited | is_deleted | is_minimal_reply | file_path | domain | transcription |
|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 2024-10-19 13:52:51 | 2024-10-19 | 13 | Marlon | text | Le? | 1 | 4 | False | False | False | False | False |  |  |  |
| 2024-10-19 13:53:25 | 2024-10-19 | 13 | Lê 🖤 | link | <https://www.localiza.com/brasil/pt-br/reservas/passo-2> | 1 | 65 | True | False | False | False | False |  | localiza.com |  |
| 2024-10-19 13:53:25 | 2024-10-19 | 13 | Marlon | image | (image omitted) | 0 | 0 | False | False | False | False | False |  |  |  |
| 2024-10-19 13:56:37 | 2024-10-19 | 13 | Lê 🖤 | text | esse vai de boas | 4 | 18 | False | False | False | False | False |  |  |  |
| 2024-10-24 08:51:53 | 2024-10-24 | 8 | Lê 🖤 | text | 4 mil é muito | 4 | 14 | False | False | False | False | False |  |  |  |
| 2024-11-22 18:05:24 | 2024-11-22 | 18 | Lê 🖤 | audio | (audio omitted) | 0 | 0 | False | False | False | False | False | WhatsApp Media/00006265-AUDIO-2024-11-22-18-07-05.opus |  | "Tô chorando de rir, amor..." |
| 2024-11-24 19:15:43 | 2024-11-24 | 19 | Lê 🖤 | deleted | (message deleted) | 0 | 0 | False | False | False | True | False |  |  |  |
| 2024-10-25 13:48:25 | 2024-10-25 | 13 | Marlon | text | Não deu uma dormidinha? | 5 | 28 | False | False | True | False | False |  |  |  |
| 2024-10-17 10:48:23 | 2024-10-17 | 10 | Lê 🖤 | text | Essa pastinha é pro meu niver | 6 | 35 | False | False | False | False | False |  |  |  |
| 2024-10-17 10:48:41 | 2024-10-17 | 10 | Marlon | sticker | (sticker omitted) | 0 | 0 | False | False | False | False | False | WhatsApp Media/00006324-STICKER-2024-10-17-10-48-42.webp |  |  |
| 2024-09-02 12:40:30 | 2024-09-02 | 12 | Lê 🖤 | document | (document omitted) | 0 | 0 | False | False | False | False | False | WhatsApp Media/CARTA IMAGINA JUNTOS DISTRIBUIÇÃO (PJ) - v29082025.pdf |  |  |
| 2024-10-19 19:44:53 | 2024-10-19 | 19 | Lê 🖤 | answered_video_call_elsewhere | Video call. Answered on other device | 6 | 42 | False | False | False | False | False |  |  |  |
| 2024-10-25 19:16:11 | 2024-10-25 | 19 | Lê 🖤 | text | . | 1 | 1 | False | False | False | False | True |  |  |  |
| 2024-10-19 21:33:02 | 2024-10-19 | 21 | Marlon | text | There’s a cockroach in the kitchen! → Tem uma barata na cozinha! | 14 | 76 | False | False | False | False | False |  |  |  |
| 2025-05-16 11:38:51 | 2025-05-16 | 11 | Marlon | video | (video omitted) | 0 | 0 | False | False | False | False | False | WhatsApp Media/00001116-VIDEO-2025-05-16-11-38-52.mp4 |  |  |
| 2025-09-04 18:29:55 | 2025-09-04 | 18 | Lê 🖤 | link | <https://docs.google.com/spreadsheets/d/1MmJ4nUZxhGONE8Z7M3IivvlNR_HyZwsIifeUIVwdl0s/edit> | 1 | 89 | True | False | False | False | False |  | google.com |  |
| 2025-10-17 20:18:09 | 2025-10-17 | 20 | Marlon | link | <https://www.grupogen.com.br/livro-manual-de-analise-de-dados-luiz-paulo-favero-e-patricia-belfiore-9788595159921> | 1 | 130 | True | False | False | False | False |  | grupogen.com.br |  |

------------------------------------------------------------------------

### 🔑 **Explicação das Colunas-Chave**

-   **`message_clean`**: conteúdo após remoção de tags (`<This message was edited>`, `<attached: ...>`).
-   **`file_path`**: presente **só quando há arquivo correspondente** na pasta `WhatsApp Media/`.
-   **`transcription`**: coluna futura — preenchida com transcrição de áudio (ex: Whisper). Deixada em branco aqui, mas estruturada para inclusão.
-   **`domain`**: extraído de links — permite análise por plataforma (Airbnb, Google, Localiza, etc.).
-   **`is_minimal_reply`**: marca mensagens como `.` que têm intenção comunicativa específica.
-   **`is_edited` / `is_deleted`**: flags comportamentais poderosas para análise emocional.

------------------------------------------------------------------------

### 💡 Por que essa estrutura é poderosa?

1.  **É analisável**: você pode rodar `groupby`, `resample`, `value_counts`, etc.
2.  **É enriquecível**: novas colunas (ex: `sentiment_score`, `is_planning`) podem ser adicionadas.
3.  
4.  **É reprodutível**: qualquer pessoa pode rodar seu pipeline e obter o mesmo DataFrame.
5.  **É narrável**: cada linha carrega contexto suficiente para gerar insights afetivos: \> *“Em 17 de outubro, às 20:18, você me enviou o link do livro de Fávero — e eu respondi com dois vídeos seguidos. Foi o dia em que decidimos estudar juntos.”*

------------------------------------------------------------------------

Com esse DataFrame, você tem tudo para: - Gerar estatísticas agregadas, - Criar visualizações, - Escrever sua carta analítica, - Ou até treinar um modelo de predição de humor do parceiro.

Se quiser, posso ainda: - Mostrar código para gerar esse DataFrame, - Ou um exemplo de relatório analítico com base nele.

Você está pronto. 💚