"""
Casting key generation module.

This module provides functionality to generate casting keys based on
character information, dialog voice, and speaker group keys.
"""

from src.utils.helpers import safe_str, log
from src.config import COL_CHARACTERKEY, COL_DIALOGVOICE, COL_SPEAKER_GROUPKEY, COL_DIALOGTYPE

# Required columns for CastingKey generation
# BOTH files need: CharacterKey, DialogVoice, DialogType
# CURRENT only needs: Speaker|CharacterGroupKey (used for BOTH files)
CASTINGKEY_COLUMNS_BOTH = [
    COL_CHARACTERKEY,      # CharacterKey - needed in BOTH
    COL_DIALOGVOICE,       # DialogVoice - needed in BOTH
    COL_DIALOGTYPE,        # DialogType - needed in BOTH
]

CASTINGKEY_COLUMNS_CURRENT_ONLY = [
    COL_SPEAKER_GROUPKEY,  # Speaker|CharacterGroupKey - CURRENT only, used for BOTH
]


def validate_castingkey_columns(df, file_label="", is_current=False):
    """
    Validate that required columns for CastingKey generation exist in DataFrame.

    Args:
        df: DataFrame to validate
        file_label: Label for the file (e.g., "PREVIOUS", "CURRENT") for error messages
        is_current: True if validating CURRENT file (needs Speaker|CharacterGroupKey)

    Returns:
        tuple: (is_valid, missing_columns)
            - is_valid: True if all required columns exist
            - missing_columns: List of missing column names
    """
    # Columns needed in this file
    required = CASTINGKEY_COLUMNS_BOTH.copy()
    if is_current:
        required.extend(CASTINGKEY_COLUMNS_CURRENT_ONLY)

    missing = []
    for col in required:
        if col not in df.columns:
            missing.append(col)

    if missing:
        log(f"⚠️  WARNING: {file_label} file missing CastingKey source columns:")
        for col in missing:
            log(f"     → Missing: {col}")
        if is_current and COL_SPEAKER_GROUPKEY in missing:
            log(f"     Note: Speaker|CharacterGroupKey from CURRENT is used for BOTH files!")
        log(f"     CastingKey comparison may produce incorrect results!")
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
