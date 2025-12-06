# Model-Based Features

Features derivadas de modelos de Machine Learning
## Configuração

| Entrada | `messages_enriched.parquet` | ~/whatsapp-ds-analytics/data/processed/export\_2024-10\_2025-10 |
| --- | --- | --- |
| Saída | `messages_with_models.parquet` | ~/whatsapp-ds-analytics/data/processed/export\_2024-10\_2025-10 |

---

## Introdução

Este notebook cria **features baseadas em modelos de Machine Learning** que complementam as features estruturais criadas no notebook anterior.

⚠️ **IMPORTANTE:** Todas as análises deste notebook são:

- **Computacionalmente custosas** (podem levar vários minutos)
- **Totalmente opcionais** (não são necessárias para EDA básico)
- **Requerem hardware adequado** (GPU recomendada para alguns modelos)

As features de modelos **não são executadas automaticamente** durante o render. Para aplicá-las, você deve executar os blocos manualmente ou via scripts.

---

## 04-model-features.qmd (índice)

## Análise de Sentimento (BERT)

Classificação de sentimento usando modelos BERT pré-treinados.

**Modelos Disponíveis:**

- [Twitter-XLM-RoBERTa](http://localhost:7860/notebooks/04a-sentiment-roberta.html) (implementado ✅)
- [DistilBERT Multilingual](http://localhost:7860/notebooks/04b-sentiment-distilbert.html) (implementado ✅)
- [RoBERTa Latest](http://localhost:7860/notebooks/04c-sentiment-deberta.html) (implementado ✅)
- [Comparação](http://localhost:7860/notebooks/04d-sentiment-comparison.html) (implementado ✅)
- [Ensemble](http://localhost:7860/notebooks/04e-sentiment-ensemble.html)
- ⏸️ BERTimba (futuro)

---

## Modelo 2: BERTimbau (Futuro)

Modelo BERT treinado especificamente em português brasileiro.

Warning ⏸️ Em Desenvolvimento

Este modelo ainda não foi implementado. A estrutura abaixo serve como placeholder para implementação futura.

### Características

- **Treinamento:** Corpus brasileiro (brWaC)
- **Otimização:** Português do Brasil formal e informal
- **Classes:** 3 (positive, neutral, negative) - após fine-tuning
- **Especial:** Entende melhor gírias e expressões brasileiras

**Script planejado:**`scripts/sentiment_bertimbau.py`

### Execução

```python
# TODO: Implementar sentiment_bertimbau.py

import subprocess

print("🤖 Iniciando análise com BERTimbau...")
print("📦 Modelo: BERTimbau")
print("⏱️  Tempo estimado: 20-35 minutos (CPU) ou 6-12 minutos (GPU)\n")

# Executa script (quando implementado)
result = subprocess.run(['python', 'scripts/sentiment_bertimbau.py'])

if result.returncode == 0:
    print("\n✅ Análise concluída!")
else:
    print("\n❌ Erro na execução.")
```

---

## Text Embeddings (Futuro)

Vetorização semântica das mensagens usando Sentence Transformers.

⏸️ **Status:** Não implementado ainda.

## Features Planejadas

- `embedding_vector` - Vetor de 384 dimensões representando o significado semântico
- `embedding_cluster` - Cluster semântico (após K-means nos embeddings)

**Uso:** Busca semântica, agrupamento de mensagens similares, visualização t-SNE/UMAP.

**Script futuro:**`scripts/embeddings_sentence_transformer.py`

```python
# TODO: Implementar embeddings
# from sentence_transformers import SentenceTransformer
# model = SentenceTransformer('neuralmind/bert-base-portuguese-cased')
# embeddings = model.encode(df['conteudo'].fillna('').tolist())
```

---

### Modelo 2: BERTimbau

Modelo específico para português brasileiro.

**Script:**`scripts/sentiment_bertimbau.py` (ainda não implementado)

```python
# TODO: Implementar comparação entre modelos
# 
# Após rodar múltiplos modelos:
# - Calcular concordância entre modelos
# - Identificar casos discordantes
# - Análise de Cohen's Kappa
```

---

## Topic Modeling (Futuro)

Identificação automática de tópicos nas conversas usando BERTopic.

⏸️ **Status:** Não implementado ainda.

## Features Planejadas

- `topic_id` - ID do tópico identificado
- `topic_name` - Nome/descrição do tópico
- `topic_probability` - Confiança na atribuição do tópico

**Uso:** Descobrir temas recorrentes, evolução de assuntos ao longo do tempo.

```python
# TODO: Implementar topic modeling
# from bertopic import BERTopic
# topic_model = BERTopic(language="portuguese")
# topics, probs = topic_model.fit_transform(df['conteudo'].fillna(''))
```

---

## Named Entity Recognition (Futuro)

Extração de entidades nomeadas (pessoas, lugares, organizações).

⏸️ **Status:** Não implementado ainda.

## Features Planejadas

- `tem_pessoa` - True se menciona pessoa
- `tem_lugar` - True se menciona lugar
- `tem_organizacao` - True se menciona organização
- `entidades_json` - JSON com todas entidades detectadas

**Uso:** Análise de contexto, frequência de menções.

```python
# TODO: Implementar NER
# import spacy
# nlp = spacy.load("pt_core_news_lg")
# doc = nlp(texto)
# entities = [(ent.text, ent.label_) for ent in doc.ents]
```

---

## Consolidação

---

## Exportação

A exportação é feita automaticamente pelos scripts de cada modelo.

```
📁 Arquivos Gerados:

   Input:  messages_enriched.parquet
   Output: messages_with_models.parquet (6.39 MB)

💡 Dica: Use o arquivo com modelos no EDA para análises mais ricas!
```

---

## Resumo das Features de Modelos

| ✅ Implementado | Sentimento | sentimento\_label | category | Classificação (positive/neutral/negative) |
| --- | --- | --- | --- | --- |
| ✅ Implementado | Sentimento | sentimento\_score | float | Confiança do modelo (0-1) |
| ⏸️ Planejado | Embeddings | embedding\_vector | array | Vetor semântico (384d) |
| ⏸️ Planejado | Embeddings | embedding\_cluster | int | Cluster semântico |
| ⏸️ Planejado | Tópicos | topic\_id | int | ID do tópico |
| ⏸️ Planejado | Tópicos | topic\_name | str | Nome do tópico |
| ⏸️ Planejado | Tópicos | topic\_probability | float | Confiança do tópico |
| ⏸️ Planejado | NER | tem\_pessoa | bool | Menciona pessoa |
| ⏸️ Planejado | NER | tem\_lugar | bool | Menciona lugar |
| ⏸️ Planejado | NER | tem\_organizacao | bool | Menciona organização |

```
📊 Estatísticas:
```

| ⏸️ Planejado | Embeddings | 2 |
| --- | --- | --- |
| ⏸️ Planejado | NER | 3 |
| ⏸️ Planejado | Tópicos | 3 |
| ✅ Implementado | Sentimento | 2 |

---

## Próximos Passos

Com as features de modelos (opcionais) criadas, seguimos para:

1. [**Exploratory Data Analysis**](http://localhost:7860/notebooks/05-eda.html) — Análise exploratória
	- Use `messages_with_models.parquet` se disponível
	- Ou `messages_enriched.parquet` para análise sem modelos

---