"""
Utilitários cross-cutting do projeto.
"""

from .dataframe_helpers import (
    multi_position_preview_dataframe, 
    format_file_overview_table,
    format_density_stats_table
)
from .file_helpers import get_file_overview, get_file_density_stats
from .audit import (
    audit_transformation, 
    audit_pipeline, 
    format_audit_table,
    format_summary_table,
    generate_impact_analysis,
    get_file_stats,
    format_bytes
)

__all__ = [
    # DataFrame helpers
    'multi_position_preview_dataframe',
    'format_file_overview_table',
    'format_density_stats_table',
    # File helpers
    'get_file_overview',
    'get_file_density_stats',
    # Audit helpers
    'audit_transformation',
    'audit_pipeline',
    'format_audit_table',
    'format_summary_table',
    'generate_impact_analysis',
    'get_file_stats',
    'format_bytes',
]