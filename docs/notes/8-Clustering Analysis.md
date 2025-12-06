[WhatsApp DS Analytics](http://localhost:7860/)

- [Home](http://localhost:7860/)
- [Notebooks](http://localhost:7860/notebooks/06-advanced-analysis.html#)
	- [00 - Data Discovery](http://localhost:7860/notebooks/00-data-discovery.html)
	- [00 - Data Profiling](http://localhost:7860/notebooks/00-data-profiling.html)
	- [01 - Data Cleaning](http://localhost:7860/notebooks/01-data-cleaning.html)
	- [02 - Data Wrangling](http://localhost:7860/notebooks/02-data-wrangling.html)
	- [03 - Feature Engineering](http://localhost:7860/notebooks/03-feature-engineering.html)
	- [04 - Model Features](http://localhost:7860/notebooks/04-model-features.html)
	- [05 - EDA](http://localhost:7860/notebooks/05-eda.html)
	- [06 - Advanced Analysis](http://localhost:7860/notebooks/06-advanced-analysis.html)
- [Dicionário de Dados](http://localhost:7860/docs/data-dictionary.html)1. [Data Analysis](http://localhost:7860/notebooks/04-model-features.html)
2. [Clustering Analysis](http://localhost:7860/notebooks/06-advanced-analysis.html)

- Projeto
	- [WhatsApp DS Analytics](http://localhost:7860/)
	- [Dicionário de Dados](http://localhost:7860/docs/data-dictionary.html)
- Data Preparation
	- [Data Discovery](http://localhost:7860/notebooks/00-data-discovery.html)
	- [Data Profiling](http://localhost:7860/notebooks/00-data-profiling.html)
	- [Data Cleaning](http://localhost:7860/notebooks/01-data-cleaning.html)
	- [Data Wrangling](http://localhost:7860/notebooks/02-data-wrangling.html)
	- [Feature Engineering](http://localhost:7860/notebooks/03-feature-engineering.html)
- Data Analysis
	- [Model-Based Features](http://localhost:7860/notebooks/04-model-features.html)
	- [Exploratory Data Analysis](http://localhost:7860/notebooks/05-eda.html)
	- [Clustering Analysis](http://localhost:7860/notebooks/06-advanced-analysis.html)

## On this page

- [Configuração](http://localhost:7860/notebooks/06-advanced-analysis.html#configura%C3%A7%C3%A3o)
- [Introdução](http://localhost:7860/notebooks/06-advanced-analysis.html#introdu%C3%A7%C3%A3o)
- [1\. Carregamento dos Dados](http://localhost:7860/notebooks/06-advanced-analysis.html#carregamento-dos-dados)
- [2\. Clustering Estrutural (Features Derivadas)](http://localhost:7860/notebooks/06-advanced-analysis.html#clustering-estrutural-features-derivadas)
	- [2.1 Seleção de Features](http://localhost:7860/notebooks/06-advanced-analysis.html#sele%C3%A7%C3%A3o-de-features)
	- [2.2 Determinação do Número de Clusters](http://localhost:7860/notebooks/06-advanced-analysis.html#determina%C3%A7%C3%A3o-do-n%C3%BAmero-de-clusters)
	- [2.3 Clustering Final](http://localhost:7860/notebooks/06-advanced-analysis.html#clustering-final)
	- [2.4 Distribuição dos Clusters](http://localhost:7860/notebooks/06-advanced-analysis.html#distribui%C3%A7%C3%A3o-dos-clusters)
	- [2.5 Perfil dos Clusters](http://localhost:7860/notebooks/06-advanced-analysis.html#perfil-dos-clusters)
	- [2.6 Clusters por Participante](http://localhost:7860/notebooks/06-advanced-analysis.html#clusters-por-participante)
	- [2.7 Visualização 2D (PCA)](http://localhost:7860/notebooks/06-advanced-analysis.html#visualiza%C3%A7%C3%A3o-2d-pca)
- [5\. Próximos Passos](http://localhost:7860/notebooks/06-advanced-analysis.html#pr%C3%B3ximos-passos)

1. [Data Analysis](http://localhost:7860/notebooks/04-model-features.html)
2. [Clustering Analysis](http://localhost:7860/notebooks/06-advanced-analysis.html)

# Clustering Analysis

Análise de clusters: features estruturais vs embeddings semânticos

Author

Marlon

Published

December 6, 2025

## Configuração| Dataset | Status | Uso |
| --- | --- | --- |
| `messages_enriched.parquet` | ✅ Disponível | Clustering Estrutural |
| `messages_with_models.parquet` | ✅ Disponível | Clustering Semântico |

```
⚡ Configurações de Performance:
```

| Parâmetro | Valor |
| --- | --- |
| Amostra para Elbow/Silhouette | 15,000 |
| Batch size (MiniBatchKMeans) | 1,024 |
| Chunk size (processamento) | 10,000 |

---

# Introdução

Este notebook explora **duas abordagens de clustering** para identificar padrões nas conversas:

1. **Clustering Estrutural** — Usa features numéricas derivadas (temporais, texto, conversação)
2. **Clustering Semântico** — Usa embeddings de modelos de linguagem

A comparação entre as duas abordagens revela insights complementares: - Estrutural captura **comportamento** (quando, como, quanto) - Semântico captura **conteúdo** (o que, significado)

NoteOtimização de Memória

Este notebook usa **MiniBatchKMeans** e **amostragem estratificada** para processar grandes volumes de dados sem estourar memória.

---

# 1\. Carregamento dos Dados

| Métrica | Valor |
| --- | --- |
| Mensagens | 91,924 |
| Colunas | 43 |
| Período | 19/10/2024 → 20/10/2025 |

---

# 2\. Clustering Estrutural (Features Derivadas)

Agrupa mensagens usando features numéricas criadas no Feature Engineering.

## 2.1 Seleção de Features| Categoria | Feature | Status |
| --- | --- | --- |
| Temporais | `hora` | ✅ |
| Temporais | `dia_semana_num` | ✅ |
| Temporais | `mes` | ✅ |
| Temporais | `fim_de_semana` | ✅ |
| Temporais | `horario_comercial` | ✅ |
| Texto | `tamanho_caracteres` | ✅ |
| Texto | `tamanho_palavras` | ✅ |
| Texto | `tem_emoji` | ✅ |
| Texto | `qtd_emojis` | ✅ |
| Texto | `tem_link` | ✅ |
| Texto | `tem_interrogacao` | ✅ |
| Texto | `tem_exclamacao` | ✅ |
| Texto | `eh_caixa_alta` | ✅ |
| Conversação | `tempo_desde_ultima_msg` | ✅ |
| Conversação | `eh_resposta_rapida` | ✅ |
| Conversação | `sequencia_mesmo_remetente` | ✅ |
| Conversação | `eh_inicio_conversa` | ✅ |

Features disponíveis para clustering: 17

## 2.2 Determinação do Número de Clusters```
📊 Usando amostra de 15,000 mensagens para determinar K ótimo
   (de 91,924 total - 16.3%)
```

![](http://localhost:7860/notebooks/06-advanced-analysis_files/figure-html/elbow-silhouette-output-2.png)

Método Elbow e Silhouette Score para determinar número ótimo de clusters```
📊 Melhor K pelo Silhouette Score: 10
```

## 2.3 Clustering Final| Métrica | Valor |
| --- | --- |
| Número de Clusters | 10 |
| Silhouette Score (amostra) | 0.277 |
| Interpretação | Moderado |

## 2.4 Distribuição dos Clusters 

<svg class="main-svg" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="949" height="525" style="background: white;"><defs id="defs-b7454e"><g class="clips"><clipPath id="clipb7454exyplot" class="plotclip"><rect width="901" height="454"></rect></clipPath><clipPath class="axesclip" id="clipb7454ex"><rect x="48" y="0" width="901" height="525"></rect></clipPath><clipPath class="axesclip" id="clipb7454ey"><rect x="0" y="30" width="949" height="454"></rect></clipPath><clipPath class="axesclip" id="clipb7454exy"><rect x="48" y="30" width="901" height="454"></rect></clipPath></g><g class="gradients"></g><g class="patterns"></g></defs><g class="bglayer"><rect class="bg" x="48" y="30" width="901" height="454" style="fill: rgb(229, 236, 246); fill-opacity: 1; stroke-width: 0;"></rect></g><g class="draglayer cursor-crosshair"><g class="xy"><rect class="nsewdrag drag" data-subplot="xy" x="48" y="30" width="901" height="454" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="nwdrag drag cursor-nw-resize" data-subplot="xy" x="28" y="10" width="20" height="20" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="nedrag drag cursor-ne-resize" data-subplot="xy" x="949" y="10" width="20" height="20" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="swdrag drag cursor-sw-resize" data-subplot="xy" x="28" y="484" width="20" height="20" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="sedrag drag cursor-se-resize" data-subplot="xy" x="949" y="484" width="20" height="20" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="ewdrag drag cursor-ew-resize" data-subplot="xy" x="138.10000000000002" y="484.5" width="720.8000000000001" height="20" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="wdrag drag cursor-w-resize" data-subplot="xy" x="48" y="484.5" width="90.10000000000001" height="20" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="edrag drag cursor-e-resize" data-subplot="xy" x="858.9" y="484.5" width="90.10000000000001" height="20" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="nsdrag drag cursor-ns-resize" data-subplot="xy" x="27.5" y="75.4" width="20" height="363.20000000000005" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="sdrag drag cursor-s-resize" data-subplot="xy" x="27.5" y="438.6" width="20" height="45.400000000000006" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="ndrag drag cursor-n-resize" data-subplot="xy" x="27.5" y="30" width="20" height="45.400000000000006" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect></g></g><g class="layer-below"><g class="imagelayer"></g><g class="shapelayer"></g></g><g class="cartesianlayer"><g class="subplot xy"><g class="layer-subplot"><g class="shapelayer"></g><g class="imagelayer"></g></g><g class="minor-gridlayer"><g class="x"></g><g class="y"></g></g><g class="gridlayer"><g class="x"></g><g class="y"><path class="ygrid crisp" transform="translate(0,387.69)" d="M48,0h901" style="stroke: rgb(255, 255, 255); stroke-opacity: 1; stroke-width: 1px;"></path><path class="ygrid crisp" transform="translate(0,291.39)" d="M48,0h901" style="stroke: rgb(255, 255, 255); stroke-opacity: 1; stroke-width: 1px;"></path><path class="ygrid crisp" transform="translate(0,195.08)" d="M48,0h901" style="stroke: rgb(255, 255, 255); stroke-opacity: 1; stroke-width: 1px;"></path><path class="ygrid crisp" transform="translate(0,98.77)" d="M48,0h901" style="stroke: rgb(255, 255, 255); stroke-opacity: 1; stroke-width: 1px;"></path></g></g><g class="zerolinelayer"><path class="yzl zl crisp" transform="translate(0,484)" d="M48,0h901" style="stroke: rgb(255, 255, 255); stroke-opacity: 1; stroke-width: 2px;"></path></g><g class="layer-between"><g class="shapelayer"></g><g class="imagelayer"></g></g><path class="xlines-below"></path><path class="ylines-below"></path><g class="overlines-below"></g><g class="xaxislayer-below"></g><g class="yaxislayer-below"></g><g class="overaxes-below"></g><g class="overplot"><g class="xy" transform="translate(48,30)" clip-path="url(#clipb7454exyplot)"><g class="barlayer mlayer"><g class="trace bars" style="opacity: 1;"><g class="points"><g class="point"><path d="M9.01,454V162.61H81.09V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(102, 194, 165); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><g class="trace bars" style="opacity: 1;"><g class="points"><g class="point"><path d="M99.11,454V101.29H171.19V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(252, 141, 98); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><g class="trace bars" style="opacity: 1;"><g class="points"><g class="point"><path d="M189.21,454V134.36H261.29V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(141, 160, 203); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><g class="trace bars" style="opacity: 1;"><g class="points"><g class="point"><path d="M279.31,454V432H351.39V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(231, 138, 195); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><g class="trace bars" style="opacity: 1;"><g class="points"><g class="point"><path d="M369.41,454V443.31H441.49V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(166, 216, 84); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><g class="trace bars" style="opacity: 1;"><g class="points"><g class="point"><path d="M459.51,454V414.44H531.59V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(255, 217, 47); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><g class="trace bars" style="opacity: 1;"><g class="points"><g class="point"><path d="M549.61,454V286.1H621.69V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(229, 196, 148); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><g class="trace bars" style="opacity: 1;"><g class="points"><g class="point"><path d="M639.71,454V360.89H711.79V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(179, 179, 179); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><g class="trace bars" style="opacity: 1;"><g class="points"><g class="point"><path d="M729.81,454V22.7H801.89V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(102, 194, 165); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><g class="trace bars" style="opacity: 1;"><g class="points"><g class="point"><path d="M819.91,454V411.72H891.99V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(252, 141, 98); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g></g></g></g><g class="zerolinelayer-above"></g><path class="xlines-above crisp" d="M0,0" style="fill: none;"></path><path class="ylines-above crisp" d="M0,0" style="fill: none;"></path><g class="overlines-above"></g><g class="xaxislayer-above"><g class="xtick"><text text-anchor="middle" x="0" y="497" data-unformatted="0" data-math="N" transform="translate(93.05,0)" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">0</text></g><g class="xtick"><text text-anchor="middle" x="0" y="497" data-unformatted="1" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(183.15,0)">1</text></g><g class="xtick"><text text-anchor="middle" x="0" y="497" data-unformatted="2" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(273.25,0)">2</text></g><g class="xtick"><text text-anchor="middle" x="0" y="497" data-unformatted="3" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(363.35,0)">3</text></g><g class="xtick"><text text-anchor="middle" x="0" y="497" data-unformatted="4" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(453.45,0)">4</text></g><g class="xtick"><text text-anchor="middle" x="0" y="497" data-unformatted="5" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(543.55,0)">5</text></g><g class="xtick"><text text-anchor="middle" x="0" y="497" data-unformatted="6" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(633.65,0)">6</text></g><g class="xtick"><text text-anchor="middle" x="0" y="497" data-unformatted="7" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(723.75,0)">7</text></g><g class="xtick"><text text-anchor="middle" x="0" y="497" data-unformatted="8" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(813.85,0)">8</text></g><g class="xtick"><text text-anchor="middle" x="0" y="497" data-unformatted="9" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(903.95,0)">9</text></g></g><g class="yaxislayer-above"><g class="ytick"><text text-anchor="end" x="47" y="4.199999999999999" data-unformatted="0" data-math="N" transform="translate(0,484)" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">0</text></g><g class="ytick"><text text-anchor="end" x="47" y="4.199999999999999" data-unformatted="5k" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(0,387.69)">5k</text></g><g class="ytick"><text text-anchor="end" x="47" y="4.199999999999999" data-unformatted="10k" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(0,291.39)">10k</text></g><g class="ytick"><text text-anchor="end" x="47" y="4.199999999999999" data-unformatted="15k" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(0,195.08)">15k</text></g><g class="ytick"><text text-anchor="end" x="47" y="4.199999999999999" data-unformatted="20k" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(0,98.77)">20k</text></g></g><g class="overaxes-above"></g></g></g><g class="polarlayer"></g><g class="smithlayer"></g><g class="ternarylayer"></g><g class="geolayer"></g><g class="funnelarealayer"></g><g class="pielayer"></g><g class="iciclelayer"></g><g class="treemaplayer"></g><g class="sunburstlayer"></g><g class="glimages"></g></svg>

<svg class="main-svg" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="949" height="525"><defs id="topdefs-b7454e"><g class="clips"></g></defs><g class="indicatorlayer"></g><g class="layer-above"><g class="imagelayer"></g><g class="shapelayer"></g></g><g class="selectionlayer"></g><g class="infolayer"><g class="g-gtitle"><text class="gtitle" x="47.45" y="15" text-anchor="start" dy="0em" data-unformatted="Distribuição por Cluster Estrutural" data-math="N" style="opacity: 1; font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 17px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">Distribuição por Cluster Estrutural</text></g><g class="g-xtitle" transform="translate(0,-2.2999999999999545)"><text class="xtitle" x="498.5" y="524.3" text-anchor="middle" data-unformatted="Cluster" data-math="N" style="opacity: 1; font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 14px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">Cluster</text></g><g class="g-ytitle" transform="translate(8.759765625,0)"><text class="ytitle" transform="rotate(-90,5.240625000000001,257)" x="5.240625000000001" y="257" text-anchor="middle" data-unformatted="Quantidade de Mensagens" data-math="N" style="opacity: 1; font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 14px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">Quantidade de Mensagens</text></g></g><g class="menulayer"></g><g class="zoomlayer"></g></svg>

[<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 132 132" height="1em" width="1em"><title>plotly-logomark</title><g id="symbol"><rect fill="#000" x="0" y="0" width="132" height="132" rx="18" ry="18"></rect><circle fill="#9EF" cx="102" cy="30" r="6"></circle><circle fill="#BAC" cx="78" cy="30" r="6"></circle><circle fill="#BAC" cx="78" cy="54" r="6"></circle><circle fill="#D69" cx="54" cy="30" r="6"></circle><circle fill="#F26" cx="30" cy="30" r="6"></circle><circle fill="#F26" cx="30" cy="54" r="6"></circle><path fill="#FFF" d="M30,72a6,6,0,0,0-6,6v24a6,6,0,0,0,12,0V78A6,6,0,0,0,30,72Z"></path><path fill="#FFF" d="M78,72a6,6,0,0,0-6,6v24a6,6,0,0,0,12,0V78A6,6,0,0,0,78,72Z"></path><path fill="#FFF" d="M54,48a6,6,0,0,0-6,6v48a6,6,0,0,0,12,0V54A6,6,0,0,0,54,48Z"></path><path fill="#FFF" d="M102,48a6,6,0,0,0-6,6v48a6,6,0,0,0,12,0V54A6,6,0,0,0,102,48Z"></path></g></svg>](https://plotly.com/)

Distribuição de mensagens por cluster estrutural

## 2.5 Perfil dos Clusters![](http://localhost:7860/notebooks/06-advanced-analysis_files/figure-html/cluster-profiles-output-1.png)

Perfil médio normalizado de cada cluster```
📋 **Interpretação dos Clusters:**

**Cluster 0** (15,128 mensagens)
  📈 Características altas: horario_comercial, eh_resposta_rapida, tem_emoji
  📉 Características baixas: mes, fim_de_semana, dia_semana_num

**Cluster 1** (18,312 mensagens)
  📈 Características altas: horario_comercial, mes, eh_resposta_rapida
  📉 Características baixas: hora, fim_de_semana, dia_semana_num

**Cluster 2** (16,595 mensagens)
  📈 Características altas: hora, eh_resposta_rapida, mes
  📉 Características baixas: horario_comercial, fim_de_semana, dia_semana_num

**Cluster 3** (1,142 mensagens)
  📈 Características altas: eh_inicio_conversa, tempo_desde_ultima_msg, tem_exclamacao
  📉 Características baixas: eh_resposta_rapida, hora, sequencia_mesmo_remetente

**Cluster 4** (555 mensagens)
  📈 Características altas: tem_link, tamanho_caracteres, eh_inicio_conversa
  📉 Características baixas: eh_resposta_rapida, tem_interrogacao, eh_caixa_alta

**Cluster 5** (2,054 mensagens)
  📈 Características altas: eh_caixa_alta, horario_comercial, eh_resposta_rapida
  📉 Características baixas: mes, tem_interrogacao, sequencia_mesmo_remetente

**Cluster 6** (8,717 mensagens)
  📈 Características altas: horario_comercial, mes, tamanho_palavras
  📉 Características baixas: eh_resposta_rapida, fim_de_semana, dia_semana_num

**Cluster 7** (4,834 mensagens)
  📈 Características altas: tem_interrogacao, tamanho_palavras, tamanho_caracteres
  📉 Características baixas: tem_emoji, tem_exclamacao, eh_caixa_alta

**Cluster 8** (22,392 mensagens)
  📈 Características altas: dia_semana_num, fim_de_semana, mes
  📉 Características baixas: horario_comercial, tem_interrogacao, tem_exclamacao

**Cluster 9** (2,195 mensagens)
  📈 Características altas: tem_exclamacao, horario_comercial, mes
  📉 Características baixas: hora, tem_interrogacao, tem_emoji
```

## 2.6 Clusters por Participante 

<svg class="main-svg" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="949" height="525" style="background: white;"><defs id="defs-fae16c"><g class="clips"><clipPath id="clipfae16cxyplot" class="plotclip"><rect width="837" height="454"></rect></clipPath><clipPath class="axesclip" id="clipfae16cx"><rect x="41" y="0" width="837" height="525"></rect></clipPath><clipPath class="axesclip" id="clipfae16cy"><rect x="0" y="30" width="949" height="454"></rect></clipPath><clipPath class="axesclip" id="clipfae16cxy"><rect x="41" y="30" width="837" height="454"></rect></clipPath></g><g class="gradients"></g><g class="patterns"></g></defs><g class="bglayer"><rect class="bg" x="41" y="30" width="837" height="454" style="fill: rgb(229, 236, 246); fill-opacity: 1; stroke-width: 0;"></rect></g><g class="draglayer cursor-crosshair"><g class="xy"><rect class="nsewdrag drag" data-subplot="xy" x="41" y="30" width="837" height="454" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="nwdrag drag cursor-nw-resize" data-subplot="xy" x="21" y="10" width="20" height="20" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="nedrag drag cursor-ne-resize" data-subplot="xy" x="878" y="10" width="20" height="20" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="swdrag drag cursor-sw-resize" data-subplot="xy" x="21" y="484" width="20" height="20" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="sedrag drag cursor-se-resize" data-subplot="xy" x="878" y="484" width="20" height="20" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="ewdrag drag cursor-ew-resize" data-subplot="xy" x="124.7" y="484.5" width="669.6" height="20" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="wdrag drag cursor-w-resize" data-subplot="xy" x="41" y="484.5" width="83.7" height="20" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="edrag drag cursor-e-resize" data-subplot="xy" x="794.3000000000001" y="484.5" width="83.7" height="20" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="nsdrag drag cursor-ns-resize" data-subplot="xy" x="20.5" y="75.4" width="20" height="363.20000000000005" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="sdrag drag cursor-s-resize" data-subplot="xy" x="20.5" y="438.6" width="20" height="45.400000000000006" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="ndrag drag cursor-n-resize" data-subplot="xy" x="20.5" y="30" width="20" height="45.400000000000006" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect></g></g><g class="layer-below"><g class="imagelayer"></g><g class="shapelayer"></g></g><g class="cartesianlayer"><g class="subplot xy"><g class="layer-subplot"><g class="shapelayer"></g><g class="imagelayer"></g></g><g class="minor-gridlayer"><g class="x"></g><g class="y"></g></g><g class="gridlayer"><g class="x"></g><g class="y"><path class="ygrid crisp" transform="translate(0,395.99)" d="M41,0h837" style="stroke: rgb(255, 255, 255); stroke-opacity: 1; stroke-width: 1px;"></path><path class="ygrid crisp" transform="translate(0,307.99)" d="M41,0h837" style="stroke: rgb(255, 255, 255); stroke-opacity: 1; stroke-width: 1px;"></path><path class="ygrid crisp" transform="translate(0,219.98)" d="M41,0h837" style="stroke: rgb(255, 255, 255); stroke-opacity: 1; stroke-width: 1px;"></path><path class="ygrid crisp" transform="translate(0,131.98000000000002)" d="M41,0h837" style="stroke: rgb(255, 255, 255); stroke-opacity: 1; stroke-width: 1px;"></path><path class="ygrid crisp" transform="translate(0,43.97)" d="M41,0h837" style="stroke: rgb(255, 255, 255); stroke-opacity: 1; stroke-width: 1px;"></path></g></g><g class="zerolinelayer"><path class="yzl zl crisp" transform="translate(0,484)" d="M41,0h837" style="stroke: rgb(255, 255, 255); stroke-opacity: 1; stroke-width: 2px;"></path></g><g class="layer-between"><g class="shapelayer"></g><g class="imagelayer"></g></g><path class="xlines-below"></path><path class="ylines-below"></path><g class="overlines-below"></g><g class="xaxislayer-below"></g><g class="yaxislayer-below"></g><g class="overaxes-below"></g><g class="overplot"><g class="xy" transform="translate(41,30)" clip-path="url(#clipfae16cxyplot)"><g class="barlayer mlayer"><g class="trace bars" style="opacity: 1;"><g class="points"><g class="point"><path d="M41.85,454V155.76H75.33V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(102, 194, 165); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g><g class="point"><path d="M460.35,454V173.29H493.83V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(102, 194, 165); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><g class="trace bars" style="opacity: 1;"><g class="points"><g class="point"><path d="M75.33,454V87.38H108.81V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(252, 141, 98); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g><g class="point"><path d="M493.83,454V120.07H527.31V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(252, 141, 98); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><g class="trace bars" style="opacity: 1;"><g class="points"><g class="point"><path d="M108.81,454V132.74H142.29V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(141, 160, 203); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g><g class="point"><path d="M527.31,454V139.91H560.79V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(141, 160, 203); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><g class="trace bars" style="opacity: 1;"><g class="points"><g class="point"><path d="M142.29,454V432.71H175.77V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(231, 138, 195); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g><g class="point"><path d="M560.79,454V431.54H594.27V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(231, 138, 195); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><g class="trace bars" style="opacity: 1;"><g class="points"><g class="point"><path d="M175.77,454V441.63H209.25V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(166, 216, 84); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g><g class="point"><path d="M594.27,454V445.19H627.75V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(166, 216, 84); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><g class="trace bars" style="opacity: 1;"><g class="points"><g class="point"><path d="M209.25,454V418.12H242.73V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(255, 217, 47); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g><g class="point"><path d="M627.75,454V411.07H661.23V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(255, 217, 47); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><g class="trace bars" style="opacity: 1;"><g class="points"><g class="point"><path d="M242.73,454V289.64H276.21V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(229, 196, 148); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g><g class="point"><path d="M661.23,454V284.43H694.71V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(229, 196, 148); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><g class="trace bars" style="opacity: 1;"><g class="points"><g class="point"><path d="M276.21,454V358.14H309.69V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(179, 179, 179); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g><g class="point"><path d="M694.71,454V364.89H728.19V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(179, 179, 179); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><g class="trace bars" style="opacity: 1;"><g class="points"><g class="point"><path d="M309.69,454V27.69H343.17V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(102, 194, 165); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g><g class="point"><path d="M728.19,454V22.7H761.67V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(102, 194, 165); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><g class="trace bars" style="opacity: 1;"><g class="points"><g class="point"><path d="M343.17,454V436.08H376.65V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(252, 141, 98); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g><g class="point"><path d="M761.67,454V386.81H795.15V454Z" style="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0.5px; fill: rgb(252, 141, 98); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g></g></g></g><g class="zerolinelayer-above"></g><path class="xlines-above crisp" d="M0,0" style="fill: none;"></path><path class="ylines-above crisp" d="M0,0" style="fill: none;"></path><g class="overlines-above"></g><g class="xaxislayer-above"><g class="xtick"><text text-anchor="middle" x="0" y="497" data-unformatted="P1" data-math="N" transform="translate(250.25,0)" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">P1</text></g><g class="xtick"><text text-anchor="middle" x="0" y="497" data-unformatted="P2" data-math="N" transform="translate(668.75,0)" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">P2</text></g></g><g class="yaxislayer-above"><g class="ytick"><text text-anchor="end" x="40" y="4.199999999999999" data-unformatted="0" data-math="N" transform="translate(0,484)" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">0</text></g><g class="ytick"><text text-anchor="end" x="40" y="4.199999999999999" data-unformatted="5" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(0,395.99)">5</text></g><g class="ytick"><text text-anchor="end" x="40" y="4.199999999999999" data-unformatted="10" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(0,307.99)">10</text></g><g class="ytick"><text text-anchor="end" x="40" y="4.199999999999999" data-unformatted="15" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(0,219.98)">15</text></g><g class="ytick"><text text-anchor="end" x="40" y="4.199999999999999" data-unformatted="20" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(0,131.98000000000002)">20</text></g><g class="ytick"><text text-anchor="end" x="40" y="4.199999999999999" data-unformatted="25" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(0,43.97)">25</text></g></g><g class="overaxes-above"></g></g></g><g class="polarlayer"></g><g class="smithlayer"></g><g class="ternarylayer"></g><g class="geolayer"></g><g class="funnelarealayer"></g><g class="pielayer"></g><g class="iciclelayer"></g><g class="treemaplayer"></g><g class="sunburstlayer"></g><g class="glimages"></g></svg>

<svg class="main-svg" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="949" height="525"><defs id="topdefs-fae16c"><g class="clips"></g><clipPath id="legendfae16c"><rect width="54" height="219" x="0" y="0"></rect></clipPath></defs><g class="indicatorlayer"></g><g class="layer-above"><g class="imagelayer"></g><g class="shapelayer"></g></g><g class="selectionlayer"></g><g class="infolayer"><g class="legend" pointer-events="all" transform="translate(894.74,30)"><rect class="bg" shape-rendering="crispEdges" style="stroke: rgb(68, 68, 68); stroke-opacity: 1; fill: rgb(255, 255, 255); fill-opacity: 1; stroke-width: 0px;" width="54" height="219" x="0" y="0"></rect><g class="scrollbox" transform="" clip-path="url(#legendfae16c)"><text class="legendtitletext" text-anchor="start" data-unformatted="Cluster" data-math="N" x="2" y="18.2" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 14px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">Cluster</text><g class="groups" transform=""><g class="traces" transform="translate(0,32.7)" style="opacity: 1;"><text class="legendtext" text-anchor="start" x="40" y="4.680000000000001" data-unformatted="0" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">0</text><g class="layers" style="opacity: 1;"><g class="legendfill"></g><g class="legendlines"></g><g class="legendsymbols"><g class="legendpoints"><path class="legendundefined" d="M6,6H-6V-6H6Z" transform="translate(20,0)" style="stroke-width: 0.5px; fill: rgb(102, 194, 165); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><rect class="legendtoggle" pointer-events="all" x="0" y="-9.5" width="47.640625" height="19" style="cursor: pointer; fill: rgb(0, 0, 0); fill-opacity: 0;"></rect></g></g><g class="groups" transform=""><g class="traces" transform="translate(0,51.7)" style="opacity: 1;"><text class="legendtext" text-anchor="start" x="40" y="4.680000000000001" data-unformatted="1" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">1</text><g class="layers" style="opacity: 1;"><g class="legendfill"></g><g class="legendlines"></g><g class="legendsymbols"><g class="legendpoints"><path class="legendundefined" d="M6,6H-6V-6H6Z" transform="translate(20,0)" style="stroke-width: 0.5px; fill: rgb(252, 141, 98); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><rect class="legendtoggle" pointer-events="all" x="0" y="-9.5" width="47.640625" height="19" style="cursor: pointer; fill: rgb(0, 0, 0); fill-opacity: 0;"></rect></g></g><g class="groups" transform=""><g class="traces" transform="translate(0,70.7)" style="opacity: 1;"><text class="legendtext" text-anchor="start" x="40" y="4.680000000000001" data-unformatted="2" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">2</text><g class="layers" style="opacity: 1;"><g class="legendfill"></g><g class="legendlines"></g><g class="legendsymbols"><g class="legendpoints"><path class="legendundefined" d="M6,6H-6V-6H6Z" transform="translate(20,0)" style="stroke-width: 0.5px; fill: rgb(141, 160, 203); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><rect class="legendtoggle" pointer-events="all" x="0" y="-9.5" width="47.640625" height="19" style="cursor: pointer; fill: rgb(0, 0, 0); fill-opacity: 0;"></rect></g></g><g class="groups" transform=""><g class="traces" transform="translate(0,89.7)" style="opacity: 1;"><text class="legendtext" text-anchor="start" x="40" y="4.680000000000001" data-unformatted="3" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">3</text><g class="layers" style="opacity: 1;"><g class="legendfill"></g><g class="legendlines"></g><g class="legendsymbols"><g class="legendpoints"><path class="legendundefined" d="M6,6H-6V-6H6Z" transform="translate(20,0)" style="stroke-width: 0.5px; fill: rgb(231, 138, 195); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><rect class="legendtoggle" pointer-events="all" x="0" y="-9.5" width="47.640625" height="19" style="cursor: pointer; fill: rgb(0, 0, 0); fill-opacity: 0;"></rect></g></g><g class="groups" transform=""><g class="traces" transform="translate(0,108.7)" style="opacity: 1;"><text class="legendtext" text-anchor="start" x="40" y="4.680000000000001" data-unformatted="4" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">4</text><g class="layers" style="opacity: 1;"><g class="legendfill"></g><g class="legendlines"></g><g class="legendsymbols"><g class="legendpoints"><path class="legendundefined" d="M6,6H-6V-6H6Z" transform="translate(20,0)" style="stroke-width: 0.5px; fill: rgb(166, 216, 84); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><rect class="legendtoggle" pointer-events="all" x="0" y="-9.5" width="47.640625" height="19" style="cursor: pointer; fill: rgb(0, 0, 0); fill-opacity: 0;"></rect></g></g><g class="groups" transform=""><g class="traces" transform="translate(0,127.7)" style="opacity: 1;"><text class="legendtext" text-anchor="start" x="40" y="4.680000000000001" data-unformatted="5" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">5</text><g class="layers" style="opacity: 1;"><g class="legendfill"></g><g class="legendlines"></g><g class="legendsymbols"><g class="legendpoints"><path class="legendundefined" d="M6,6H-6V-6H6Z" transform="translate(20,0)" style="stroke-width: 0.5px; fill: rgb(255, 217, 47); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><rect class="legendtoggle" pointer-events="all" x="0" y="-9.5" width="47.640625" height="19" style="cursor: pointer; fill: rgb(0, 0, 0); fill-opacity: 0;"></rect></g></g><g class="groups" transform=""><g class="traces" transform="translate(0,146.7)" style="opacity: 1;"><text class="legendtext" text-anchor="start" x="40" y="4.680000000000001" data-unformatted="6" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">6</text><g class="layers" style="opacity: 1;"><g class="legendfill"></g><g class="legendlines"></g><g class="legendsymbols"><g class="legendpoints"><path class="legendundefined" d="M6,6H-6V-6H6Z" transform="translate(20,0)" style="stroke-width: 0.5px; fill: rgb(229, 196, 148); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><rect class="legendtoggle" pointer-events="all" x="0" y="-9.5" width="47.640625" height="19" style="cursor: pointer; fill: rgb(0, 0, 0); fill-opacity: 0;"></rect></g></g><g class="groups" transform=""><g class="traces" transform="translate(0,165.7)" style="opacity: 1;"><text class="legendtext" text-anchor="start" x="40" y="4.680000000000001" data-unformatted="7" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">7</text><g class="layers" style="opacity: 1;"><g class="legendfill"></g><g class="legendlines"></g><g class="legendsymbols"><g class="legendpoints"><path class="legendundefined" d="M6,6H-6V-6H6Z" transform="translate(20,0)" style="stroke-width: 0.5px; fill: rgb(179, 179, 179); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><rect class="legendtoggle" pointer-events="all" x="0" y="-9.5" width="47.640625" height="19" style="cursor: pointer; fill: rgb(0, 0, 0); fill-opacity: 0;"></rect></g></g><g class="groups" transform=""><g class="traces" transform="translate(0,184.7)" style="opacity: 1;"><text class="legendtext" text-anchor="start" x="40" y="4.680000000000001" data-unformatted="8" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">8</text><g class="layers" style="opacity: 1;"><g class="legendfill"></g><g class="legendlines"></g><g class="legendsymbols"><g class="legendpoints"><path class="legendundefined" d="M6,6H-6V-6H6Z" transform="translate(20,0)" style="stroke-width: 0.5px; fill: rgb(102, 194, 165); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><rect class="legendtoggle" pointer-events="all" x="0" y="-9.5" width="47.640625" height="19" style="cursor: pointer; fill: rgb(0, 0, 0); fill-opacity: 0;"></rect></g></g><g class="groups" transform=""><g class="traces" transform="translate(0,203.7)" style="opacity: 1;"><text class="legendtext" text-anchor="start" x="40" y="4.680000000000001" data-unformatted="9" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">9</text><g class="layers" style="opacity: 1;"><g class="legendfill"></g><g class="legendlines"></g><g class="legendsymbols"><g class="legendpoints"><path class="legendundefined" d="M6,6H-6V-6H6Z" transform="translate(20,0)" style="stroke-width: 0.5px; fill: rgb(252, 141, 98); fill-opacity: 1; stroke: rgb(229, 236, 246); stroke-opacity: 1;"></path></g></g></g><rect class="legendtoggle" pointer-events="all" x="0" y="-9.5" width="47.640625" height="19" style="cursor: pointer; fill: rgb(0, 0, 0); fill-opacity: 0;"></rect></g></g></g><rect class="scrollbar" rx="20" ry="3" width="0" height="0" style="fill: rgb(128, 139, 164); fill-opacity: 1;" x="0" y="0"></rect></g><g class="g-gtitle"><text class="gtitle" x="47.45" y="15" text-anchor="start" dy="0em" data-unformatted="Distribuição de Clusters por Participante (%)" data-math="N" style="opacity: 1; font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 17px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">Distribuição de Clusters por Participante (%)</text></g><g class="g-xtitle" transform="translate(0,-2.2999999999999545)"><text class="xtitle" x="459.5" y="524.3" text-anchor="middle" data-unformatted="remetente" data-math="N" style="opacity: 1; font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 14px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">remetente</text></g><g class="g-ytitle" transform="translate(8.666015625,0)"><text class="ytitle" transform="rotate(-90,5.334375000000001,257)" x="5.334375000000001" y="257" text-anchor="middle" data-unformatted="% das Mensagens" data-math="N" style="opacity: 1; font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 14px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">% das Mensagens</text></g></g><g class="menulayer"></g><g class="zoomlayer"></g></svg>

[<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 132 132" height="1em" width="1em"><title>plotly-logomark</title><g id="symbol"><rect fill="#000" x="0" y="0" width="132" height="132" rx="18" ry="18"></rect><circle fill="#9EF" cx="102" cy="30" r="6"></circle><circle fill="#BAC" cx="78" cy="30" r="6"></circle><circle fill="#BAC" cx="78" cy="54" r="6"></circle><circle fill="#D69" cx="54" cy="30" r="6"></circle><circle fill="#F26" cx="30" cy="30" r="6"></circle><circle fill="#F26" cx="30" cy="54" r="6"></circle><path fill="#FFF" d="M30,72a6,6,0,0,0-6,6v24a6,6,0,0,0,12,0V78A6,6,0,0,0,30,72Z"></path><path fill="#FFF" d="M78,72a6,6,0,0,0-6,6v24a6,6,0,0,0,12,0V78A6,6,0,0,0,78,72Z"></path><path fill="#FFF" d="M54,48a6,6,0,0,0-6,6v48a6,6,0,0,0,12,0V54A6,6,0,0,0,54,48Z"></path><path fill="#FFF" d="M102,48a6,6,0,0,0-6,6v48a6,6,0,0,0,12,0V54A6,6,0,0,0,102,48Z"></path></g></svg>](https://plotly.com/)

Distribuição de clusters por participante

## 2.7 Visualização 2D (PCA) 

<svg class="main-svg" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="949" height="525" style="background: white;"><defs id="defs-8aa229"><g class="clips"><clipPath id="clip8aa229xyplot" class="plotclip"><rect width="835" height="454"></rect></clipPath><clipPath class="axesclip" id="clip8aa229x"><rect x="43" y="0" width="835" height="525"></rect></clipPath><clipPath class="axesclip" id="clip8aa229y"><rect x="0" y="30" width="949" height="454"></rect></clipPath><clipPath class="axesclip" id="clip8aa229xy"><rect x="43" y="30" width="835" height="454"></rect></clipPath></g><g class="gradients"></g><g class="patterns"></g></defs><g class="bglayer"><rect class="bg" x="43" y="30" width="835" height="454" style="fill: rgb(229, 236, 246); fill-opacity: 1; stroke-width: 0;"></rect></g><g class="draglayer cursor-crosshair"><g class="xy"><rect class="nsewdrag drag" data-subplot="xy" x="43" y="30" width="835" height="454" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="nwdrag drag cursor-nw-resize" data-subplot="xy" x="23" y="10" width="20" height="20" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="nedrag drag cursor-ne-resize" data-subplot="xy" x="878" y="10" width="20" height="20" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="swdrag drag cursor-sw-resize" data-subplot="xy" x="23" y="484" width="20" height="20" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="sedrag drag cursor-se-resize" data-subplot="xy" x="878" y="484" width="20" height="20" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="ewdrag drag cursor-ew-resize" data-subplot="xy" x="126.5" y="484.5" width="668" height="20" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="wdrag drag cursor-w-resize" data-subplot="xy" x="43" y="484.5" width="83.5" height="20" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="edrag drag cursor-e-resize" data-subplot="xy" x="794.5" y="484.5" width="83.5" height="20" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="nsdrag drag cursor-ns-resize" data-subplot="xy" x="22.5" y="75.4" width="20" height="363.20000000000005" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="sdrag drag cursor-s-resize" data-subplot="xy" x="22.5" y="438.6" width="20" height="45.400000000000006" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect><rect class="ndrag drag cursor-n-resize" data-subplot="xy" x="22.5" y="30" width="20" height="45.400000000000006" style="fill: transparent; stroke-width: 0; pointer-events: all;"></rect></g></g><g class="layer-below"><g class="imagelayer"></g><g class="shapelayer"></g></g><g class="cartesianlayer"><g class="subplot xy"><g class="layer-subplot"><g class="shapelayer"></g><g class="imagelayer"></g></g><g class="minor-gridlayer"><g class="x"></g><g class="y"></g></g><g class="gridlayer"><g class="x"><path class="xgrid crisp" transform="translate(145.66,0)" d="M0,30v454" style="stroke: rgb(255, 255, 255); stroke-opacity: 1; stroke-width: 1px;"></path><path class="xgrid crisp" transform="translate(277.95,0)" d="M0,30v454" style="stroke: rgb(255, 255, 255); stroke-opacity: 1; stroke-width: 1px;"></path><path class="xgrid crisp" transform="translate(542.51,0)" d="M0,30v454" style="stroke: rgb(255, 255, 255); stroke-opacity: 1; stroke-width: 1px;"></path><path class="xgrid crisp" transform="translate(674.79,0)" d="M0,30v454" style="stroke: rgb(255, 255, 255); stroke-opacity: 1; stroke-width: 1px;"></path><path class="xgrid crisp" transform="translate(807.08,0)" d="M0,30v454" style="stroke: rgb(255, 255, 255); stroke-opacity: 1; stroke-width: 1px;"></path></g><g class="y"><path class="ygrid crisp" transform="translate(0,427.24)" d="M43,0h835" style="stroke: rgb(255, 255, 255); stroke-opacity: 1; stroke-width: 1px;"></path><path class="ygrid crisp" transform="translate(0,288.51)" d="M43,0h835" style="stroke: rgb(255, 255, 255); stroke-opacity: 1; stroke-width: 1px;"></path><path class="ygrid crisp" transform="translate(0,219.15)" d="M43,0h835" style="stroke: rgb(255, 255, 255); stroke-opacity: 1; stroke-width: 1px;"></path><path class="ygrid crisp" transform="translate(0,149.78)" d="M43,0h835" style="stroke: rgb(255, 255, 255); stroke-opacity: 1; stroke-width: 1px;"></path><path class="ygrid crisp" transform="translate(0,80.42)" d="M43,0h835" style="stroke: rgb(255, 255, 255); stroke-opacity: 1; stroke-width: 1px;"></path></g></g><g class="zerolinelayer"><path class="xzl zl crisp" transform="translate(410.23,0)" d="M0,30v454" style="stroke: rgb(255, 255, 255); stroke-opacity: 1; stroke-width: 2px;"></path><path class="yzl zl crisp" transform="translate(0,357.87)" d="M43,0h835" style="stroke: rgb(255, 255, 255); stroke-opacity: 1; stroke-width: 2px;"></path></g><g class="layer-between"><g class="shapelayer"></g><g class="imagelayer"></g></g><path class="xlines-below"></path><path class="ylines-below"></path><g class="overlines-below"></g><g class="xaxislayer-below"></g><g class="yaxislayer-below"></g><g class="overaxes-below"></g><g class="overplot"><g class="xy" transform="translate(43,30)" clip-path="url(#clip8aa229xyplot)"></g></g><g class="zerolinelayer-above"></g><path class="xlines-above crisp" d="M0,0" style="fill: none;"></path><path class="ylines-above crisp" d="M0,0" style="fill: none;"></path><g class="overlines-above"></g><g class="xaxislayer-above"><g class="xtick"><text text-anchor="middle" x="0" y="497" data-unformatted="−2" data-math="N" transform="translate(145.66,0)" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">−2</text></g><g class="xtick"><text text-anchor="middle" x="0" y="497" data-unformatted="−1" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(277.95,0)">−1</text></g><g class="xtick"><text text-anchor="middle" x="0" y="497" data-unformatted="0" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(410.23,0)">0</text></g><g class="xtick"><text text-anchor="middle" x="0" y="497" data-unformatted="1" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(542.51,0)">1</text></g><g class="xtick"><text text-anchor="middle" x="0" y="497" data-unformatted="2" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(674.79,0)">2</text></g><g class="xtick"><text text-anchor="middle" x="0" y="497" data-unformatted="3" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(807.08,0)">3</text></g></g><g class="yaxislayer-above"><g class="ytick"><text text-anchor="end" x="42" y="4.199999999999999" data-unformatted="−2" data-math="N" transform="translate(0,427.24)" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">−2</text></g><g class="ytick"><text text-anchor="end" x="42" y="4.199999999999999" data-unformatted="0" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(0,357.87)">0</text></g><g class="ytick"><text text-anchor="end" x="42" y="4.199999999999999" data-unformatted="2" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(0,288.51)">2</text></g><g class="ytick"><text text-anchor="end" x="42" y="4.199999999999999" data-unformatted="4" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(0,219.15)">4</text></g><g class="ytick"><text text-anchor="end" x="42" y="4.199999999999999" data-unformatted="6" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(0,149.78)">6</text></g><g class="ytick"><text text-anchor="end" x="42" y="4.199999999999999" data-unformatted="8" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;" transform="translate(0,80.42)">8</text></g></g><g class="overaxes-above"></g></g></g><g class="polarlayer"></g><g class="smithlayer"></g><g class="ternarylayer"></g><g class="geolayer"></g><g class="funnelarealayer"></g><g class="pielayer"></g><g class="iciclelayer"></g><g class="treemaplayer"></g><g class="sunburstlayer"></g><g class="glimages"></g></svg>

<svg class="main-svg" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="949" height="525"><defs id="topdefs-8aa229"><g class="clips"></g><clipPath id="legend8aa229"><rect width="54" height="219" x="0" y="0"></rect></clipPath></defs><g class="indicatorlayer"></g><g class="layer-above"><g class="imagelayer"></g><g class="shapelayer"></g></g><g class="selectionlayer"></g><g class="infolayer"><g class="legend" pointer-events="all" transform="translate(894.7,30)"><rect class="bg" shape-rendering="crispEdges" style="stroke: rgb(68, 68, 68); stroke-opacity: 1; fill: rgb(255, 255, 255); fill-opacity: 1; stroke-width: 0px;" width="54" height="219" x="0" y="0"></rect><g class="scrollbox" transform="" clip-path="url(#legend8aa229)"><text class="legendtitletext" text-anchor="start" data-unformatted="Cluster" data-math="N" x="2" y="18.2" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 14px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">Cluster</text><g class="groups" transform=""><g class="traces" transform="translate(0,32.7)" style="opacity: 1;"><text class="legendtext" text-anchor="start" x="40" y="4.680000000000001" data-unformatted="6" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">6</text><g class="layers" style="opacity: 1;"><g class="legendfill"></g><g class="legendlines"></g><g class="legendsymbols"><g class="legendpoints"><path class="scatterpts" transform="translate(20,0)" d="M2.5,0A2.5,2.5 0 1,1 0,-2.5A2.5,2.5 0 0,1 2.5,0Z" style="opacity: 0.6; stroke-width: 0px; fill: rgb(102, 194, 165); fill-opacity: 1;"></path></g></g></g><rect class="legendtoggle" pointer-events="all" x="0" y="-9.5" width="47.640625" height="19" style="cursor: pointer; fill: rgb(0, 0, 0); fill-opacity: 0;"></rect></g></g><g class="groups" transform=""><g class="traces" transform="translate(0,51.7)" style="opacity: 1;"><text class="legendtext" text-anchor="start" x="40" y="4.680000000000001" data-unformatted="8" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">8</text><g class="layers" style="opacity: 1;"><g class="legendfill"></g><g class="legendlines"></g><g class="legendsymbols"><g class="legendpoints"><path class="scatterpts" transform="translate(20,0)" d="M2.5,0A2.5,2.5 0 1,1 0,-2.5A2.5,2.5 0 0,1 2.5,0Z" style="opacity: 0.6; stroke-width: 0px; fill: rgb(252, 141, 98); fill-opacity: 1;"></path></g></g></g><rect class="legendtoggle" pointer-events="all" x="0" y="-9.5" width="47.640625" height="19" style="cursor: pointer; fill: rgb(0, 0, 0); fill-opacity: 0;"></rect></g></g><g class="groups" transform=""><g class="traces" transform="translate(0,70.7)" style="opacity: 1;"><text class="legendtext" text-anchor="start" x="40" y="4.680000000000001" data-unformatted="2" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">2</text><g class="layers" style="opacity: 1;"><g class="legendfill"></g><g class="legendlines"></g><g class="legendsymbols"><g class="legendpoints"><path class="scatterpts" transform="translate(20,0)" d="M2.5,0A2.5,2.5 0 1,1 0,-2.5A2.5,2.5 0 0,1 2.5,0Z" style="opacity: 0.6; stroke-width: 0px; fill: rgb(141, 160, 203); fill-opacity: 1;"></path></g></g></g><rect class="legendtoggle" pointer-events="all" x="0" y="-9.5" width="47.640625" height="19" style="cursor: pointer; fill: rgb(0, 0, 0); fill-opacity: 0;"></rect></g></g><g class="groups" transform=""><g class="traces" transform="translate(0,89.7)" style="opacity: 1;"><text class="legendtext" text-anchor="start" x="40" y="4.680000000000001" data-unformatted="0" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">0</text><g class="layers" style="opacity: 1;"><g class="legendfill"></g><g class="legendlines"></g><g class="legendsymbols"><g class="legendpoints"><path class="scatterpts" transform="translate(20,0)" d="M2.5,0A2.5,2.5 0 1,1 0,-2.5A2.5,2.5 0 0,1 2.5,0Z" style="opacity: 0.6; stroke-width: 0px; fill: rgb(231, 138, 195); fill-opacity: 1;"></path></g></g></g><rect class="legendtoggle" pointer-events="all" x="0" y="-9.5" width="47.640625" height="19" style="cursor: pointer; fill: rgb(0, 0, 0); fill-opacity: 0;"></rect></g></g><g class="groups" transform=""><g class="traces" transform="translate(0,108.7)" style="opacity: 1;"><text class="legendtext" text-anchor="start" x="40" y="4.680000000000001" data-unformatted="5" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">5</text><g class="layers" style="opacity: 1;"><g class="legendfill"></g><g class="legendlines"></g><g class="legendsymbols"><g class="legendpoints"><path class="scatterpts" transform="translate(20,0)" d="M2.5,0A2.5,2.5 0 1,1 0,-2.5A2.5,2.5 0 0,1 2.5,0Z" style="opacity: 0.6; stroke-width: 0px; fill: rgb(166, 216, 84); fill-opacity: 1;"></path></g></g></g><rect class="legendtoggle" pointer-events="all" x="0" y="-9.5" width="47.640625" height="19" style="cursor: pointer; fill: rgb(0, 0, 0); fill-opacity: 0;"></rect></g></g><g class="groups" transform=""><g class="traces" transform="translate(0,127.7)" style="opacity: 1;"><text class="legendtext" text-anchor="start" x="40" y="4.680000000000001" data-unformatted="1" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">1</text><g class="layers" style="opacity: 1;"><g class="legendfill"></g><g class="legendlines"></g><g class="legendsymbols"><g class="legendpoints"><path class="scatterpts" transform="translate(20,0)" d="M2.5,0A2.5,2.5 0 1,1 0,-2.5A2.5,2.5 0 0,1 2.5,0Z" style="opacity: 0.6; stroke-width: 0px; fill: rgb(255, 217, 47); fill-opacity: 1;"></path></g></g></g><rect class="legendtoggle" pointer-events="all" x="0" y="-9.5" width="47.640625" height="19" style="cursor: pointer; fill: rgb(0, 0, 0); fill-opacity: 0;"></rect></g></g><g class="groups" transform=""><g class="traces" transform="translate(0,146.7)" style="opacity: 1;"><text class="legendtext" text-anchor="start" x="40" y="4.680000000000001" data-unformatted="9" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">9</text><g class="layers" style="opacity: 1;"><g class="legendfill"></g><g class="legendlines"></g><g class="legendsymbols"><g class="legendpoints"><path class="scatterpts" transform="translate(20,0)" d="M2.5,0A2.5,2.5 0 1,1 0,-2.5A2.5,2.5 0 0,1 2.5,0Z" style="opacity: 0.6; stroke-width: 0px; fill: rgb(229, 196, 148); fill-opacity: 1;"></path></g></g></g><rect class="legendtoggle" pointer-events="all" x="0" y="-9.5" width="47.640625" height="19" style="cursor: pointer; fill: rgb(0, 0, 0); fill-opacity: 0;"></rect></g></g><g class="groups" transform=""><g class="traces" transform="translate(0,165.7)" style="opacity: 1;"><text class="legendtext" text-anchor="start" x="40" y="4.680000000000001" data-unformatted="3" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">3</text><g class="layers" style="opacity: 1;"><g class="legendfill"></g><g class="legendlines"></g><g class="legendsymbols"><g class="legendpoints"><path class="scatterpts" transform="translate(20,0)" d="M2.5,0A2.5,2.5 0 1,1 0,-2.5A2.5,2.5 0 0,1 2.5,0Z" style="opacity: 0.6; stroke-width: 0px; fill: rgb(179, 179, 179); fill-opacity: 1;"></path></g></g></g><rect class="legendtoggle" pointer-events="all" x="0" y="-9.5" width="47.640625" height="19" style="cursor: pointer; fill: rgb(0, 0, 0); fill-opacity: 0;"></rect></g></g><g class="groups" transform=""><g class="traces" transform="translate(0,184.7)" style="opacity: 1;"><text class="legendtext" text-anchor="start" x="40" y="4.680000000000001" data-unformatted="7" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">7</text><g class="layers" style="opacity: 1;"><g class="legendfill"></g><g class="legendlines"></g><g class="legendsymbols"><g class="legendpoints"><path class="scatterpts" transform="translate(20,0)" d="M2.5,0A2.5,2.5 0 1,1 0,-2.5A2.5,2.5 0 0,1 2.5,0Z" style="opacity: 0.6; stroke-width: 0px; fill: rgb(102, 194, 165); fill-opacity: 1;"></path></g></g></g><rect class="legendtoggle" pointer-events="all" x="0" y="-9.5" width="47.640625" height="19" style="cursor: pointer; fill: rgb(0, 0, 0); fill-opacity: 0;"></rect></g></g><g class="groups" transform=""><g class="traces" transform="translate(0,203.7)" style="opacity: 1;"><text class="legendtext" text-anchor="start" x="40" y="4.680000000000001" data-unformatted="4" data-math="N" style="font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 12px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">4</text><g class="layers" style="opacity: 1;"><g class="legendfill"></g><g class="legendlines"></g><g class="legendsymbols"><g class="legendpoints"><path class="scatterpts" transform="translate(20,0)" d="M2.5,0A2.5,2.5 0 1,1 0,-2.5A2.5,2.5 0 0,1 2.5,0Z" style="opacity: 0.6; stroke-width: 0px; fill: rgb(252, 141, 98); fill-opacity: 1;"></path></g></g></g><rect class="legendtoggle" pointer-events="all" x="0" y="-9.5" width="47.640625" height="19" style="cursor: pointer; fill: rgb(0, 0, 0); fill-opacity: 0;"></rect></g></g></g><rect class="scrollbar" rx="20" ry="3" width="0" height="0" style="fill: rgb(128, 139, 164); fill-opacity: 1;" x="0" y="0"></rect></g><g class="g-gtitle"><text class="gtitle" x="47.45" y="15" text-anchor="start" dy="0em" data-unformatted="Clusters Estruturais em 2D (PCA: 17.8% + 10.6% = 28.4% variância)" data-math="N" style="opacity: 1; font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 17px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">Clusters Estruturais em 2D (PCA: 17.8% + 10.6% = 28.4% variância)</text></g><g class="g-xtitle" transform="translate(0,-2.2999999999999545)"><text class="xtitle" x="460.5" y="524.3" text-anchor="middle" data-unformatted="PC1" data-math="N" style="opacity: 1; font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 14px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">PC1</text></g><g class="g-ytitle" transform="translate(8.853515625,0)"><text class="ytitle" transform="rotate(-90,5.146875000000001,257)" x="5.146875000000001" y="257" text-anchor="middle" data-unformatted="PC2" data-math="N" style="opacity: 1; font-family: &quot;Open Sans&quot;, verdana, arial, sans-serif; font-size: 14px; fill: rgb(42, 63, 95); fill-opacity: 1; font-weight: normal; font-style: normal; font-variant: normal; white-space: pre;">PC2</text></g></g><g class="menulayer"></g><g class="zoomlayer"></g></svg>

[<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 132 132" height="1em" width="1em"><title>plotly-logomark</title><g id="symbol"><rect fill="#000" x="0" y="0" width="132" height="132" rx="18" ry="18"></rect><circle fill="#9EF" cx="102" cy="30" r="6"></circle><circle fill="#BAC" cx="78" cy="30" r="6"></circle><circle fill="#BAC" cx="78" cy="54" r="6"></circle><circle fill="#D69" cx="54" cy="30" r="6"></circle><circle fill="#F26" cx="30" cy="30" r="6"></circle><circle fill="#F26" cx="30" cy="54" r="6"></circle><path fill="#FFF" d="M30,72a6,6,0,0,0-6,6v24a6,6,0,0,0,12,0V78A6,6,0,0,0,30,72Z"></path><path fill="#FFF" d="M78,72a6,6,0,0,0-6,6v24a6,6,0,0,0,12,0V78A6,6,0,0,0,78,72Z"></path><path fill="#FFF" d="M54,48a6,6,0,0,0-6,6v48a6,6,0,0,0,12,0V54A6,6,0,0,0,54,48Z"></path><path fill="#FFF" d="M102,48a6,6,0,0,0-6,6v48a6,6,0,0,0,12,0V54A6,6,0,0,0,102,48Z"></path></g></svg>](https://plotly.com/)

Projeção PCA dos clusters estruturais

---

# 5\. Próximos Passos

Com os clusters identificados, as próximas análises podem incluir:

1. **EDA por Cluster** — Explorar características de cada grupo
2. **Análise Temporal** — Como os clusters evoluem ao longo do tempo
3. **Radar Charts** — Perfis visuais de P1 vs P2 por cluster
4. **MCA** — Análise de correspondência para variáveis categóricas

```
✅ **Análise de Clustering Concluída**

📁 Dataset salvo: messages_clustered.parquet
   Clusters estruturais: 10
```

---

TipExportar Clusters

O dataset com clusters foi salvo em `messages_clustered.parquet`. Use-o nos próximos notebooks para análises segmentadas.

##### Source Code

```
---
title: "Clustering Analysis"
subtitle: "Análise de clusters: features estruturais vs embeddings semânticos"
author: "Marlon"
date: today
format:
  html:
    toc: true
    toc-depth: 3
    code-fold: true
    theme: cosmo
execute:
  warning: false
  echo: false
---

\`\`\`{python}
#| label: setup
#| code-fold: false

import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Visualização
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Clustering (MiniBatch para eficiência de memória)
from sklearn.cluster import MiniBatchKMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.decomposition import PCA

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona src ao path
sys.path.insert(0, os.getenv('PROJECT_ROOT') + '/src')

from config import PROJECT_ROOT, PATHS, PARTICIPANTES

# Arquivos de entrada
FILE_ENRICHED = PATHS['processed'] / 'messages_enriched.parquet'
FILE_MODELS = PATHS['processed'] / 'messages_with_models.parquet'

# Configurações de performance
CHUNK_SIZE = 10000  # Processa 10k mensagens por vez
SAMPLE_SIZE_ELBOW = 15000  # Amostra para determinar K ótimo
BATCH_SIZE_KMEANS = 1024  # Batch size para MiniBatchKMeans

# Configurações de visualização
plt.style.use('seaborn-v0_8-whitegrid')
COLORS = {'P1': PARTICIPANTES['P1']['cor'], 'P2': PARTICIPANTES['P2']['cor']}
\`\`\`

## Configuração

\`\`\`{python}
#| label: config-display

# Verifica arquivos disponíveis
has_enriched = FILE_ENRICHED.exists()
has_models = FILE_MODELS.exists()

config_data = [
    {'Dataset': '<code>messages_enriched.parquet</code>', 'Status': '✅ Disponível' if has_enriched else '❌ Não encontrado', 'Uso': 'Clustering Estrutural'},
    {'Dataset': '<code>messages_with_models.parquet</code>', 'Status': '✅ Disponível' if has_models else '⚠️ Opcional', 'Uso': 'Clustering Semântico'},
]

display(pd.DataFrame(config_data).style.hide(axis='index'))

# Mostra config de performance
perf_data = [
    {'Parâmetro': 'Amostra para Elbow/Silhouette', 'Valor': f'{SAMPLE_SIZE_ELBOW:,}'},
    {'Parâmetro': 'Batch size (MiniBatchKMeans)', 'Valor': f'{BATCH_SIZE_KMEANS:,}'},
    {'Parâmetro': 'Chunk size (processamento)', 'Valor': f'{CHUNK_SIZE:,}'},
]
print("\n⚡ Configurações de Performance:")
display(pd.DataFrame(perf_data).style.hide(axis='index'))
\`\`\`

------------------------------------------------------------------------

# Introdução

Este notebook explora **duas abordagens de clustering** para identificar padrões nas conversas:

1. **Clustering Estrutural** — Usa features numéricas derivadas (temporais, texto, conversação)
2. **Clustering Semântico** — Usa embeddings de modelos de linguagem

A comparação entre as duas abordagens revela insights complementares:
- Estrutural captura **comportamento** (quando, como, quanto)
- Semântico captura **conteúdo** (o que, significado)

::: {.callout-note}
## Otimização de Memória
Este notebook usa **MiniBatchKMeans** e **amostragem estratificada** para processar grandes volumes de dados sem estourar memória.
:::

------------------------------------------------------------------------

# 1. Carregamento dos Dados

\`\`\`{python}
#| label: load-data
#| output: false

# Carrega dataset enriquecido
df = pd.read_parquet(FILE_ENRICHED)

# Estatísticas básicas
n_mensagens = len(df)
n_colunas = len(df.columns)
periodo_inicio = df['timestamp'].min().strftime('%d/%m/%Y')
periodo_fim = df['timestamp'].max().strftime('%d/%m/%Y')
\`\`\`

\`\`\`{python}
#| label: data-summary

dados_resumo = [
    {'Métrica': 'Mensagens', 'Valor': f'{n_mensagens:,}'},
    {'Métrica': 'Colunas', 'Valor': f'{n_colunas}'},
    {'Métrica': 'Período', 'Valor': f'{periodo_inicio} → {periodo_fim}'},
]

display(pd.DataFrame(dados_resumo).style.hide(axis='index'))
\`\`\`

------------------------------------------------------------------------

# 2. Clustering Estrutural (Features Derivadas)

Agrupa mensagens usando features numéricas criadas no Feature Engineering.

## 2.1 Seleção de Features

\`\`\`{python}
#| label: select-features
#| output: false

# Features numéricas para clustering
# Excluímos: IDs, timestamps, textos, categorias não-ordinais

FEATURES_TEMPORAIS = [
    'hora', 'dia_semana_num', 'mes', 'fim_de_semana', 'horario_comercial'
]

FEATURES_TEXTO = [
    'tamanho_caracteres', 'tamanho_palavras',
    'tem_emoji', 'qtd_emojis', 'tem_link',
    'tem_interrogacao', 'tem_exclamacao', 'eh_caixa_alta'
]

FEATURES_CONVERSACAO = [
    'tempo_desde_ultima_msg', 'eh_resposta_rapida',
    'sequencia_mesmo_remetente', 'eh_inicio_conversa'
]

# Combina todas as features
FEATURES_CLUSTERING = FEATURES_TEMPORAIS + FEATURES_TEXTO + FEATURES_CONVERSACAO

# Verifica quais existem no dataset
features_disponiveis = [f for f in FEATURES_CLUSTERING if f in df.columns]
features_faltando = [f for f in FEATURES_CLUSTERING if f not in df.columns]

# Adiciona dia_semana_num se não existir
if 'dia_semana_num' not in df.columns and 'dia_semana' in df.columns:
    dia_map = {'Segunda': 0, 'Terça': 1, 'Quarta': 2, 'Quinta': 3, 'Sexta': 4, 'Sábado': 5, 'Domingo': 6}
    df['dia_semana_num'] = df['dia_semana'].map(dia_map)
    if 'dia_semana_num' not in features_disponiveis:
        features_disponiveis.append('dia_semana_num')
\`\`\`

\`\`\`{python}
#| label: show-features

features_info = []
for cat, feats in [('Temporais', FEATURES_TEMPORAIS),
                   ('Texto', FEATURES_TEXTO),
                   ('Conversação', FEATURES_CONVERSACAO)]:
    for f in feats:
        status = '✅' if f in features_disponiveis else '❌'
        features_info.append({'Categoria': cat, 'Feature': f'<code>{f}</code>', 'Status': status})

display(pd.DataFrame(features_info).style.hide(axis='index'))
\`\`\`

\`\`\`{python}
#| label: prepare-clustering-data
#| output: false

# Prepara matriz de features
df_cluster = df[features_disponiveis].copy()

# Processa cada coluna individualmente
for col in df_cluster.columns:
    # Converte categorias para numérico
    if df_cluster[col].dtype.name == 'category':
        df_cluster[col] = df_cluster[col].cat.codes

    # Converte booleanos para int
    elif df_cluster[col].dtype == bool:
        df_cluster[col] = df_cluster[col].astype(int)

    # Substitui infinitos por NaN
    df_cluster[col] = df_cluster[col].replace([np.inf, -np.inf], np.nan)

    # Preenche NaN com mediana (só para numéricos)
    if df_cluster[col].isna().any():
        df_cluster[col] = df_cluster[col].fillna(df_cluster[col].median())

# Padroniza features (Z-score)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_cluster)

n_features_usadas = len(features_disponiveis)
\`\`\`

Features disponíveis para clustering: \`{python} n_features_usadas\`

## 2.2 Determinação do Número de Clusters

\`\`\`{python}
#| label: elbow-silhouette
#| fig-cap: "Método Elbow e Silhouette Score para determinar número ótimo de clusters"

# Usa amostra estratificada para determinar K (economiza memória)
n_total = len(X_scaled)
sample_size = min(SAMPLE_SIZE_ELBOW, n_total)

# Amostra aleatória para análise
np.random.seed(42)
sample_idx = np.random.choice(n_total, sample_size, replace=False)
X_sample = X_scaled[sample_idx]

print(f"📊 Usando amostra de {sample_size:,} mensagens para determinar K ótimo")
print(f"   (de {n_total:,} total - {sample_size/n_total*100:.1f}%)\n")

# Testa diferentes números de clusters com MiniBatchKMeans
K_range = range(2, 11)
inertias = []
silhouettes = []

for k in K_range:
    # MiniBatchKMeans é ~10x mais rápido e usa menos memória
    kmeans = MiniBatchKMeans(
        n_clusters=k,
        random_state=42,
        batch_size=min(BATCH_SIZE_KMEANS, sample_size),
        n_init=3  # Menos inicializações para velocidade
    )
    labels = kmeans.fit_predict(X_sample)
    inertias.append(kmeans.inertia_)
    silhouettes.append(silhouette_score(X_sample, labels))

# Plot
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Elbow
axes[0].plot(list(K_range), inertias, 'bo-', linewidth=2, markersize=8)
axes[0].set_xlabel('Número de Clusters (K)')
axes[0].set_ylabel('Inércia (Within-cluster SS)')
axes[0].set_title('Método Elbow')
axes[0].set_xticks(list(K_range))

# Silhouette
axes[1].plot(list(K_range), silhouettes, 'go-', linewidth=2, markersize=8)
axes[1].set_xlabel('Número de Clusters (K)')
axes[1].set_ylabel('Silhouette Score')
axes[1].set_title('Silhouette Score por K')
axes[1].set_xticks(list(K_range))

# Marca o melhor K
best_k = list(K_range)[np.argmax(silhouettes)]
axes[1].axvline(x=best_k, color='red', linestyle='--', alpha=0.7, label=f'Melhor K = {best_k}')
axes[1].legend()

plt.tight_layout()
plt.show()

print(f"📊 Melhor K pelo Silhouette Score: {best_k}")
\`\`\`

## 2.3 Clustering Final

\`\`\`{python}
#| label: final-clustering
#| output: false

# Usa o melhor K (ou permite override manual)
K_ESTRUTURAL = best_k  # Altere aqui se quiser testar outro valor

# Executa MiniBatchKMeans no dataset completo
# Processa em chunks para economizar memória
kmeans_estrutural = MiniBatchKMeans(
    n_clusters=K_ESTRUTURAL,
    random_state=42,
    batch_size=BATCH_SIZE_KMEANS,
    n_init=3
)

# Fit em chunks
n_chunks = (len(X_scaled) + CHUNK_SIZE - 1) // CHUNK_SIZE
for i in range(n_chunks):
    start_idx = i * CHUNK_SIZE
    end_idx = min((i + 1) * CHUNK_SIZE, len(X_scaled))
    chunk = X_scaled[start_idx:end_idx]
    kmeans_estrutural.partial_fit(chunk)

# Predict em chunks para economizar memória
labels = []
for i in range(n_chunks):
    start_idx = i * CHUNK_SIZE
    end_idx = min((i + 1) * CHUNK_SIZE, len(X_scaled))
    chunk = X_scaled[start_idx:end_idx]
    labels.extend(kmeans_estrutural.predict(chunk))

df['cluster_estrutural'] = labels

# Calcula silhouette score usando amostra (silhouette_samples é muito pesado)
sample_for_silhouette = min(10000, len(X_scaled))
sil_idx = np.random.choice(len(X_scaled), sample_for_silhouette, replace=False)
score_estrutural = silhouette_score(X_scaled[sil_idx], np.array(labels)[sil_idx])
\`\`\`

\`\`\`{python}
#| label: clustering-result

result_data = [
    {'Métrica': 'Número de Clusters', 'Valor': f'{K_ESTRUTURAL}'},
    {'Métrica': 'Silhouette Score (amostra)', 'Valor': f'{score_estrutural:.3f}'},
    {'Métrica': 'Interpretação', 'Valor': 'Bom' if score_estrutural > 0.5 else 'Moderado' if score_estrutural > 0.25 else 'Fraco'},
]

display(pd.DataFrame(result_data).style.hide(axis='index'))
\`\`\`

## 2.4 Distribuição dos Clusters

\`\`\`{python}
#| label: cluster-distribution
#| fig-cap: "Distribuição de mensagens por cluster estrutural"

cluster_counts = df['cluster_estrutural'].value_counts().sort_index()

fig = px.bar(
    x=cluster_counts.index,
    y=cluster_counts.values,
    labels={'x': 'Cluster', 'y': 'Quantidade de Mensagens'},
    title='Distribuição por Cluster Estrutural',
    color=cluster_counts.index.astype(str),
    color_discrete_sequence=px.colors.qualitative.Set2
)
fig.update_layout(showlegend=False, xaxis_tickmode='linear')
fig.show()
\`\`\`

## 2.5 Perfil dos Clusters

\`\`\`{python}
#| label: cluster-profiles
#| fig-cap: "Perfil médio normalizado de cada cluster"

# Calcula médias por cluster usando chunks para economizar memória
cluster_profiles_list = []

for cluster_id in range(K_ESTRUTURAL):
    mask = df['cluster_estrutural'] == cluster_id
    cluster_data = X_scaled[mask]

    # Processa em chunks se necessário
    if len(cluster_data) > CHUNK_SIZE:
        means = []
        for i in range(0, len(cluster_data), CHUNK_SIZE):
            chunk = cluster_data[i:i+CHUNK_SIZE]
            means.append(chunk.mean(axis=0))
        cluster_mean = np.mean(means, axis=0)
    else:
        cluster_mean = cluster_data.mean(axis=0)

    cluster_profiles_list.append(cluster_mean)

cluster_profiles = pd.DataFrame(
    cluster_profiles_list,
    columns=features_disponiveis,
    index=range(K_ESTRUTURAL)
)

# Heatmap
fig, ax = plt.subplots(figsize=(14, 6))
sns.heatmap(
    cluster_profiles.T,
    cmap='RdYlBu_r',
    center=0,
    annot=True,
    fmt='.2f',
    ax=ax,
    cbar_kws={'label': 'Z-score (desvios da média)'}
)
ax.set_xlabel('Cluster')
ax.set_ylabel('Feature')
ax.set_title('Perfil dos Clusters Estruturais (Features Normalizadas)')
plt.tight_layout()
plt.show()
\`\`\`

\`\`\`{python}
#| label: cluster-interpretation

# Gera interpretação automática baseada nas features dominantes
print("📋 **Interpretação dos Clusters:**\n")

for cluster_id in range(K_ESTRUTURAL):
    profile = cluster_profiles.loc[cluster_id]
    count = cluster_counts.get(cluster_id, 0)

    # Features mais altas e mais baixas
    top_features = profile.nlargest(3)
    bottom_features = profile.nsmallest(3)

    print(f"**Cluster {cluster_id}** ({count:,} mensagens)")
    print(f"  📈 Características altas: {', '.join(top_features.index.tolist())}")
    print(f"  📉 Características baixas: {', '.join(bottom_features.index.tolist())}")
    print()
\`\`\`

## 2.6 Clusters por Participante

\`\`\`{python}
#| label: clusters-by-participant
#| fig-cap: "Distribuição de clusters por participante"

if 'remetente' in df.columns:
    crosstab = pd.crosstab(df['remetente'], df['cluster_estrutural'], normalize='index') * 100

    fig = px.bar(
        crosstab,
        barmode='group',
        labels={'value': '% das Mensagens', 'cluster_estrutural': 'Cluster'},
        title='Distribuição de Clusters por Participante (%)',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(legend_title='Cluster')
    fig.show()
\`\`\`

## 2.7 Visualização 2D (PCA)

\`\`\`{python}
#| label: pca-visualization
#| fig-cap: "Projeção PCA dos clusters estruturais"

# Usa amostra para PCA (performance)
pca_sample_size = min(5000, len(X_scaled))
pca_idx = np.random.choice(len(X_scaled), pca_sample_size, replace=False)
X_pca_sample = X_scaled[pca_idx]
labels_sample = np.array(df['cluster_estrutural'])[pca_idx]

# Reduz para 2D com PCA
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_pca_sample)

# Variância explicada
var_explained = pca.explained_variance_ratio_

# Cria DataFrame para plot
df_pca = pd.DataFrame({
    'PC1': X_pca[:, 0],
    'PC2': X_pca[:, 1],
    'Cluster': labels_sample.astype(str),
    'Remetente': df['remetente'].iloc[pca_idx].values if 'remetente' in df.columns else 'N/A'
})

# Plot
fig = px.scatter(
    df_pca,
    x='PC1', y='PC2',
    color='Cluster',
    hover_data=['Remetente'],
    title=f'Clusters Estruturais em 2D (PCA: {var_explained[0]:.1%} + {var_explained[1]:.1%} = {sum(var_explained):.1%} variância)',
    color_discrete_sequence=px.colors.qualitative.Set2,
    opacity=0.6
)
fig.update_traces(marker=dict(size=5))
fig.show()
\`\`\`

------------------------------------------------------------------------

# 5. Próximos Passos

Com os clusters identificados, as próximas análises podem incluir:

1. **EDA por Cluster** — Explorar características de cada grupo
2. **Análise Temporal** — Como os clusters evoluem ao longo do tempo
3. **Radar Charts** — Perfis visuais de P1 vs P2 por cluster
4. **MCA** — Análise de correspondência para variáveis categóricas

\`\`\`{python}
#| label: save-clusters
#| output: false

# Salva dataset com clusters
OUTPUT_FILE = PATHS['processed'] / 'messages_clustered.parquet'
df.to_parquet(OUTPUT_FILE, index=False)
\`\`\`

\`\`\`{python}
#| label: final-summary

print("✅ **Análise de Clustering Concluída**\n")
print(f"📁 Dataset salvo: messages_clustered.parquet")
print(f"   Clusters estruturais: {K_ESTRUTURAL}")
#if has_embeddings and 'K_SEMANTICO' in dir():
#print(f"   Clusters semânticos: {K_SEMANTICO}")
#print(f"   Modelo de embeddings: {EMBEDDING_CHOICE.upper()}")
\`\`\`

------------------------------------------------------------------------

::: {.callout-tip}
## Exportar Clusters

O dataset com clusters foi salvo em \`messages_clustered.parquet\`.
Use-o nos próximos notebooks para análises segmentadas.
:::
```

Desenvolvido por [@mrlnlms](https://github.com/mrlnlms)

````


