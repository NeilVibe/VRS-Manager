"""
Working process comparison logic.

This module handles the comparison logic specific to the Working VRS Check,
including data import and PreviousData generation.
"""

import pandas as pd
from src.config import (
    COL_SEQUENCE, COL_EVENTNAME, COL_STRORIGIN, COL_CASTINGKEY,
    COL_TEXT, COL_STATUS, COL_FREEMEMO, COL_PREVIOUSDATA, COL_MAINLINE_TRANSLATION,
    COL_CHARACTERKEY, COL_DIALOGVOICE, COL_SPEAKER_GROUPKEY, COL_DESC, COL_STARTFRAME
)
from src.utils.helpers import safe_str, contains_korean, log
from src.utils.progress import print_progress, finalize_progress
from src.core.casting import generate_casting_key, generate_previous_data
from src.core.import_logic import apply_import_logic


def process_working_comparison(df_curr, prev_lookup_cw, prev_lookup_cg, prev_lookup_es, prev_lookup_cs):
    """
    Compare current data with previous using 4-key system for Working Process.

    Applies the full import logic including STATUS, Text, and Desc handling
    based on change type and recording status.

    Args:
        df_curr: Current DataFrame
        prev_lookup_cw: Previous lookup for (SequenceName, EventName)
        prev_lookup_cg: Previous lookup for (SequenceName, StrOrigin)
        prev_lookup_es: Previous lookup for (EventName, StrOrigin)
        prev_lookup_cs: Previous lookup for (CastingKey, SequenceName)

    Returns:
        tuple: (df_result, counter) where:
            - df_result: DataFrame with imported data
            - counter: Dictionary of change type counts
    """
    log("Comparing and importing data...")

    results = []
    counter = {}
    total_rows = len(df_curr)

    for idx, curr_row in df_curr.iterrows():
        curr_dict = curr_row.to_dict()
        key_cw = (curr_row[COL_SEQUENCE], curr_row[COL_EVENTNAME])
        key_cg = (curr_row[COL_SEQUENCE], curr_row[COL_STRORIGIN])
        key_es = (curr_row[COL_EVENTNAME], curr_row[COL_STRORIGIN])
        key_cs = (curr_row[COL_CASTINGKEY], curr_row[COL_SEQUENCE])

        # Save mainline translation before import
        mainline_translation = safe_str(curr_dict.get(COL_TEXT, ""))

        # Stage 1: Direct match (SequenceName + EventName)
        if key_cw in prev_lookup_cw:
            prev_row = prev_lookup_cw[key_cw]

            differences = [col for col in curr_dict.keys() if col in prev_row and curr_dict[col] != prev_row[col]]

            if not differences:
                change_type = "No Change"
            else:
                important_changes = []
                if COL_STRORIGIN in differences:
                    important_changes.append("StrOrigin")
                if COL_DESC in differences:
                    important_changes.append("Desc")
                if COL_STARTFRAME in differences:
                    important_changes.append("TimeFrame")

                if important_changes:
                    change_type = "+".join(important_changes) + " Change"
                else:
                    change_type = "No Relevant Change"

        # Stage 2: StrOrigin+Sequence match - VERIFY with Key 4
        elif key_cg in prev_lookup_cg:
            # Check if same character (Key 4 verification)
            if key_cs in prev_lookup_cs:
                # Same character → EventName Change
                old_eventname = prev_lookup_cg[key_cg]
                prev_row = prev_lookup_cw.get((curr_row[COL_SEQUENCE], old_eventname))

                if prev_row:
                    differences = [col for col in curr_dict.keys() if col in prev_row and curr_dict[col] != prev_row[col]]

                    important_changes = []
                    if COL_STRORIGIN in differences:
                        important_changes.append("StrOrigin")
                    if COL_DESC in differences:
                        important_changes.append("Desc")
                    if COL_STARTFRAME in differences:
                        important_changes.append("TimeFrame")

                    if not important_changes:
                        if contains_korean(curr_row[COL_STRORIGIN]):
                            change_type = "EventName Change"
                        else:
                            change_type = "No Relevant Change"
                    else:
                        important_changes.insert(0, "EventName")
                        change_type = "+".join(important_changes) + " Change"
                else:
                    change_type = "New Row"
                    prev_row = None
            else:
                # Different character → New Row (duplicate StrOrigin case)
                change_type = "New Row"
                prev_row = None

        # Stage 3: SequenceName changed (EventName + StrOrigin match)
        elif key_es in prev_lookup_es:
            prev_row = prev_lookup_es[key_es]
            change_type = "SequenceName Change"

        # Stage 4: Truly new (no keys match)
        else:
            change_type = "New Row"
            prev_row = None

        # Apply import logic
        import_data = apply_import_logic(curr_dict, prev_row, change_type)

        for col, value in import_data.items():
            curr_dict[col] = value

        # Generate CastingKey
        curr_dict[COL_CASTINGKEY] = generate_casting_key(
            curr_dict.get(COL_CHARACTERKEY, ""),
            curr_dict.get(COL_DIALOGVOICE, ""),
            curr_dict.get(COL_SPEAKER_GROUPKEY, ""),
            curr_dict.get("DialogType", "")
        )

        # Generate PreviousData
        curr_dict[COL_PREVIOUSDATA] = generate_previous_data(
            prev_row, COL_TEXT, COL_STATUS, COL_FREEMEMO
        )

        # Set special columns
        curr_dict[COL_MAINLINE_TRANSLATION] = mainline_translation
        curr_dict["CHANGES"] = change_type

        results.append(curr_dict)
        counter[change_type] = counter.get(change_type, 0) + 1

        if (idx + 1) % 500 == 0 or idx == total_rows - 1:
            print_progress(idx + 1, total_rows, "Processing rows")

    finalize_progress()
    return pd.DataFrame(results), counter
