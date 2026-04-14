# Roadmap

## Concluído

- Pipeline completo: profiling, cleaning, wrangling, feature engineering
- Sentiment analysis multi-modelo (RoBERTa, DistilBERT, DeBERTa, ensemble)
- Embeddings (mpnet, MiniLM, DistilUSE)
- EDA por dimensão (temporal, interação, conteúdo)
- Advanced analysis (clustering semântico, N-Grams, TF-IDF)
- CLI unificado (`whatsapp-interaction`) — [#3](https://github.com/mrlnlms/whatsapp-interaction-analysis/issues/3)
- Dataset sintético de exemplo — [#1](https://github.com/mrlnlms/whatsapp-interaction-analysis/issues/1)
- Reorganização do pacote Python — pacote unificado `whatsapp/`, imports absolutos, zero sys.path hacks
- Project hardening — 149 testes, schema validation, path traversal fix, exceções específicas, dependências pinadas, docs consolidados
- **Quarto website no GitHub Pages** — [#2](https://github.com/mrlnlms/whatsapp-interaction-analysis/issues/2) (13/abr/2026)
- **Camada de findings** (13/abr/2026) — 5 notebooks de síntese (07-11) cobrindo overview, dinâmica, sentimento, temas e estilos; seção "Principais Descobertas" na homepage

## Próximo

1. **DVC para dados processados** — [#4](https://github.com/mrlnlms/whatsapp-interaction-analysis/issues/4)
   Avaliar quando houver múltiplos exports — permite comparar períodos e versionar datasets.

## Follow-ups técnicos

- **Integrar transcrições** de áudio/vídeo à análise semântica
  25% das mensagens (mídia) hoje ficam de fora do clustering e do sentiment analysis porque não têm embedding. As transcrições existem em `transcriptions.csv` — precisariam ser injetadas no corpus textual antes de recalcular embeddings.

- **Modelo de sentimento em português (BERTimbau)**
  Os 3 modelos atuais foram treinados em inglês. Um modelo PT-BR validaria a estabilidade de tom encontrada nos findings (58% neutro / 27% pos / 15% neg, constante no ano).

- **Micro-histórias dos extremos**
  Examinar qualitativamente os dias de pico (ex: 22/jun/2025 com 1.288 msgs) e os vales para enriquecer a interpretação narrativa.

- **Testes de integração E2E**
  Testar pipeline completo de ponta a ponta (clean → wrangle → export) usando o dataset sample como fixture.

## Entregáveis paralelos

- **Presente pessoal** (fora do escopo deste repo) — versão narrativa dos findings sem jargão técnico, reaproveitando timeline e visualizações. Agora que a camada de análise fechou, é o próximo entregável natural — formato (single-page, PDF, slides) ainda em aberto.
