"""
VRS Manager processors.

This module contains all processor classes for the four main VRS processes.
"""

from src.processors.base_processor import BaseProcessor
from src.processors.raw_processor import RawProcessor
from src.processors.working_processor import WorkingProcessor
from src.processors.alllang_processor import AllLangProcessor
from src.processors.master_processor import MasterProcessor

__all__ = [
    'BaseProcessor',
    'RawProcessor',
    'WorkingProcessor',
    'AllLangProcessor',
    'MasterProcessor',
]
