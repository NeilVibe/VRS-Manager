"""
Casting key generation module.

This module provides functionality to generate casting keys based on
character information, dialog voice, and speaker group keys.
"""

from src.utils.helpers import safe_str


def generate_casting_key(character_key, dialog_voice, speaker_groupkey, dialog_type=""):
    """
    Generate a casting key based on character and dialog information.

    Args:
        character_key: The character key identifier
        dialog_voice: The dialog voice identifier
        speaker_groupkey: The speaker group key
        dialog_type: Type of dialog (e.g., "aidialog", "questdialog")

    Returns:
        str: The generated casting key or "Not Found" if unable to generate
    """
    char_key = safe_str(character_key)
    dialog_v = safe_str(dialog_voice)
    speaker_gk = safe_str(speaker_groupkey)
    dtype = safe_str(dialog_type)

    if dtype.lower() in ["aidialog", "questdialog"]:
        return dialog_v.lower() if dialog_v else "Not Found"

    if dialog_v and "unique_" in dialog_v.lower():
        return dialog_v.lower()

    if char_key and speaker_gk and char_key.lower() in speaker_gk.lower():
        return speaker_gk.lower()

    if char_key:
        return char_key.lower()

    return "Not Found"
