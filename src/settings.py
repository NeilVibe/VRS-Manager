"""
User settings management for VRS Manager.

This module provides functionality to save and load user preferences,
including the Priority Change display toggle.
"""

import json
import os

# Settings file path (in user's home directory for persistence)
SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".vrsmanager_settings.json")

# Default settings
DEFAULT_SETTINGS = {
    "use_priority_change": True  # ON by default (new behavior)
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
                # Merge with defaults for any missing keys
                for key, value in DEFAULT_SETTINGS.items():
                    if key not in settings:
                        settings[key] = value
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
