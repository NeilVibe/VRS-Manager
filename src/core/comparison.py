"""
Row comparison and change classification module.

This module provides functionality to compare rows between previous and
current VRS files, classify changes, and find deleted rows using the
4-tier key system.
"""

from src.config import (
    COL_SEQUENCE, COL_EVENTNAME, COL_STRORIGIN, COL_CASTINGKEY,
    COL_DESC, COL_STARTFRAME, CHAR_GROUP_COLS
)
from src.utils.helpers import safe_str, contains_korean
from src.utils.progress import print_progress, finalize_progress


def classify_change(curr_row, prev_row, prev_lookup_cg, differences, col_idx):
    """
    Classify the type of change for a raw VRS check.

    Args:
        curr_row: Current row data (tuple)
        prev_row: Previous row data (tuple)
        prev_lookup_cg: Lookup dictionary for (SequenceName, StrOrigin) keys
        differences: List of column names that differ
        col_idx: Dictionary mapping column names to indices

    Returns:
        tuple: (change_label, changed_char_cols) where:
            - change_label: String describing the change type
            - changed_char_cols: List of character group columns that changed
    """
    key_cg = (curr_row[col_idx[COL_SEQUENCE]], curr_row[col_idx[COL_STRORIGIN]])

    if key_cg in prev_lookup_cg and prev_lookup_cg[key_cg] != curr_row[col_idx[COL_EVENTNAME]]:
        strorigin_value = curr_row[col_idx[COL_STRORIGIN]]
        if contains_korean(strorigin_value):
            if len(differences) == 1 and differences[0] == COL_EVENTNAME:
                return "EventName Change", []

    existing_char_cols = [col for col in CHAR_GROUP_COLS if col in col_idx]
    char_group_diffs = [col for col in differences if col in existing_char_cols]

    if char_group_diffs:
        return "Character Group Change", char_group_diffs

    important_changes = []
    if COL_STRORIGIN in differences:
        important_changes.append("StrOrigin")
    if COL_DESC in differences:
        important_changes.append("Desc")
    if COL_STARTFRAME in differences:
        important_changes.append("TimeFrame")

    if important_changes:
        return "+".join(important_changes) + " Change", []

    return "No Relevant Change", []


def compare_rows(df_curr, prev_lookup_cw, prev_lookup_cg, prev_lookup_es, prev_lookup_cs):
    """
    Compare rows using 4-key system for raw VRS check.

    Compares current rows against previous file using the 4-tier key system:
    1. Try (SequenceName, EventName)
    2. Try (SequenceName, StrOrigin) with CastingKey verification
    3. Try (EventName, StrOrigin)
    4. Mark as new row if none match

    Args:
        df_curr: Current DataFrame
        prev_lookup_cw: Previous lookup for (SequenceName, EventName)
        prev_lookup_cg: Previous lookup for (SequenceName, StrOrigin)
        prev_lookup_es: Previous lookup for (EventName, StrOrigin)
        prev_lookup_cs: Previous lookup for (CastingKey, SequenceName)

    Returns:
        tuple: (changes, previous_strorigins, changed_columns_map, counter) where:
            - changes: List of change labels for each row
            - previous_strorigins: List of previous StrOrigin values
            - changed_columns_map: Dict mapping row indices to changed column names
            - counter: Dict counting occurrences of each change type
    """
    changes = []
    previous_strorigins = []
    changed_columns_map = {}
    counter = {}
    col_idx = {col: i for i, col in enumerate(df_curr.columns)}
    total_rows = len(df_curr)

    for idx, curr_row in enumerate(df_curr.itertuples(index=False, name=None)):
        key_cw = (curr_row[col_idx[COL_SEQUENCE]], curr_row[col_idx[COL_EVENTNAME]])
        key_cg = (curr_row[col_idx[COL_SEQUENCE]], curr_row[col_idx[COL_STRORIGIN]])
        key_es = (curr_row[col_idx[COL_EVENTNAME]], curr_row[col_idx[COL_STRORIGIN]])
        key_cs = (curr_row[col_idx[COL_CASTINGKEY]], curr_row[col_idx[COL_SEQUENCE]])

        # Stage 1: Direct match by (Sequence, EventName)
        if key_cw in prev_lookup_cw:
            prev_row = prev_lookup_cw[key_cw]
            prev_strorigin = safe_str(prev_row[col_idx[COL_STRORIGIN]])

            differences = [
                col for col in df_curr.columns
                if safe_str(curr_row[col_idx[col]]) != safe_str(prev_row[col_idx[col]])
            ]

            if not differences:
                change_label = "No Change"
                changed_char_cols = []
            else:
                existing_char_cols = [col for col in CHAR_GROUP_COLS if col in col_idx]
                char_group_diffs = [col for col in differences if col in existing_char_cols]

                if char_group_diffs:
                    change_label = "Character Group Change"
                    changed_char_cols = char_group_diffs
                else:
                    important_changes = []
                    if COL_STRORIGIN in differences:
                        important_changes.append("StrOrigin")
                    if COL_DESC in differences:
                        important_changes.append("Desc")
                    if COL_STARTFRAME in differences:
                        important_changes.append("TimeFrame")

                    if important_changes:
                        change_label = "+".join(important_changes) + " Change"
                    else:
                        change_label = "No Relevant Change"
                    changed_char_cols = []

        # Stage 2: StrOrigin + Sequence match - VERIFY with Key 4 (4-Tier System)
        elif key_cg in prev_lookup_cg:
            # Check if same character (Key 4 verification)
            if key_cs in prev_lookup_cs:
                # Same character → EventName Change
                old_eventname = prev_lookup_cg[key_cg]
                prev_row = prev_lookup_cw.get((curr_row[col_idx[COL_SEQUENCE]], old_eventname))

                if prev_row:
                    prev_strorigin = safe_str(prev_row[col_idx[COL_STRORIGIN]])

                    differences = [
                        col for col in df_curr.columns
                        if safe_str(curr_row[col_idx[col]]) != safe_str(prev_row[col_idx[col]])
                    ]

                    important_changes = []
                    if COL_STRORIGIN in differences:
                        important_changes.append("StrOrigin")
                    if COL_DESC in differences:
                        important_changes.append("Desc")
                    if COL_STARTFRAME in differences:
                        important_changes.append("TimeFrame")

                    existing_char_cols = [col for col in CHAR_GROUP_COLS if col in col_idx]
                    char_group_diffs = [col for col in differences if col in existing_char_cols]

                    if char_group_diffs:
                        change_label = "Character Group Change"
                        changed_char_cols = char_group_diffs
                    elif not important_changes:
                        if contains_korean(curr_row[col_idx[COL_STRORIGIN]]):
                            change_label = "EventName Change"
                        else:
                            change_label = "No Relevant Change"
                        changed_char_cols = []
                    else:
                        important_changes.insert(0, "EventName")
                        change_label = "+".join(important_changes) + " Change"
                        changed_char_cols = []
                else:
                    change_label = "New Row"
                    prev_row = None
                    prev_strorigin = ""
                    changed_char_cols = []
            else:
                # Different character → New Row (duplicate StrOrigin case)
                change_label = "New Row"
                prev_row = None
                prev_strorigin = ""
                changed_char_cols = []

        # Stage 3: SequenceName changed - match by (EventName, StrOrigin)
        elif key_es in prev_lookup_es:
            prev_row = prev_lookup_es[key_es]
            prev_strorigin = safe_str(prev_row[col_idx[COL_STRORIGIN]])

            # Same content but different sequence
            change_label = "SequenceName Change"
            changed_char_cols = []

        # Stage 4: Truly new row
        else:
            change_label = "New Row"
            prev_row = None
            prev_strorigin = ""
            changed_char_cols = []

        changes.append(change_label)
        previous_strorigins.append(prev_strorigin)

        if changed_char_cols:
            changed_columns_map[idx] = changed_char_cols

        counter[change_label] = counter.get(change_label, 0) + 1

        if (idx + 1) % 500 == 0 or idx == total_rows - 1:
            print_progress(idx + 1, total_rows, "Comparing rows")

    finalize_progress()
    return changes, previous_strorigins, changed_columns_map, counter


def classify_working_change(curr_row, prev_row, prev_lookup_cg, prev_lookup_cs):
    """
    Classify change type for Working Process with 4-key system.

    Args:
        curr_row: Current row data (dict)
        prev_row: Previous row data (dict)
        prev_lookup_cg: Lookup dictionary for (SequenceName, StrOrigin) keys
        prev_lookup_cs: Lookup dictionary for (CastingKey, SequenceName) keys

    Returns:
        str: Change type label
    """
    key_cg = (curr_row[COL_SEQUENCE], curr_row[COL_STRORIGIN])
    key_cs = (curr_row[COL_CASTINGKEY], curr_row[COL_SEQUENCE])

    # Check for EventName Change with Key 4 verification
    if key_cg in prev_lookup_cg and prev_lookup_cg[key_cg] != curr_row[COL_EVENTNAME]:
        # Verify if same character (Key 4 check)
        if key_cs in prev_lookup_cs:
            # Same character → EventName Change
            strorigin_value = curr_row[COL_STRORIGIN]
            if contains_korean(strorigin_value):
                return "EventName Change"
        # Different character → Not EventName Change (will be classified as New Row elsewhere)

    differences = [col for col in curr_row.keys() if col in prev_row and curr_row[col] != prev_row[col]]

    if not differences:
        return "No Change"

    important_changes = []
    if COL_STRORIGIN in differences:
        important_changes.append("StrOrigin")
    if COL_DESC in differences:
        important_changes.append("Desc")
    if COL_STARTFRAME in differences:
        important_changes.append("TimeFrame")

    if important_changes:
        return "+".join(important_changes) + " Change"

    return "No Relevant Change"


def classify_alllang_change(curr_row, prev_row, prev_lookup_cg, prev_lookup_cs):
    """
    Classify change type for All Language Process with 4-key system.

    Similar to classify_working_change but without Desc changes
    (since Desc is not tracked in AllLang process).

    Args:
        curr_row: Current row data (dict)
        prev_row: Previous row data (dict)
        prev_lookup_cg: Lookup dictionary for (SequenceName, StrOrigin) keys
        prev_lookup_cs: Lookup dictionary for (CastingKey, SequenceName) keys

    Returns:
        str: Change type label
    """
    key_cg = (curr_row[COL_SEQUENCE], curr_row[COL_STRORIGIN])
    key_cs = (curr_row[COL_CASTINGKEY], curr_row[COL_SEQUENCE])

    # Check for EventName Change with Key 4 verification
    if key_cg in prev_lookup_cg and prev_lookup_cg[key_cg] != curr_row[COL_EVENTNAME]:
        # Verify if same character (Key 4 check)
        if key_cs in prev_lookup_cs:
            # Same character → EventName Change
            strorigin_value = curr_row[COL_STRORIGIN]
            if contains_korean(strorigin_value):
                return "EventName Change"
        # Different character → Not EventName Change (will be classified as New Row elsewhere)

    differences = [col for col in curr_row.keys() if col in prev_row and curr_row[col] != prev_row[col]]

    if not differences:
        return "No Change"

    important_changes = []
    if COL_STRORIGIN in differences:
        important_changes.append("StrOrigin")
    if COL_STARTFRAME in differences:
        important_changes.append("TimeFrame")

    if important_changes:
        return "+".join(important_changes) + " Change"

    return "No Relevant Change"


def find_deleted_rows(df_prev, df_curr):
    """
    Find deleted rows using 3-key system for raw VRS check.

    A row is only considered deleted if ALL three keys are missing from current file:
    - (SequenceName, EventName)
    - (SequenceName, StrOrigin)
    - (EventName, StrOrigin)

    Args:
        df_prev: Previous DataFrame
        df_curr: Current DataFrame

    Returns:
        DataFrame: Deleted rows
    """
    # Build all 3 key types from current
    curr_keys_cw = set((row[COL_SEQUENCE], row[COL_EVENTNAME]) for row in df_curr.to_dict("records"))
    curr_keys_cg = set((row[COL_SEQUENCE], row[COL_STRORIGIN]) for row in df_curr.to_dict("records"))
    curr_keys_es = set((row[COL_EVENTNAME], row[COL_STRORIGIN]) for row in df_curr.to_dict("records"))

    deleted_mask = []
    for row in df_prev.to_dict("records"):
        key_cw = (row[COL_SEQUENCE], row[COL_EVENTNAME])
        key_cg = (row[COL_SEQUENCE], row[COL_STRORIGIN])
        key_es = (row[COL_EVENTNAME], row[COL_STRORIGIN])

        # Only mark as deleted if ALL 3 keys are missing
        is_deleted = (key_cw not in curr_keys_cw) and \
                     (key_cg not in curr_keys_cg) and \
                     (key_es not in curr_keys_es)
        deleted_mask.append(is_deleted)

    return df_prev[deleted_mask].copy()


def find_working_deleted_rows(df_prev, df_curr):
    """
    Find deleted rows using 4-key system for Working Process.

    A row is only considered deleted if ALL four keys are missing from current file:
    - (SequenceName, EventName)
    - (SequenceName, StrOrigin)
    - (EventName, StrOrigin)
    - (CastingKey, SequenceName)

    Args:
        df_prev: Previous DataFrame
        df_curr: Current DataFrame

    Returns:
        DataFrame: Deleted rows
    """
    from src.utils.helpers import log
    import pandas as pd

    log("Finding deleted rows (PREVIOUS rows not in CURRENT)...")

    # Build all 4 key types
    curr_keys_cw = set((row[COL_SEQUENCE], row[COL_EVENTNAME]) for _, row in df_curr.iterrows())
    curr_keys_cg = set((row[COL_SEQUENCE], row[COL_STRORIGIN]) for _, row in df_curr.iterrows())
    curr_keys_es = set((row[COL_EVENTNAME], row[COL_STRORIGIN]) for _, row in df_curr.iterrows())
    curr_keys_cs = set((row[COL_CASTINGKEY], row[COL_SEQUENCE]) for _, row in df_curr.iterrows())

    deleted_rows = []

    for idx, row in df_prev.iterrows():
        key_cw = (row[COL_SEQUENCE], row[COL_EVENTNAME])
        key_cg = (row[COL_SEQUENCE], row[COL_STRORIGIN])
        key_es = (row[COL_EVENTNAME], row[COL_STRORIGIN])
        key_cs = (row[COL_CASTINGKEY], row[COL_SEQUENCE])

        # Only mark as deleted if ALL 4 keys are missing
        if (key_cw not in curr_keys_cw) and \
           (key_cg not in curr_keys_cg) and \
           (key_es not in curr_keys_es) and \
           (key_cs not in curr_keys_cs):
            deleted_rows.append(row.to_dict())

    log(f"  → Found {len(deleted_rows):,} deleted rows")
    return pd.DataFrame(deleted_rows) if deleted_rows else pd.DataFrame()
