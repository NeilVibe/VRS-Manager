"""
User settings management for VRS Manager.

This module provides functionality to save and load user preferences,
including the Priority Change display toggle and column customization.
"""

import json
import os

from src.config import AUTO_GENERATED_COLUMNS, OPTIONAL_COLUMNS, MANDATORY_COLUMNS, VRS_CONDITIONAL_COLUMNS

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


def get_vrs_conditional_columns():
    """
    Get VRS conditional columns (always from CURRENT, always enabled).

    These columns are used in VRS change detection logic and cannot be disabled.

    Returns:
        list: List of VRS conditional column names
    """
    return VRS_CONDITIONAL_COLUMNS.copy()


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
    # Exclude MANDATORY, AUTO_GENERATED, and VRS_CONDITIONAL (those are not optional)
    analyzed = settings.get("analyzed_columns", [])
    settings["output_columns"]["optional"] = {
        col: {"enabled": col in columns}
        for col in analyzed
        if col not in MANDATORY_COLUMNS
        and col not in AUTO_GENERATED_COLUMNS
        and col not in VRS_CONDITIONAL_COLUMNS
    }
    save_settings(settings)


# ===========================================================================
# V3: DUAL-FILE COLUMN ANALYSIS (PREVIOUS + CURRENT)
# ===========================================================================

def get_previous_file_columns():
    """Get columns analyzed from PREVIOUS file."""
    settings = load_settings()
    return settings.get("previous_file_columns", [])


def set_previous_file_columns(columns):
    """Set columns analyzed from PREVIOUS file."""
    settings = load_settings()
    settings["previous_file_columns"] = columns
    save_settings(settings)
    # Update combined columns
    _update_combined_columns()


def get_current_file_columns():
    """Get columns analyzed from CURRENT file."""
    settings = load_settings()
    return settings.get("current_file_columns", [])


def set_current_file_columns(columns):
    """Set columns analyzed from CURRENT file."""
    settings = load_settings()
    settings["current_file_columns"] = columns
    save_settings(settings)
    # Update combined columns
    _update_combined_columns()


def _update_combined_columns():
    """
    Combine columns from PREVIOUS and CURRENT files.

    For duplicate column names:
    - Add "Previous_" prefix for columns from PREVIOUS file
    - Add "Current_" prefix for columns from CURRENT file

    Unique columns keep their original names.
    """
    settings = load_settings()
    prev_cols = set(settings.get("previous_file_columns", []))
    curr_cols = set(settings.get("current_file_columns", []))

    # Find duplicates (exist in both)
    duplicates = prev_cols & curr_cols

    # Build combined list with prefixes for duplicates
    combined = []

    # Add PREVIOUS columns
    for col in sorted(prev_cols):
        if col in duplicates:
            combined.append(f"Previous_{col}")
        else:
            combined.append(col)

    # Add CURRENT columns
    for col in sorted(curr_cols):
        if col in duplicates:
            combined.append(f"Current_{col}")
        elif col not in prev_cols:  # Only add if not already added from PREVIOUS
            combined.append(col)

    # Update analyzed_columns for backward compatibility
    settings["analyzed_columns"] = combined
    save_settings(settings)


def get_dual_file_status():
    """
    Get status of both file uploads.

    Returns:
        dict: {
            "previous": {"uploaded": bool, "filename": str, "count": int},
            "current": {"uploaded": bool, "filename": str, "count": int}
        }
    """
    settings = load_settings()
    return {
        "previous": {
            "uploaded": len(settings.get("previous_file_columns", [])) > 0,
            "filename": settings.get("previous_filename", ""),
            "count": len(settings.get("previous_file_columns", []))
        },
        "current": {
            "uploaded": len(settings.get("current_file_columns", [])) > 0,
            "filename": settings.get("current_filename", ""),
            "count": len(settings.get("current_file_columns", []))
        }
    }


def set_file_info(file_type, filename, columns):
    """
    Set file info for PREVIOUS or CURRENT.

    Args:
        file_type: "previous" or "current"
        filename: Name of the uploaded file
        columns: List of column names
    """
    settings = load_settings()

    if file_type == "previous":
        settings["previous_filename"] = filename
        settings["previous_file_columns"] = columns
    elif file_type == "current":
        settings["current_filename"] = filename
        settings["current_file_columns"] = columns

    save_settings(settings)
    _update_combined_columns()


def clear_file_columns(file_type):
    """Clear columns for a specific file type."""
    settings = load_settings()

    if file_type == "previous":
        settings["previous_file_columns"] = []
        settings["previous_filename"] = ""
    elif file_type == "current":
        settings["current_file_columns"] = []
        settings["current_filename"] = ""

    save_settings(settings)
    _update_combined_columns()


# ===========================================================================
# V5: DUAL-FILE COLUMN SELECTION (CURRENT + PREVIOUS with KEY matching)
# ===========================================================================

def get_v5_column_settings():
    """
    Get V5 column settings.

    Returns:
        dict: {
            "auto_generated": {col: bool, ...},
            "current_file": {"filename": str, "columns": [], "selected": []},
            "previous_file": {"filename": str, "columns": [], "selected": []}
        }
    """
    settings = load_settings()
    return {
        "auto_generated": settings.get("v5_auto_generated", {col: True for col in AUTO_GENERATED_COLUMNS}),
        "current_file": settings.get("v5_current_file", {"filename": "", "columns": [], "selected": []}),
        "previous_file": settings.get("v5_previous_file", {"filename": "", "columns": [], "selected": []})
    }


def set_v5_auto_generated(auto_gen_settings):
    """
    Set V5 auto-generated column settings.

    Args:
        auto_gen_settings: Dict of {column_name: enabled_bool}
    """
    settings = load_settings()
    settings["v5_auto_generated"] = auto_gen_settings
    save_settings(settings)


def set_v5_current_file(filename, columns, selected):
    """
    Set V5 current file info.

    Args:
        filename: Name of the uploaded file
        columns: List of all optional column names found
        selected: List of selected column names
    """
    settings = load_settings()
    settings["v5_current_file"] = {
        "filename": filename,
        "columns": columns,
        "selected": selected
    }
    save_settings(settings)


def set_v5_previous_file(filename, columns, selected):
    """
    Set V5 previous file info.

    Args:
        filename: Name of the uploaded file
        columns: List of all optional column names found
        selected: List of selected column names
    """
    settings = load_settings()
    settings["v5_previous_file"] = {
        "filename": filename,
        "columns": columns,
        "selected": selected
    }
    save_settings(settings)


def reset_v5_all():
    """Reset all V5 settings (auto-generated, current file, previous file)."""
    settings = load_settings()

    # Reset auto-generated to all ON
    settings["v5_auto_generated"] = {col: True for col in AUTO_GENERATED_COLUMNS}

    # Clear file uploads
    settings["v5_current_file"] = {"filename": "", "columns": [], "selected": []}
    settings["v5_previous_file"] = {"filename": "", "columns": [], "selected": []}

    save_settings(settings)


def get_v5_enabled_columns():
    """
    Get all enabled columns for V5.

    Previous_ prefix is ONLY added when there's a CONFLICT:
    - Same column selected from BOTH CURRENT and PREVIOUS files
    - Prefix differentiates the two values in output

    If a column is only selected from PREVIOUS (not CURRENT), no prefix needed.

    Returns:
        dict: {
            "auto_generated": [list of enabled auto-gen column names],
            "current": [list of selected current file columns],
            "previous": [list of previous columns - prefixed only if conflict with current]
        }
    """
    v5 = get_v5_column_settings()

    enabled_auto = [col for col, enabled in v5["auto_generated"].items() if enabled]
    enabled_current = set(v5["current_file"].get("selected", []))
    selected_previous = v5["previous_file"].get("selected", [])

    # Only add Previous_ prefix if column is ALSO selected from CURRENT (conflict)
    enabled_previous = []
    for col in selected_previous:
        if col in enabled_current:
            # CONFLICT: same column selected from both files - add prefix
            enabled_previous.append(f"Previous_{col}")
        else:
            # NO CONFLICT: column only from PREVIOUS - no prefix needed
            enabled_previous.append(col)

    return {
        "auto_generated": enabled_auto,
        "current": list(enabled_current),
        "previous": enabled_previous
    }
