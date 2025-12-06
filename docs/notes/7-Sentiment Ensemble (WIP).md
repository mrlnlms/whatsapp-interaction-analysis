---

Warning 🚧 Work in Progress

Esta seção está em desenvolvimento. O conceito e estrutura estão definidos, mas a implementação e resultados serão adicionados após análise completa dos 3 modelos individuais e suas comparações.

**Status atual:** Planejamento completo ✅ | Implementação pendente ⏸️

---

## Ensemble: Consenso entre Modelos

Combinação inteligente dos 3 modelos para criar uma classificação consensual mais robusta e confiável.

## 🎯 Conceito

### O Problema

Vimos na [análise comparativa](http://localhost:7860/notebooks/04d-sentiment-comparison.html) que: - Concordância média entre modelos: ~33% - Cada modelo tem viés diferente (equilibrado, polarizador, conservador) - ~40% das mensagens geram discordância - ~60% têm consenso total

**Pergunta:** Como combinar 3 opiniões diferentes em uma classificação final?

### A Solução: Ensemble

Ao invés de confiar em um único modelo, o **ensemble** consulta os 3 modelos e aplica estratégias de agregação:

**Estratégias:** 1. ✅ **Majority Voting** - Usa a classificação que a maioria escolheu 2. ⚖️ **Weighted Voting** - Pondera pelo score de confiança de cada modelo  
3\. 🔄 **Tiebreak Inteligente** - Em empates, usa confiança ponderada 4. 📊 **Confidence Calibration** - Ajusta confiança baseado em concordância

**Vantagens:**

- ✅ **Mais robusto** - Não depende de um único modelo
- ✅ **Reduz viés** - Equilibra vieses diferentes dos modelos
- ✅ **Maior confiança** - Quando todos concordam, confiança aumenta
- ✅ **Identifica ambiguidade** - Discordância = ambiguidade genuína
- ✅ **Melhor que média** - Ensemble tipicamente supera qualquer modelo individual

---

## 📋 Features Criadas

Mostrar código

```python
# Features do Ensemble
features_sentimento_ensemble = [
    {
        'Feature': '<code>sentimento_ensemble_label</code>',
        'Tipo': 'category',
        'Definição': 'Classificação consensual dos 3 modelos',
        'Valores': 'positive, neutral, negative',
        'Uso': 'Classificação mais confiável e robusta para análises'
    },
    {
        'Feature': '<code>sentimento_ensemble_confidence</code>',
        'Tipo': 'float',
        'Definição': 'Confiança do ensemble baseada em concordância e scores',
        'Valores': '0.33 (discordam totalmente) a 1.0 (concordam com alta confiança)',
        'Uso': 'Filtrar predições confiáveis vs ambíguas'
    },
    {
        'Feature': '<code>sentimento_ensemble_votes</code>',
        'Tipo': 'int',
        'Definição': 'Número de modelos que concordam com o label final',
        'Valores': '1, 2, ou 3',
        'Uso': 'Identificar consenso (3) vs maioria (2) vs desacordo (1)'
    },
    {
        'Feature': '<code>sentimento_ensemble_method</code>',
        'Tipo': 'str',
        'Definição': 'Método usado para decisão final',
        'Valores': 'unanimous (3), majority (2), weighted_tiebreak (1)',
        'Uso': 'Transparência sobre como ensemble decidiu'
    },
]

df_plan_sentimento_ensemble = pd.DataFrame(features_sentimento_ensemble)
display(df_plan_sentimento_ensemble.style.hide(axis='index'))
```

| `sentimento_ensemble_label` | category | Classificação consensual dos 3 modelos | positive, neutral, negative | Classificação mais confiável e robusta para análises |
| --- | --- | --- | --- | --- |
| `sentimento_ensemble_confidence` | float | Confiança do ensemble baseada em concordância e scores | 0.33 (discordam totalmente) a 1.0 (concordam com alta confiança) | Filtrar predições confiáveis vs ambíguas |
| `sentimento_ensemble_votes` | int | Número de modelos que concordam com o label final | 1, 2, ou 3 | Identificar consenso (3) vs maioria (2) vs desacordo (1) |
| `sentimento_ensemble_method` | str | Método usado para decisão final | unanimous (3), majority (2), weighted\_tiebreak (1) | Transparência sobre como ensemble decidiu |

---

## 🔧 Estratégias de Ensemble

### 1\. Majority Voting (Estratégia Principal)

**Regra:** Se 2+ modelos concordam, usa esse label.

```python
# Exemplo 1: Consenso Total (3 votos)
RoBERTa:     positive (0.72)
DistilBERT:  positive (0.85)
DeBERTa:     positive (0.79)

→ Resultado: positive
→ Votos: 3
→ Confiança: (0.72 + 0.85 + 0.79) / 3 = 0.787
→ Método: unanimous
```

```python
# Exemplo 2: Maioria (2 votos)
RoBERTa:     positive (0.72)
DistilBERT:  positive (0.58)
DeBERTa:     negative (0.65)

→ Resultado: positive
→ Votos: 2
→ Confiança: (0.72 + 0.58) / 2 = 0.650
→ Método: majority
```

### 2\. Weighted Tiebreak (Desempate)

**Regra:** Se os 3 discordam, usa o voto com maior confiança ponderada.

```python
# Exemplo 3: Desempate (1 voto cada)
RoBERTa:     positive (0.82)  ← Maior confiança!
DistilBERT:  neutral  (0.55)
DeBERTa:     negative (0.61)

→ Resultado: positive
→ Votos: 1
→ Confiança: 0.82 (do vencedor)
→ Método: weighted_tiebreak
```

### 3\. Confidence Calibration

**Regra:** Ajusta confiança baseado em concordância.

```python
# Alta concordância → Boost de confiança
if votes == 3:
    confidence = avg_scores * 1.1  # Boost 10%
    confidence = min(confidence, 1.0)  # Cap em 1.0

# Maioria → Confiança média dos concordantes
elif votes == 2:
    confidence = avg_scores_dos_2_concordantes

# Desempate → Confiança do vencedor (penalizada)
else:
    confidence = max_score * 0.9  # Penaliza 10%
```

---

## 💻 Implementação

**Script:**`scripts/sentiment_ensemble.py`

### Execução

```python
import subprocess

print("🎯 Criando ensemble dos 3 modelos...")
print("📊 Estratégia: Majority Voting + Weighted Tiebreak")
print("⏱️  Tempo estimado: < 1 minuto (combina resultados existentes)\n")

# Executa script
result = subprocess.run(['python', 'scripts/sentiment_ensemble.py'])

if result.returncode == 0:
    print("\n✅ Ensemble criado com sucesso!")
    print(f"📁 Arquivo atualizado: messages_with_models.parquet")
    print(f"📁 Metadata gerado: sentiment_ensemble_metadata.json")
else:
    print("\n❌ Erro na execução. Verifique os logs acima.")
```

**Ou via terminal:**

```bash
python scripts/sentiment_ensemble.py
```

---

## 📊 Resultados

Note 📝 Nota

Os resultados serão exibidos aqui após executar o script `sentiment_ensemble.py`. Execute primeiro os 3 modelos individuais e depois o ensemble.

```python
### 📊 Estatísticas do Ensemble
```

| Mensagens processadas | 61,482 |
| --- | --- |
| Consenso total (3 votos) | 4,223 (6.9%) |
| Maioria (2 votos) | 48,962 (79.6%) |
| Desacordo total (1 voto) | 8,297 (13.5%) |
| Confiança média | 0.702 |

```python
### 📈 Distribuição do Ensemble
```

| 😐 Neutral | 35,837 | 58.3% |
| --- | --- | --- |
| 😊 Positive | 16,534 | 26.9% |
| 😢 Negative | 9,111 | 14.8% |

```python
### 🏆 Ensemble vs Modelos Individuais
```

| Twitter-RoBERTa | 88.2% | 0.659 |
| --- | --- | --- |
| DistilBERT | 40.8% | 0.553 |
| RoBERTa Latest | 64.4% | 0.775 |
| \*\*Ensemble\*\* | 100.0% | \*\*0.702\*\* |

```python
**Observação:** Concordância indica % de mensagens onde cada modelo concorda com o ensemble.
```

```python
#### ✅ Consenso Total (3 votos)

*Todos os modelos concordam - máxima confiabilidade*
```

| Total tá, não por pessoa | neutral | 0.699 |
| --- | --- | --- |
| ou eu pago e não vou | neutral | 0.609 |
| hahaah | positive | 0.534 |
| Eu vi mas nem lembro mais kkkkk tenho que ver de novo | neutral | 0.659 |
| Claro que não importo | neutral | 0.600 |

```python
#### 🤝 Maioria (2 votos)

*Dois modelos concordam, um discorda*
```

| https://www.localiza.com/brasil/pt-br/reservas/passo-2 | neutral | 0.898 | neutral | positive | neutral |
| --- | --- | --- | --- | --- | --- |
| Arrasou | positive | 0.538 | positive | positive | neutral |
| confortável | neutral | 0.550 | neutral | positive | neutral |
| esse vai de boas | positive | 0.868 | positive | positive | neutral |
| Tem um outro lá tbm mas mesmo preco | neutral | 0.833 | neutral | positive | neutral |

```python
#### ⚠️ Desacordo Total (1 voto cada)

*Cada modelo escolheu diferente - ambiguidade genuína*
```

| É tudo igual | neutral | 0.788 | negative | positive | neutral |
| --- | --- | --- | --- | --- | --- |
| 4 mil é muito | neutral | 0.773 | negative | positive | neutral |
| Mas sim, ainda caro | neutral | 0.798 | negative | positive | neutral |
| Saquei | neutral | 0.674 | negative | positive | neutral |
| Caralho de corretor | negative | 0.795 | negative | positive | neutral |

---

## 💭 Interpretação

Tip 🎯 Por Que o Ensemble Funciona?

**1\. Wisdom of Crowds (Sabedoria das Multidões)**

Múltiplas opiniões independentes tendem a ser mais precisas que uma única opinião, mesmo de especialista.

**2\. Redução de Viés**

Cada modelo tem viés diferente: - RoBERTa: Conservador → neutral - DistilBERT: Polarizador → positive/negative - Latest: Ultra conservador → neutral

Ensemble equilibra esses vieses.

**3\. Confidence Calibration**

- **Alta concordância** = Alta confiança (genuinamente claro)
- **Baixa concordância** = Baixa confiança (genuinamente ambíguo)

**4\. Performance Empírica**

Ensemble geralmente supera qualquer modelo individual em métricas como: - Accuracy - F1-Score - Calibração de confiança

---

### 📊 Níveis de Confiança

**🟢 Alta Confiança (3 votos - ~60% das mensagens)** - Todos os modelos concordam - Confiança > 0.70 - **Uso:** Análises estatísticas robustas

**🟡 Média Confiança (2 votos - ~35% das mensagens)** - Maioria concorda - Confiança 0.50-0.70 - **Uso:** Análises gerais, tendências

**🔴 Baixa Confiança (1 voto - ~5% das mensagens)** - Todos discordam - Confiança < 0.50 - **Uso:** Análise qualitativa, contexto adicional necessário

---

### 🎯 Recomendações de Uso

**Para Análise Exploratória (EDA):**

```python
# Use ensemble como classificação principal
df['sentimento_final'] = df['sentimento_ensemble_label']

# Filtre por confiança quando precisar
df_confiaveis = df[df['sentimento_ensemble_confidence'] > 0.7]
df_ambiguos = df[df['sentimento_ensemble_confidence'] < 0.5]
```

**Para Análises Estatísticas:**

```python
# Use apenas mensagens com consenso total
df_robusto = df[df['sentimento_ensemble_votes'] == 3]

# Garante máxima confiabilidade
```

**Para Identificar Padrões:**

```python
# Cruza confiança com outras features
df.groupby(['sentimento_ensemble_votes', 'periodo_dia']).size()

# Ambiguidade aumenta em certos contextos?
```

---

## 💡 Guia Prático: Como Usar no EDA

### Exemplo 1: Timeline Emocional

```python
# Usa ensemble para timeline mais robusta
df_timeline = df.groupby([
    pd.Grouper(key='timestamp', freq='D'),
    'sentimento_ensemble_label'
]).size().unstack(fill_value=0)

# Só mensagens confiáveis (opcional)
df_timeline_confiaveis = df[
    df['sentimento_ensemble_confidence'] > 0.7
].groupby([
    pd.Grouper(key='timestamp', freq='D'),
    'sentimento_ensemble_label'
]).size().unstack(fill_value=0)
```

### Exemplo 2: Comparação entre Remetentes

## 🔮 Validação Futura

Próximos passos para validar a performance do ensemble:

### 1\. Validação Manual

### 2\. Métricas de Performance

### 3\. Análise de Erros

---

## 📚 Referências

**Conceitos:** - Ensemble Learning - Majority Voting - Weighted Voting - Confidence Calibration

**Literatura:** - Dietterich, T. G. (2000). “Ensemble Methods in Machine Learning” - Kuncheva, L. I. (2004). “Combining Pattern Classifiers”

---

**Status:** 🚧 Aguardando implementação do script `sentiment_ensemble.py`

**Próximo passo:**[Usar ensemble no EDA](http://localhost:7860/05-eda.qmd)

---