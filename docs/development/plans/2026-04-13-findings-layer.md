# Plano de Implementação: Camada de Findings

> **Para workers agentic:** use `superpowers:executing-plans` ou execute em sessão. Steps marcáveis com `- [ ]`.

**Goal:** Criar 5 notebooks de descobertas (`07`–`11`), atualizar `index.qmd` com "Principais Descobertas" e adicionar seção "Descobertas" no navbar, fechando a camada de análise/resultados do site Quarto.

**Architecture:** Cada notebook consolida um eixo analítico (overview/dinâmica/sentimento/temas/estilos), combinando (A) síntese curatorial dos outputs existentes em `_freeze/` e prose interpretativa + (B) código novo que carrega dados de `data/processed/export_2024-10_2025-10/` e gera 1-3 gráficos de síntese. Imports via `from whatsapp.pipeline.*`. Privacidade: P1/P2 anonimizados, permissivo a citações curtas com crivo manual posterior.

**Tech Stack:** Quarto (.qmd), Python 3.14, pandas, plotly, scikit-learn, scipy, o pacote `whatsapp.pipeline` local. Dados em CSV/parquet + embeddings `.npy`.

**Spec:** `docs/development/specs/2026-04-13-findings-layer-design.md`

---

## File Structure

**Criar:**
- `notebooks/07-findings-overview.qmd` — abertura narrativa + arco temporal + mapa
- `notebooks/08-findings-dinamica.qmd` — volume/frequência/temporal consolidado
- `notebooks/09-findings-sentimento.qmd` — modelo escolhido + tom + evolução
- `notebooks/10-findings-temas.qmd` — clustering semântico + N-Grams/TF-IDF
- `notebooks/11-findings-estilos.qmd` — P1 vs P2 (emoji/vocab/pontuação/tamanho)

**Modificar:**
- `index.qmd` — adicionar seção "Principais Descobertas" no topo (antes da timeline, L32)
- `_quarto.yml` — adicionar menu "Descobertas" no navbar (entre "Análise" e "Referência")
- `MEMORY.md` auto-memória — apontar pro novo estado

**Referência (leitura):**
- `notebooks/05.3-eda-conteudo.qmd` (usar YAML header como template)
- `data/processed/export_2024-10_2025-10/*.parquet` (fontes de dados)
- `_freeze/notebooks/*/` (outputs cacheados dos notebooks existentes)

---

## Convenções

**YAML header padrão (cada notebook novo):**

```yaml
---
title: "Findings - <TOPICO>"
subtitle: "<subtítulo específico>"
author: "Marlon"
date: today
format:
  html:
    toc: true
    toc-depth: 3
    theme: cosmo
    code-fold: true
    code-tools: true
execute:
  warning: false
  echo: true
  freeze: true
---
```

Note `code-fold: true` (não `show`) — notebook de findings privilegia leitura; código fica disponível mas recolhido.

**Setup code compartilhado (primeira célula Python de cada):**

```python
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from whatsapp.pipeline.config import DATA_FOLDER
import warnings
warnings.filterwarnings('ignore')

DATA_DIR = Path("../data/processed") / DATA_FOLDER
```

**Commits:** conventional em PT-BR, via `~/.claude/scripts/commit.sh`. Um commit por notebook completo, não por step.

**Verificação:** após cada notebook, rodar `quarto render notebooks/<novo>.qmd` e inspecionar HTML em `_site/notebooks/<novo>.html`. Se renderizar sem erro e o HTML tem prose + gráficos → passa.

---

## Task 1: Auditar outputs existentes

**Objetivo:** Gerar um "banco de findings" único com números reais extraídos dos notebooks existentes, pra alimentar os 5 notebooks novos sem ter que revisitar tudo a cada seção.

**Files:**
- Criar: `docs/development/plans/findings-source-bank.md` (scratch, pode deletar depois)

- [ ] **Step 1.1:** Ler `data/processed/export_2024-10_2025-10/messages.csv` e extrair métricas globais (total de mensagens, período, contagem por remetente, média por dia).
- [ ] **Step 1.2:** Ler `messages_with_models.parquet` e extrair colunas de sentiment disponíveis (roberta, distilbert, deberta). Calcular distribuições e concordância.
- [ ] **Step 1.3:** Ler `messages_clustered.parquet` e verificar que clustering já existe. Listar clusters, tamanhos, palavras-chave se disponíveis.
- [ ] **Step 1.4:** Ler `messages_enriched.parquet` e ver que features existem (contagem de emoji, tamanho, etc.).
- [ ] **Step 1.5:** Grep em `notebooks/*.qmd` pelos padrões "podemos ver que", "observa-se", "conclui", "indica" pra extrair conclusões já escritas.
- [ ] **Step 1.6:** Gravar tudo em `findings-source-bank.md` organizado por eixo (dinâmica/sentimento/temas/estilos).
- [ ] **Step 1.7:** Commit não necessário — scratch file.

---

## Task 2: Atualizar `_quarto.yml` com nova seção "Descobertas"

**Files:**
- Modificar: `_quarto.yml` (navbar)

- [ ] **Step 2.1:** Abrir `_quarto.yml` e localizar o menu "Análise" no navbar.
- [ ] **Step 2.2:** Adicionar novo menu "Descobertas" logo após "Análise", contendo os 5 notebooks:
  ```yaml
  - text: Descobertas
    menu:
      - href: notebooks/07-findings-overview.qmd
        text: "07 - Overview"
      - href: notebooks/08-findings-dinamica.qmd
        text: "08 - Dinâmica"
      - href: notebooks/09-findings-sentimento.qmd
        text: "09 - Sentimento"
      - href: notebooks/10-findings-temas.qmd
        text: "10 - Temas"
      - href: notebooks/11-findings-estilos.qmd
        text: "11 - Estilos"
  ```
- [ ] **Step 2.3:** Adicionar as mesmas entradas no sidebar se houver um configurado análogo.
- [ ] **Step 2.4:** Não commitar ainda — vai junto com o primeiro notebook.

---

## Task 3: Scaffold dos 5 notebooks (smoke test)

**Objetivo:** Criar os 5 arquivos com YAML + setup + seções vazias e garantir que renderizam. Isola problemas de configuração antes do trabalho de conteúdo.

**Files:**
- Criar: `notebooks/07-findings-overview.qmd`
- Criar: `notebooks/08-findings-dinamica.qmd`
- Criar: `notebooks/09-findings-sentimento.qmd`
- Criar: `notebooks/10-findings-temas.qmd`
- Criar: `notebooks/11-findings-estilos.qmd`

- [ ] **Step 3.1:** Criar os 5 arquivos com o YAML header padrão (ver Convenções) + uma célula de setup + placeholders `# TODO` em cada seção planejada.
- [ ] **Step 3.2:** Rodar `quarto render notebooks/08-findings-dinamica.qmd` e verificar que renderiza sem erro. Fazer o mesmo nos outros 4.
- [ ] **Step 3.3:** Rodar `quarto render` (site inteiro) e abrir `_site/index.html` para verificar que o navbar "Descobertas" aparece e os links funcionam (mesmo que as páginas sejam quase vazias).
- [ ] **Step 3.4:** Commit: `~/.claude/scripts/commit.sh "feat: scaffold dos 5 notebooks de findings + navbar atualizado"`

---

## Task 4: Construir `11-findings-estilos.qmd` (primeiro — tem mais base)

**Por que primeiro:** 05.3-eda-conteudo já é categoria C (tem findings). Vai ser o notebook com menos improviso.

**Files:**
- Modificar: `notebooks/11-findings-estilos.qmd`

**Seções-alvo:**
1. Abertura (1 parágrafo: o que é "estilo" nessa análise)
2. Volume e tamanho (quem escreve mais, mensagem média, distribuição)
3. Pontuação e capitalização (P1 formal vs P2 expressivo?)
4. Emojis (top 10 por pessoa, divergência de uso)
5. Vocabulário (top palavras únicas, sobreposição)
6. Conclusão sintética (3-5 bullets: "o que os dados dizem de cada um")

- [ ] **Step 4.1:** Carregar `messages_enriched.parquet` e selecionar colunas relevantes (sender, text, char_count, word_count, emoji_count).
- [ ] **Step 4.2:** Computar métricas por remetente (groupby + agg) e escrever prose com números reais.
- [ ] **Step 4.3:** Gráfico novo (B): painel `plotly` com 2 subplots — distribuição de tamanho por remetente + top emojis por remetente. Exportar para `assets/images/findings-estilos-painel.png` (opcional) ou manter só inline.
- [ ] **Step 4.4:** Escrever seção 6 (conclusão) sintetizando os achados em bullets. Usar P1/P2, não nomes.
- [ ] **Step 4.5:** Render + inspeção visual: `quarto render notebooks/11-findings-estilos.qmd && open _site/notebooks/11-findings-estilos.html`.
- [ ] **Step 4.6:** Ajustes de tom/número até ficar fluido.
- [ ] **Step 4.7:** Commit: `~/.claude/scripts/commit.sh "feat: notebook 11-findings-estilos (P1 vs P2)"`

---

## Task 5: Construir `08-findings-dinamica.qmd`

**Seções-alvo:**
1. Abertura (visão de um ano em volume)
2. Volume total e evolução (total + curva mensal)
3. Padrões semanais (dia da semana)
4. Padrões diários (hora do dia)
5. Efeito "juntos vs separados" (se `em_encontro` existir)
6. Conclusão (3-5 bullets)

- [ ] **Step 5.1:** Carregar `messages_with_context.parquet` (tem `em_encontro` se existir) ou `messages.parquet`.
- [ ] **Step 5.2:** Computar série temporal diária (count por data) e salvar em DataFrame.
- [ ] **Step 5.3:** Escrever seção 2 (curva mensal) com prose + gráfico.
- [ ] **Step 5.4:** Computar heatmap hora x dia-da-semana.
- [ ] **Step 5.5:** Gráfico novo (B): heatmap com plotly (`px.imshow`) e prose interpretativa.
- [ ] **Step 5.6:** Seção 5 se `em_encontro` existir: comparar volume médio juntos vs separados (t-test se fizer sentido).
- [ ] **Step 5.7:** Conclusão em bullets.
- [ ] **Step 5.8:** Render e inspeção: `quarto render notebooks/08-findings-dinamica.qmd`.
- [ ] **Step 5.9:** Commit: `~/.claude/scripts/commit.sh "feat: notebook 08-findings-dinamica (volume e padrões temporais)"`

---

## Task 6: Construir `09-findings-sentimento.qmd`

**Seções-alvo:**
1. Abertura (o que foi testado — 3 modelos)
2. Por que escolher um modelo (comparar concordância + viés)
3. Modelo escolhido e justificativa (recomendação com 1 parágrafo)
4. Distribuição do tom geral (positivo/neutro/negativo)
5. Evolução mensal do sentimento
6. Sentimento por remetente
7. Conclusão (3-5 bullets)

- [ ] **Step 6.1:** Carregar `messages_with_models.parquet`. Identificar colunas de sentiment disponíveis (algo como `sentiment_roberta`, `sentiment_distilbert`, `sentiment_deberta`).
- [ ] **Step 6.2:** Computar concordância entre os 3 modelos (% das mensagens onde 2 ou 3 concordam).
- [ ] **Step 6.3:** Escrever seção 2 com prose justificando a escolha (pode ser "ensemble" se implementado, ou RoBERTa/DeBERTa). Citar números de concordância.
- [ ] **Step 6.4:** Distribuição global: contagem + % de cada classe. Gráfico novo (B): donut ou barras horizontais.
- [ ] **Step 6.5:** Série temporal mensal: agg por mês + classe. Gráfico novo (B): linha empilhada ou área.
- [ ] **Step 6.6:** Comparação P1 vs P2: % positivo/neutro/negativo por remetente.
- [ ] **Step 6.7:** Conclusão em bullets.
- [ ] **Step 6.8:** Render e inspeção.
- [ ] **Step 6.9:** Commit: `~/.claude/scripts/commit.sh "feat: notebook 09-findings-sentimento (modelo escolhido e tom dominante)"`

---

## Task 7: Construir `10-findings-temas.qmd`

**Este é o mais trabalhoso** — requer rodar ou conferir clustering.

**Seções-alvo:**
1. Abertura (de embeddings a temas)
2. Qual embedding usado e por quê
3. Clustering: nº de clusters, método (K-Means? HDBSCAN?), tamanho
4. Caracterização de cada cluster (keywords via TF-IDF ou top palavras)
5. Mapa 2D dos clusters (UMAP ou t-SNE)
6. Evolução temporal dos temas (qual cluster dominou em qual mês)
7. Conclusão (3-5 bullets — quais temas definem a conversa)

- [ ] **Step 7.1:** Verificar `messages_clustered.parquet` — já tem clusters? Se sim, carregar e pular para Step 7.4.
- [ ] **Step 7.2:** Se não tem, carregar embeddings de `data/processed/.../message_embeddings_mpnet.npy` + mensagens originais.
- [ ] **Step 7.3:** Rodar K-Means (k=8? escolher via silhouette curto) ou reaproveitar código de `06-advanced-analysis`.
- [ ] **Step 7.4:** Para cada cluster, extrair top N palavras via TF-IDF (excluindo stopwords PT-BR).
- [ ] **Step 7.5:** Nomear clusters manualmente (ex: "Cluster 3 = rotina diária"). Escrever prose por cluster.
- [ ] **Step 7.6:** Gráfico novo (B): UMAP 2D colorido por cluster (plotly scatter).
- [ ] **Step 7.7:** Série temporal: clusters dominantes por mês (heatmap ou linha empilhada).
- [ ] **Step 7.8:** Conclusão em bullets.
- [ ] **Step 7.9:** Render e inspeção.
- [ ] **Step 7.10:** Commit: `~/.claude/scripts/commit.sh "feat: notebook 10-findings-temas (clustering semantico e temas)"`

---

## Task 8: Construir `07-findings-overview.qmd` (por último — referencia os outros)

**Seções-alvo:**
1. Abertura narrativa (3 parágrafos contando o arco do ano em prose)
2. Escala e escopo (números de grande porte: total, período, remetentes, mídia)
3. Resumo dos 4 eixos (cada um 1 parágrafo + link pro notebook completo)
4. Principais descobertas (5-7 bullets que viram também o `index.qmd`)
5. Limitações e caveats (3 bullets: modelos em EN para texto PT, 1 conversa, etc.)

- [ ] **Step 8.1:** Carregar `messages.parquet` e computar números gerais (total, período, remetentes).
- [ ] **Step 8.2:** Escrever seção 1 (abertura) — prose pura, sem código. Use a Timeline Ultimate como âncora visual.
- [ ] **Step 8.3:** Seção 2 (escala) — números em cards ou tabela compacta.
- [ ] **Step 8.4:** Seção 3 (resumo dos 4 eixos): ler os notebooks 08-11 e condensar a conclusão de cada um em 1 parágrafo + link `[continuar lendo](08-findings-dinamica.qmd)`.
- [ ] **Step 8.5:** Seção 4 (Principais Descobertas) — 5-7 bullets-chave. **Reutilizar no index.qmd depois.**
- [ ] **Step 8.6:** Seção 5 (caveats).
- [ ] **Step 8.7:** Render e inspeção.
- [ ] **Step 8.8:** Commit: `~/.claude/scripts/commit.sh "feat: notebook 07-findings-overview (abertura narrativa + resumo)"`

---

## Task 9: Atualizar `index.qmd` com "Principais Descobertas"

**Files:**
- Modificar: `index.qmd`

- [ ] **Step 9.1:** Abrir `index.qmd` e localizar a Timeline (linha 32-38 aprox, `# Timeline: Um Ano em Dados`).
- [ ] **Step 9.2:** Adicionar nova seção `# Principais Descobertas` ANTES da Timeline.
- [ ] **Step 9.3:** Copiar os 5-7 bullets da Seção 4 do `07-findings-overview.qmd`, cada bullet linkando pro notebook correspondente. Formato:
  ```markdown
  - **P1 e P2 têm estilos opostos de escrita** — [ver detalhes](notebooks/11-findings-estilos.qmd)
  - **O tom da conversa é majoritariamente positivo** — [ver detalhes](notebooks/09-findings-sentimento.qmd)
  - ...
  ```
- [ ] **Step 9.4:** Adicionar um link geral para `notebooks/07-findings-overview.qmd` com texto "Leia o panorama completo →".
- [ ] **Step 9.5:** Render do site: `quarto render`.
- [ ] **Step 9.6:** Abrir `_site/index.html` e verificar que a seção aparece visível no topo, antes da Timeline.
- [ ] **Step 9.7:** Commit: `~/.claude/scripts/commit.sh "feat: adiciona Principais Descobertas na homepage"`

---

## Task 10: Render final + deploy + memória

- [ ] **Step 10.1:** Rodar `quarto render` full site e confirmar que todos os 5 notebooks novos + index renderizam sem erro.
- [ ] **Step 10.2:** Verificar que o navbar "Descobertas" aparece e todos os links funcionam localmente em `_site/`.
- [ ] **Step 10.3:** `git push` — CI vai disparar o workflow `publish.yml` e atualizar o GitHub Pages automaticamente.
- [ ] **Step 10.4:** Aguardar ~3 min e abrir https://mrlnlms.github.io/whatsapp-interaction-analysis/ para verificar que foi pro ar.
- [ ] **Step 10.5:** Atualizar `MEMORY.md` auto-memória do projeto: marcar camada de findings como concluída, atualizar contagem de notebooks (de 20 para 25), mover "fechar análise/resultados" da pendência em `project-purpose-and-deliverables.md`.
- [ ] **Step 10.6:** Comentar ou abrir issue de follow-up: "após crivo manual de privacidade, revisar notebooks 07-11 e remover mensagens sensíveis que eventualmente vazarem".

---

## Checkpoints de revisão humana

Recomendo pausar pra você revisar depois de cada notebook (Tasks 4-8). Especialmente importante:

- **Task 4 (estilos)** — primeira amostra do tom. Se não tiver a voz certa, calibro antes de seguir.
- **Task 7 (temas)** — se o clustering não produz grupos semanticamente coerentes, pode precisar ajustar k ou usar HDBSCAN.
- **Task 9 (index)** — os 5-7 bullets viram a "vitrine" do projeto. Vale revisão cuidadosa.

---

## Notas de execução

- **Test-driven** não se aplica aqui (notebook de prose + viz). Substituímos por "render + inspeção visual".
- **YAGNI:** não criar gráficos pela metade nem seções vazias. Se algo não dá pra concluir, removo a seção e marco no caveats do overview.
- **DRY:** se um número aparece em >1 notebook, calcular uma vez e reutilizar (pode ser em comentário no próprio código).
- **Commits frequentes:** um por notebook completo. Não commitar notebook meio pronto.
