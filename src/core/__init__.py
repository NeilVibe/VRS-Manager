"""
Core VRS Manager processing modules.
"""

from src.core.casting import generate_casting_key
from src.core.lookups import build_lookups
from src.core.comparison import (
    compare_rows,
    classify_working_change,
    classify_alllang_change,
    find_deleted_rows
)
from src.core.import_logic import (
    apply_import_logic,
    apply_import_logic_alllang_lang
)
from src.core.working_comparison import process_working_comparison
from src.core.alllang_helpers import (
    find_alllang_files,
    merge_current_files,
    process_alllang_comparison_twopass
)
from src.core.working_helpers import (
    build_working_lookups,
    find_working_deleted_rows
)

__all__ = [
    'generate_casting_key',
    'build_lookups',
    'build_working_lookups',
    'compare_rows',
    'classify_working_change',
    'classify_alllang_change',
    'find_deleted_rows',
    'find_working_deleted_rows',
    'apply_import_logic',
    'apply_import_logic_alllang_lang',
    'process_working_comparison',
    'find_alllang_files',
    'merge_current_files',
    'process_alllang_comparison_twopass'
]
