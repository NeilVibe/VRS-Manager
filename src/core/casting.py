"""
Casting key generation module.

This module provides functionality to generate casting keys based on
character information, dialog voice, and speaker group keys.
"""

from src.utils.helpers import safe_str, log
from src.config import COL_CHARACTERKEY, COL_DIALOGVOICE, COL_SPEAKER_GROUPKEY, COL_DIALOGTYPE

# Required columns for proper CastingKey generation
CASTINGKEY_SOURCE_COLUMNS = [
    COL_CHARACTERKEY,      # CharacterKey
    COL_DIALOGVOICE,       # DialogVoice
    COL_SPEAKER_GROUPKEY,  # Speaker|CharacterGroupKey
    COL_DIALOGTYPE,        # DialogType
]


def validate_castingkey_columns(df, file_label=""):
    """
    Validate that all required columns for CastingKey generation exist in DataFrame.

    Args:
        df: DataFrame to validate
        file_label: Label for the file (e.g., "PREVIOUS", "CURRENT") for error messages

    Returns:
        tuple: (is_valid, missing_columns)
            - is_valid: True if all required columns exist
            - missing_columns: List of missing column names
    """
    missing = []
    for col in CASTINGKEY_SOURCE_COLUMNS:
        if col not in df.columns:
            missing.append(col)

    if missing:
        log(f"⚠️  WARNING: {file_label} file missing CastingKey source columns:")
        for col in missing:
            log(f"     → Missing: {col}")
        log(f"     CastingKey comparison may produce incorrect results!")
        log(f"     Please ensure all these columns exist: {', '.join(CASTINGKEY_SOURCE_COLUMNS)}")
        return False, missing

    return True, []


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
