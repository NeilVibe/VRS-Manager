"""
User settings management for VRS Manager.

This module provides functionality to save and load user preferences,
including the Priority Change display toggle and column customization.
"""

import json
import os

from src.config import AUTO_GENERATED_COLUMNS, OPTIONAL_COLUMNS, MANDATORY_COLUMNS

# Settings file path (in user's home directory for persistence)
SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".vrsmanager_settings.json")

# Default column settings - all ON by default
DEFAULT_AUTO_GENERATED_SETTINGS = {col: {"enabled": True} for col in AUTO_GENERATED_COLUMNS}
DEFAULT_OPTIONAL_SETTINGS = {col: {"enabled": True, "source": "CURRENT"} for col in OPTIONAL_COLUMNS}

# Default settings
DEFAULT_SETTINGS = {
    "use_priority_change": True,  # ON by default (new behavior)
    "output_columns": {
        "auto_generated": DEFAULT_AUTO_GENERATED_SETTINGS,
        "optional": DEFAULT_OPTIONAL_SETTINGS
    }
}


def load_settings():
    """
    Load user settings from file.

    Returns:
        dict: Settings dictionary with all user preferences
    """
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                # Merge with defaults for any missing top-level keys
                for key, value in DEFAULT_SETTINGS.items():
                    if key not in settings:
                        settings[key] = value

                # Ensure output_columns has all required columns (for new columns added later)
                if "output_columns" in settings:
                    # Merge auto_generated columns
                    for col in AUTO_GENERATED_COLUMNS:
                        if col not in settings["output_columns"].get("auto_generated", {}):
                            if "auto_generated" not in settings["output_columns"]:
                                settings["output_columns"]["auto_generated"] = {}
                            settings["output_columns"]["auto_generated"][col] = {"enabled": True}

                    # Merge optional columns - only if V2 analyzed_columns not set
                    # V2 uses analyzed_columns from file, V1 uses hardcoded OPTIONAL_COLUMNS
                    if not settings.get("analyzed_columns"):
                        for col in OPTIONAL_COLUMNS:
                            if col not in settings["output_columns"].get("optional", {}):
                                if "optional" not in settings["output_columns"]:
                                    settings["output_columns"]["optional"] = {}
                                settings["output_columns"]["optional"][col] = {"enabled": True, "source": "CURRENT"}

                return settings
    except (json.JSONDecodeError, IOError):
        pass

    return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    """
    Save user settings to file.

    Args:
        settings: Dictionary of settings to save
    """
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
    except IOError:
        pass  # Silently fail if we can't save


def get_use_priority_change():
    """
    Get the Priority Change display setting.

    Returns:
        bool: True if Priority Change mode is enabled (new behavior),
              False for legacy DETAILED_CHANGES mode
    """
    settings = load_settings()
    return settings.get("use_priority_change", True)


def set_use_priority_change(value):
    """
    Set the Priority Change display setting.

    Args:
        value: True for Priority Change mode, False for legacy mode
    """
    settings = load_settings()
    settings["use_priority_change"] = bool(value)
    save_settings(settings)


# ===========================================================================
# COLUMN SETTINGS
# ===========================================================================

def get_column_settings():
    """
    Get the output column settings.

    Returns:
        dict: Column settings with 'auto_generated' and 'optional' keys
    """
    settings = load_settings()
    return settings.get("output_columns", DEFAULT_SETTINGS["output_columns"])


def set_column_settings(column_settings):
    """
    Set the output column settings.

    Args:
        column_settings: Dictionary with 'auto_generated' and 'optional' keys
    """
    settings = load_settings()
    settings["output_columns"] = column_settings
    save_settings(settings)


def get_enabled_columns():
    """
    Get list of enabled columns based on current settings.

    Returns:
        tuple: (enabled_auto_generated, enabled_optional_with_source)
            - enabled_auto_generated: List of enabled auto-generated column names
            - enabled_optional_with_source: Dict of {column_name: source} for enabled optional columns
    """
    col_settings = get_column_settings()

    # Auto-generated columns that are enabled
    enabled_auto = [
        col for col, cfg in col_settings.get("auto_generated", {}).items()
        if cfg.get("enabled", True)
    ]

    # Optional columns that are enabled, with their source
    enabled_optional = {
        col: cfg.get("source", "CURRENT")
        for col, cfg in col_settings.get("optional", {}).items()
        if cfg.get("enabled", True)
    }

    return enabled_auto, enabled_optional


def reset_column_settings():
    """Reset column settings to defaults (all ON)."""
    settings = load_settings()
    settings["output_columns"] = {
        "auto_generated": {col: {"enabled": True} for col in AUTO_GENERATED_COLUMNS},
        "optional": {}  # V2: Will be populated from file analysis
    }
    settings["analyzed_columns"] = []  # V2: Clear analyzed columns
    save_settings(settings)


# ===========================================================================
# V2: ANALYZED COLUMNS (from file upload)
# ===========================================================================

def get_analyzed_columns():
    """
    Get the list of columns analyzed from uploaded file.

    Returns:
        list: List of column names from analyzed file
    """
    settings = load_settings()
    return settings.get("analyzed_columns", [])


def set_analyzed_columns(columns):
    """
    Set the list of columns analyzed from uploaded file.

    Args:
        columns: List of column names
    """
    settings = load_settings()
    settings["analyzed_columns"] = columns
    save_settings(settings)


def get_selected_optional_columns():
    """
    Get the list of selected optional columns.

    Returns:
        list: List of enabled optional column names
    """
    col_settings = get_column_settings()
    return [
        col for col, cfg in col_settings.get("optional", {}).items()
        if cfg.get("enabled", True)
    ]


def set_selected_optional_columns(columns):
    """
    Set which optional columns are selected.

    Args:
        columns: List of column names to enable
    """
    settings = load_settings()
    if "output_columns" not in settings:
        settings["output_columns"] = {"auto_generated": {}, "optional": {}}

    # Set all analyzed columns, enabled if in columns list
    analyzed = settings.get("analyzed_columns", [])
    settings["output_columns"]["optional"] = {
        col: {"enabled": col in columns}
        for col in analyzed
        if col not in MANDATORY_COLUMNS and col not in AUTO_GENERATED_COLUMNS
    }
    save_settings(settings)
