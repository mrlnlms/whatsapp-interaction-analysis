# Backlog

Tudo que ainda falta, em ordem de prioridade. Itens concluídos saem daqui e vão para o [CHANGELOG](CHANGELOG.md).

## Próximo trabalho (em ordem)

### 1. NLP preprocessing antes do presente

A camada de findings (concluída em 13/abr/2026) revelou que sentiment, embeddings e clustering rodam sobre texto insuficientemente normalizado para chat em PT-BR. Isso precisa ser corrigido **antes** do presente pessoal — o presente só tem valor se os números forem confiáveis.

**Evidências concretas nos findings:**

- **Cluster C3 é inteiramente "kkkkkkk"** em variações de comprimento (`notebooks/10-findings-temas.qmd:79,92`) — 12 variantes da mesma risada viraram 12 tokens distintos no TF-IDF (`kkkk`, `kkkkk`, ..., `kkkkkkkkkkkkkkk`), criando um cluster artificial.
- **System strings no texto**: `message`, `this`, `was`, `edited` aparecem como palavras top em clusters (resíduo de `<This message was edited>`).
- **Modificadores de pele 🏻 🏼** aparecem como top tokens em contagens de emoji — são caracteres Unicode acompanhantes, não emojis em si.
- **Abreviações tratadas como palavras distintas**: `mto` vs `muito`, `vdd` vs `verdade`, `pq` vs `porque`, `tbm` vs `também`, `vc` vs `você`, `tá` vs `está`. Infla o vocabulário e dispersa semântica.
- **Modelos de sentiment treinados em inglês** (`notebooks/09-findings-sentimento.qmd:29` reconhece a limitação) — cenário piora com PT-BR coloquial sujo.

**Escopo:**

1. Módulo `whatsapp/pipeline/nlp_preprocessing.py` (ou extensão de `cleaning.py`):
   - Colapsar `kkkk+` → `kkk` único (regex)
   - Dicionário de abreviações PT-BR de chat (configurável)
   - Limpar system strings (`<This message was edited>`, `<Media omitted>`, modificadores Unicode de pele)
   - Política explícita de emoji (manter / remover / tokenizar como `<EMOJI_HEART>`)
   - Opcional: spell correction leve
2. Regerar embeddings com texto limpo → substituir `.npy` atuais
3. Rerodar sentiment com texto limpo + adicionar **modelo PT-BR (BERTimbau)** para validar ensemble
4. Refazer clustering + findings — C3 provavelmente some ou dilui; "expressões importadas" fica mais nítido
5. Só então: presente pessoal apoiado em findings confiáveis

### 2. Validar fluxo incremental com 2º export real

`docs/INCREMENTAL-GUIDE.md` documenta o fluxo teórico, e o CLI (`whatsapp-interaction prepare/process/run`) foi pensado para isso, mas **nunca rodou com um segundo export real**. Pode ter gaps que só aparecem na prática.

**Quando fizer sentido:** quando chegar um novo export do WhatsApp (conversa segue ativa pós-out/2025). Faz sentido combinar com o item 1 — re-rodar o pipeline inteiro com dado novo + texto limpo numa só passada.

**Pré-requisito soft do presente:** se a conversa continuou depois de out/2025, o presente fica mais rico com dado atualizado.

### 3. Presente pessoal (entregável paralelo)

Versão narrativa dos findings sem jargão técnico, reaproveitando timeline e visualizações. Audiência: a parceira.

- **Status:** destravado tecnicamente (camada de findings entregue), aguardando os itens 1 e 2.
- **Formato:** em aberto (single-page web, PDF, slides). Decidir quando os findings forem regerados.
- **Fora do escopo deste repo** — provavelmente vai para outro projeto / artefato.

## Backlog técnico (sem ordem fixa)

- **DVC para dados processados** — [issue #4](https://github.com/mrlnlms/whatsapp-interaction-analysis/issues/4). Faz sentido depois que houver múltiplos exports versionáveis.
- **Integrar transcrições de áudio/vídeo no NLP** — 25% das mensagens (mídia) ficam fora de clustering/sentiment hoje. Transcrições existem em `transcriptions.csv` mas não entram no corpus textual antes de embeddings.
- **Micro-histórias dos extremos** — examinar qualitativamente os dias de pico (ex: 22/jun/2025 com 1.288 msgs) e os vales para enriquecer a interpretação narrativa.
- **Testes de integração E2E** — pipeline completo de ponta a ponta (clean → wrangle → export) usando o sample como fixture.

## Antena

- **MBA Data Science (ESALQ/USP)** — verificar ocasionalmente se aparece encaixe para usar o projeto em trabalho do curso. Não é direção ativa.

## Perguntas em aberto (de `docs/notes/insights e ideias.md`)

Perguntas que ficaram abertas das notas iniciais e ainda podem virar novos findings:

- Como cada um fala? Quais características de cada remetente? *(parcial — coberto em `11-findings-estilos`)*
- Quem inicia mais conversas? Quem termina?
- "Saudades" — análise temática específica
- Tempo equivalente de "presença" via WhatsApp (~4 dias falando sem parar)
