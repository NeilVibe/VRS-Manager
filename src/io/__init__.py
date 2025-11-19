"""
Input/Output modules for VRS Manager.
"""

from src.io.excel_reader import (
    safe_read_excel,
    normalize_dataframe_status,
    find_status_column,
    normalize_status,
    is_after_recording_status
)
from src.utils.data_processing import filter_output_columns
from src.io.formatters import (
    apply_direct_coloring,
    widen_summary_columns,
    format_update_history_sheet,
    generate_color_for_value
)

__all__ = [
    # Excel reader
    'safe_read_excel',
    'normalize_dataframe_status',
    'find_status_column',
    'normalize_status',
    'is_after_recording_status',
    # Excel writer
    'filter_output_columns',
    # Formatters
    'apply_direct_coloring',
    'widen_summary_columns',
    'format_update_history_sheet',
    'generate_color_for_value'
]
