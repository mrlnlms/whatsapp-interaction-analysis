# Roadmap

## Concluído

- Pipeline completo: profiling, cleaning, wrangling, feature engineering
- Sentiment analysis multi-modelo (RoBERTa, DistilBERT, DeBERTa, ensemble)
- Embeddings (mpnet, MiniLM, DistilUSE)
- EDA por dimensão (temporal, interação, conteúdo)
- Advanced analysis (clustering semântico, N-Grams, TF-IDF)
- CLI unificado (`whatsapp-interaction`) — [#3](https://github.com/mrlnlms/whatsapp-interaction-analysis/issues/3)
- Dataset sintético de exemplo — [#1](https://github.com/mrlnlms/whatsapp-interaction-analysis/issues/1)
- **Reorganização do pacote Python** — pacote unificado `whatsapp/`, imports absolutos, zero sys.path hacks
- **Project hardening** — 147 testes (config, utils, cleaning, wrangling, CLI), schema validation, path traversal fix, exceções específicas, dependências pinadas, docs consolidados

## Próximo

1. **Quarto website no GitHub Pages** — [#2](https://github.com/mrlnlms/whatsapp-interaction-analysis/issues/2)
   Pipeline inteiro como site navegável. Já tem `_quarto.yml` e `index.qmd`. Precisa: workflow de deploy, ajustar notebooks pra renderizar com dataset sample.

## Futuro

2. **DVC para dados processados** — [#4](https://github.com/mrlnlms/whatsapp-interaction-analysis/issues/4)
   Avaliar quando houver múltiplos exports.

3. **Testes de integração E2E**
   Testar pipeline completo de ponta a ponta (clean → wrangle → export). Requer dataset sample como fixture. Não testar scripts de ML (dependem de torch/transformers).
