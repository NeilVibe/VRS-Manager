"""
Universal Change Detection Module - THE SINGLE SOURCE OF TRUTH

Phase 3.1.1b: This module provides the universal change detection function
that ALL pattern matches across ALL processors must use.

Created: 2025-11-27
Purpose: Eliminate hardcoded labels and ensure consistent detection
"""

from src.config import (
    COL_SEQUENCE, COL_EVENTNAME, COL_STRORIGIN, COL_CASTINGKEY,
    COL_STARTFRAME, COL_DESC, COL_DIALOGTYPE, COL_GROUP,
    CHAR_GROUP_COLS
)
from src.utils.helpers import safe_str, contains_korean


def detect_all_field_changes(curr_row, prev_row, df_curr, df_prev, require_korean=None):
    """
    Universal change detection - detects ALL field differences.

    This function MUST be called after ANY pattern match to detect
    what actually changed between current and previous rows.

    Works for BOTH standalone and composite changes:
    - 1 field changed → "TimeFrame Change" (standalone)
    - 3 fields changed → "EventName+StrOrigin+TimeFrame Change" (composite)

    Args:
        curr_row: Current row (pandas Series or dict-like)
        prev_row: Previous row (pandas Series or dict-like) - the matched row
        df_curr: Current DataFrame (for column list)
        df_prev: Previous DataFrame (for column list)
        require_korean: If provided (StrOrigin value), return "No Relevant Change"
                       if no Korean content found. Used for filtering non-Korean rows.

    Returns:
        str: Change label, e.g.:
            - "No Change" - No differences found
            - "TimeFrame Change" - Only TimeFrame differs
            - "EventName+StrOrigin Change" - EventName and StrOrigin differ
            - "EventName+StrOrigin+TimeFrame Change" - All three differ
            - "Character Group Change" - Character group fields differ
            - "No Relevant Change" - Changes found but no Korean content

    Example:
        >>> change_label = detect_all_field_changes(curr_row, prev_row, df_curr, df_prev)
        >>> # Returns: "EventName+StrOrigin+TimeFrame Change"
    """
    # 1. Find ALL differences between current and previous rows
    common_cols = [col for col in df_curr.columns if col in df_prev.columns]
    differences = [
        col for col in common_cols
        if safe_str(curr_row.get(col, "") if hasattr(curr_row, 'get') else curr_row[col]) !=
           safe_str(prev_row.get(col, "") if hasattr(prev_row, 'get') else prev_row[col])
    ]

    # 2. Check Character Groups first (special priority - takes precedence)
    existing_char_cols = [col for col in CHAR_GROUP_COLS if col in df_curr.columns]
    char_group_diffs = [col for col in differences if col in existing_char_cols]
    if char_group_diffs:
        return "Character Group Change"

    # 3. Build change list from ACTUAL differences (CANONICAL ORDER)
    #    Order: EventName → StrOrigin → SequenceName → CastingKey → Desc → TimeFrame → DialogType → Group
    important_changes = []

    # Core keys (in canonical order)
    if COL_EVENTNAME in differences:
        important_changes.append("EventName")
    if COL_STRORIGIN in differences:
        important_changes.append("StrOrigin")
    if COL_SEQUENCE in differences:
        important_changes.append("SequenceName")
    if COL_CASTINGKEY in differences:
        important_changes.append("CastingKey")

    # Metadata fields (in canonical order)
    if COL_DESC in differences:
        important_changes.append("Desc")
    if COL_STARTFRAME in differences:
        important_changes.append("TimeFrame")
    if COL_DIALOGTYPE in differences:
        important_changes.append("DialogType")
    if COL_GROUP in differences:
        important_changes.append("Group")

    # 4. No important changes found
    if not important_changes:
        return "No Change"

    # 5. Korean relevance filter (optional)
    # Used when we want to filter out rows that don't have Korean content
    if require_korean is not None and not contains_korean(str(require_korean)):
        return "No Relevant Change"

    # 6. Build and return the change label
    return "+".join(important_changes) + " Change"


def get_changed_char_cols(curr_row, prev_row, df_curr, df_prev):
    """
    Get the list of character group columns that changed.

    Used for detailed reporting when Character Group Change is detected.

    Args:
        curr_row: Current row
        prev_row: Previous row
        df_curr: Current DataFrame
        df_prev: Previous DataFrame

    Returns:
        list: List of column names that changed (e.g., ['Tribe', 'Age'])
    """
    common_cols = [col for col in df_curr.columns if col in df_prev.columns]
    differences = [
        col for col in common_cols
        if safe_str(curr_row.get(col, "") if hasattr(curr_row, 'get') else curr_row[col]) !=
           safe_str(prev_row.get(col, "") if hasattr(prev_row, 'get') else prev_row[col])
    ]

    existing_char_cols = [col for col in CHAR_GROUP_COLS if col in df_curr.columns]
    return [col for col in differences if col in existing_char_cols]


def detect_dict_field_changes(curr_dict, prev_dict, require_korean=None):
    """
    Universal change detection for dict-based comparisons.

    Used by ALLLANG process where lookups store dicts directly.

    Args:
        curr_dict: Current row as dict
        prev_dict: Previous row as dict
        require_korean: If provided, return "No Relevant Change" if no Korean

    Returns:
        str: Change label
    """
    if prev_dict is None:
        return "New Row"

    # Find common keys
    curr_keys = set(curr_dict.keys()) if curr_dict else set()
    prev_keys = set(prev_dict.keys()) if prev_dict else set()
    common_keys = curr_keys & prev_keys

    # Find differences
    differences = [
        key for key in common_keys
        if safe_str(curr_dict.get(key, "")) != safe_str(prev_dict.get(key, ""))
    ]

    # Check Character Groups first
    char_group_diffs = [col for col in differences if col in CHAR_GROUP_COLS]
    if char_group_diffs:
        return "Character Group Change"

    # Build change list from ACTUAL differences (CANONICAL ORDER)
    #    Order: EventName → StrOrigin → SequenceName → CastingKey → Desc → TimeFrame → DialogType → Group
    important_changes = []
    if COL_EVENTNAME in differences:
        important_changes.append("EventName")
    if COL_STRORIGIN in differences:
        important_changes.append("StrOrigin")
    if COL_SEQUENCE in differences:
        important_changes.append("SequenceName")
    if COL_CASTINGKEY in differences:
        important_changes.append("CastingKey")
    if COL_DESC in differences:
        important_changes.append("Desc")
    if COL_STARTFRAME in differences:
        important_changes.append("TimeFrame")
    if COL_DIALOGTYPE in differences:
        important_changes.append("DialogType")
    if COL_GROUP in differences:
        important_changes.append("Group")

    # No important changes found
    if not important_changes:
        return "No Change"

    # Korean relevance filter
    if require_korean is not None and not contains_korean(str(require_korean)):
        return "No Relevant Change"

    return "+".join(important_changes) + " Change"
