"""
WhatsApp Analysis - Módulos de processamento de dados.

Este pacote contém os módulos para o pipeline completo de análise
de conversas do WhatsApp, desde o profiling até feature engineering.

Módulos:
    - profiling: Investigação inicial de arquivos brutos
    - cleaning: Funções de limpeza de dados
    - parsing: Parser de txt para DataFrame
    - wrangling: Vinculação de mídia e transcrição
    - features: Feature engineering
    - audit: Auditoria de transformações
    - config: Configurações centralizadas
"""

from .config import (
    PARTICIPANTES,
    PATHS,
    THRESHOLDS,
    PERIODOS_DIA,
    DIAS_SEMANA,
    MESES,
    REGEX_PATTERNS
)

__version__ = '2.0.0'
__author__ = 'Marlon'
