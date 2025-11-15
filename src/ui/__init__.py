"""
VRS Manager user interface components.

This module contains the GUI components for the VRS Manager application.
"""

from src.ui.main_window import create_gui
from src.ui.history_viewer import show_update_history_viewer

__all__ = [
    'create_gui',
    'show_update_history_viewer',
]
