"""
Import logic for VRS data processing.

This module handles the logic for importing data from previous files,
determining which fields to preserve based on change type and recording status.
"""

from src.config import (
    COL_TEXT, COL_DESC, COL_STATUS, COL_FREEMEMO
)
from src.utils.helpers import safe_str, is_after_recording_status


def apply_import_logic(curr_row, prev_row, change_type):
    """
    Apply import logic for Working Process.

    Determines which data to import from previous row based on change type
    and recording status.

    Args:
        curr_row: Current row data (dict)
        prev_row: Previous row data (dict) or None
        change_type: Type of change detected

    Returns:
        dict: Dictionary of columns to update in current row
    """
    result = {}

    # Always import FREEMEMO if available
    if prev_row:
        result[COL_FREEMEMO] = safe_str(prev_row.get(COL_FREEMEMO, ""))

    # New rows don't import any other data
    if change_type == "New Row":
        return result

    prev_status = prev_row.get(COL_STATUS, "") if prev_row else ""
    is_after_recording = is_after_recording_status(prev_status)

    # StrOrigin Change logic
    if "StrOrigin" in change_type:
        if is_after_recording:
            # Preserve all previous data
            result[COL_TEXT] = safe_str(prev_row.get(COL_TEXT, "")) if prev_row else ""
            result[COL_DESC] = safe_str(prev_row.get(COL_DESC, "")) if prev_row else ""
            result[COL_STATUS] = prev_status
        else:
            # Use current text, preserve desc, mark for review
            result[COL_TEXT] = safe_str(curr_row.get(COL_TEXT, ""))
            result[COL_DESC] = safe_str(prev_row.get(COL_DESC, "")) if prev_row else ""
            result[COL_STATUS] = "NEED CHECK"

    # Desc Change logic
    elif change_type == "Desc Change":
        result[COL_TEXT] = safe_str(prev_row.get(COL_TEXT, "")) if prev_row else ""
        result[COL_DESC] = safe_str(curr_row.get(COL_DESC, ""))
        result[COL_STATUS] = prev_status

    # TimeFrame Change logic
    elif "TimeFrame" in change_type:
        result[COL_TEXT] = safe_str(prev_row.get(COL_TEXT, "")) if prev_row else ""
        result[COL_DESC] = safe_str(prev_row.get(COL_DESC, "")) if prev_row else ""
        result[COL_STATUS] = prev_status

    # No change or irrelevant changes
    elif change_type in ["No Change", "No Relevant Change", "EventName Change", "SequenceName Change"]:
        result[COL_TEXT] = safe_str(prev_row.get(COL_TEXT, "")) if prev_row else ""
        result[COL_DESC] = safe_str(prev_row.get(COL_DESC, "")) if prev_row else ""
        result[COL_STATUS] = prev_status

    # Default: preserve all previous data
    else:
        result[COL_TEXT] = safe_str(prev_row.get(COL_TEXT, "")) if prev_row else ""
        result[COL_DESC] = safe_str(prev_row.get(COL_DESC, "")) if prev_row else ""
        result[COL_STATUS] = prev_status

    return result


def apply_import_logic_alllang_lang(curr_row, prev_row, change_type, lang_suffix):
    """
    Apply import logic for All Language Process (per language).

    Similar to apply_import_logic but for multi-language columns.

    Args:
        curr_row: Current row data (dict)
        prev_row: Previous row data (dict) or None
        change_type: Type of change detected
        lang_suffix: Language suffix (KR, EN, or CN)

    Returns:
        dict: Dictionary of columns to update in current row
    """
    result = {}

    text_col = f"Text_{lang_suffix}"
    status_col = f"STATUS_{lang_suffix}"
    freememo_col = f"FREEMEMO_{lang_suffix}"

    # Always import FREEMEMO if available
    if prev_row:
        result[freememo_col] = safe_str(prev_row.get(COL_FREEMEMO, ""))

    # New rows don't import any other data
    if change_type == "New Row":
        return result

    prev_status = prev_row.get(COL_STATUS, "") if prev_row else ""
    is_after_recording = is_after_recording_status(prev_status)

    # StrOrigin Change logic
    if "StrOrigin" in change_type:
        if is_after_recording:
            # Preserve previous translation
            result[text_col] = safe_str(prev_row.get(COL_TEXT, "")) if prev_row else ""
            result[status_col] = prev_status
        else:
            # Use current translation, mark for review
            result[text_col] = safe_str(curr_row.get(text_col, ""))
            result[status_col] = "NEED CHECK"

    # TimeFrame Change logic
    elif "TimeFrame" in change_type:
        result[text_col] = safe_str(prev_row.get(COL_TEXT, "")) if prev_row else ""
        result[status_col] = prev_status

    # No change or irrelevant changes
    elif change_type in ["No Change", "No Relevant Change", "EventName Change", "SequenceName Change"]:
        result[text_col] = safe_str(prev_row.get(COL_TEXT, "")) if prev_row else ""
        result[status_col] = prev_status

    # Default: preserve all previous data
    else:
        result[text_col] = safe_str(prev_row.get(COL_TEXT, "")) if prev_row else ""
        result[status_col] = prev_status

    return result
