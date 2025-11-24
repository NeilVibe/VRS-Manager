"""
Working process comparison logic.

This module handles the comparison logic specific to the Working VRS Check,
including data import and PreviousData generation using the TWO-PASS 10-key system.
"""

import pandas as pd
from src.config import (
    COL_SEQUENCE, COL_EVENTNAME, COL_STRORIGIN, COL_CASTINGKEY,
    COL_TEXT, COL_STATUS, COL_FREEMEMO, COL_PREVIOUSDATA, COL_MAINLINE_TRANSLATION,
    COL_CHARACTERKEY, COL_DIALOGVOICE, COL_SPEAKER_GROUPKEY, COL_DESC, COL_STARTFRAME,
    COL_DIALOGTYPE, COL_GROUP
)
from src.utils.helpers import safe_str, contains_korean, log, generate_previous_data
from src.utils.progress import print_progress, finalize_progress
from src.core.casting import generate_casting_key
from src.core.import_logic import apply_import_logic


def process_working_comparison(df_curr, df_prev, prev_lookup_se, prev_lookup_so, prev_lookup_sc,
                                prev_lookup_eo, prev_lookup_ec, prev_lookup_oc,
                                prev_lookup_seo, prev_lookup_sec, prev_lookup_soc, prev_lookup_eoc):
    """
    Compare current data with previous using TWO-PASS 10-key system for Working Process.

    TWO-PASS ALGORITHM prevents 1-to-many matching issues:
    - PASS 1: Detect and mark No Change/New rows (certainties)
    - PASS 2: Detect partial changes using only UNMARKED previous rows

    Applies the full import logic including STATUS, Text, and Desc handling
    based on change type and recording status.

    Args:
        df_curr: Current DataFrame
        df_prev: Previous DataFrame (needed to retrieve rows by index)
        prev_lookup_se: Previous lookup for (Sequence, Event) → DataFrame index
        prev_lookup_so: Previous lookup for (Sequence, StrOrigin) → DataFrame index
        prev_lookup_sc: Previous lookup for (Sequence, CastingKey) → DataFrame index
        prev_lookup_eo: Previous lookup for (Event, StrOrigin) → DataFrame index
        prev_lookup_ec: Previous lookup for (Event, CastingKey) → DataFrame index
        prev_lookup_oc: Previous lookup for (StrOrigin, CastingKey) → DataFrame index
        prev_lookup_seo: Previous lookup for (Sequence, Event, StrOrigin) → DataFrame index
        prev_lookup_sec: Previous lookup for (Sequence, Event, CastingKey) → DataFrame index
        prev_lookup_soc: Previous lookup for (Sequence, StrOrigin, CastingKey) → DataFrame index
        prev_lookup_eoc: Previous lookup for (Event, StrOrigin, CastingKey) → DataFrame index

    Returns:
        tuple: (df_result, counter, marked_prev_indices, pass1_results) where:
            - df_result: DataFrame with imported data
            - counter: Dictionary of change type counts
            - marked_prev_indices: Set of previous DataFrame indices that were matched
            - pass1_results: Dictionary of PASS 1 results (needed for Super Group Word Analysis)
    """
    log("Comparing and importing data (TWO-PASS algorithm)...")

    marked_prev_indices = set()
    total_rows = len(df_curr)

    # ========================================
    # PASS 1: Detect No Change and New rows
    # ========================================
    pass1_results = {}  # curr_idx → (change_type, prev_idx_or_none)

    progress_count = 0
    for curr_idx, curr_row in df_curr.iterrows():
        S = safe_str(curr_row.get(COL_SEQUENCE, ""))
        E = safe_str(curr_row.get(COL_EVENTNAME, ""))
        O = safe_str(curr_row.get(COL_STRORIGIN, ""))
        C = safe_str(curr_row.get(COL_CASTINGKEY, ""))

        # Defensive check: ensure all values are strings
        if isinstance(S, dict) or isinstance(E, dict) or isinstance(O, dict) or isinstance(C, dict):
            log(f"ERROR at row {curr_idx}: Found dict value in keys!")
            if isinstance(S, dict):
                log(f"  SequenceName is dict: {S}")
            if isinstance(E, dict):
                log(f"  EventName is dict: {E}")
            if isinstance(O, dict):
                log(f"  StrOrigin is dict: {O}")
            if isinstance(C, dict):
                log(f"  CastingKey is dict: {C}")
            raise TypeError(f"Row {curr_idx} contains dict value in key columns. Check Excel file for corrupted data.")

        # Generate all 10 keys
        key_se = (S, E)
        key_so = (S, O)
        key_sc = (S, C)
        key_eo = (E, O)
        key_ec = (E, C)
        key_oc = (O, C)
        key_seo = (S, E, O)
        key_sec = (S, E, C)
        key_soc = (S, O, C)
        key_eoc = (E, O, C)

        # Check for perfect 4-key match (No Change)
        if key_seo in prev_lookup_seo:
            prev_idx = prev_lookup_seo[key_seo]
            if prev_idx not in marked_prev_indices:
                prev_row = df_prev.loc[prev_idx]
                prev_S = safe_str(prev_row.get(COL_SEQUENCE, ""))
                prev_E = safe_str(prev_row.get(COL_EVENTNAME, ""))
                prev_O = safe_str(prev_row.get(COL_STRORIGIN, ""))
                prev_C = safe_str(prev_row.get(COL_CASTINGKEY, ""))
                prev_strorigin = safe_str(prev_row.get(COL_STRORIGIN, ""))

                # Perfect match: All 4 keys identical
                if S == prev_S and E == prev_E and O == prev_O and C == prev_C:
                    marked_prev_indices.add(prev_idx)
                    pass1_results[curr_idx] = ("No Change", prev_idx, prev_strorigin, [])

        # Check if NEW row (all 10 keys missing)
        if curr_idx not in pass1_results:
            if (key_se not in prev_lookup_se) and \
               (key_so not in prev_lookup_so) and \
               (key_sc not in prev_lookup_sc) and \
               (key_eo not in prev_lookup_eo) and \
               (key_ec not in prev_lookup_ec) and \
               (key_oc not in prev_lookup_oc) and \
               (key_seo not in prev_lookup_seo) and \
               (key_sec not in prev_lookup_sec) and \
               (key_soc not in prev_lookup_soc) and \
               (key_eoc not in prev_lookup_eoc):
                pass1_results[curr_idx] = ("New Row", None, "", [])

        progress_count += 1
        if progress_count % 500 == 0 or progress_count == total_rows:
            print_progress(progress_count, total_rows, "PASS 1: Detecting certainties")

    finalize_progress()

    # ========================================
    # PASS 2: Detect partial changes using UNMARKED rows
    # ========================================
    progress_count = 0
    for curr_idx, curr_row in df_curr.iterrows():
        # Skip if already classified in PASS 1
        if curr_idx in pass1_results:
            progress_count += 1
            if progress_count % 500 == 0 or progress_count == total_rows:
                print_progress(progress_count, total_rows, "PASS 2: Detecting changes")
            continue

        S = safe_str(curr_row.get(COL_SEQUENCE, ""))
        E = safe_str(curr_row.get(COL_EVENTNAME, ""))
        O = safe_str(curr_row.get(COL_STRORIGIN, ""))
        C = safe_str(curr_row.get(COL_CASTINGKEY, ""))

        # Defensive check: ensure all values are strings
        if isinstance(S, dict) or isinstance(E, dict) or isinstance(O, dict) or isinstance(C, dict):
            log(f"ERROR at row {curr_idx}: Found dict value in keys!")
            if isinstance(S, dict):
                log(f"  SequenceName is dict: {S}")
            if isinstance(E, dict):
                log(f"  EventName is dict: {E}")
            if isinstance(O, dict):
                log(f"  StrOrigin is dict: {O}")
            if isinstance(C, dict):
                log(f"  CastingKey is dict: {C}")
            raise TypeError(f"Row {curr_idx} contains dict value in key columns. Check Excel file for corrupted data.")

        # Generate all 10 keys
        key_se = (S, E)
        key_so = (S, O)
        key_sc = (S, C)
        key_eo = (E, O)
        key_ec = (E, C)
        key_oc = (O, C)
        key_seo = (S, E, O)
        key_sec = (S, E, C)
        key_soc = (S, O, C)
        key_eoc = (E, O, C)

        matched = False
        change_type = None
        prev_idx = None

        # LEVEL 1: 3-Key Matches (One field changed)
        if not matched and key_seo in prev_lookup_seo:
            candidate_idx = prev_lookup_seo[key_seo]
            if candidate_idx not in marked_prev_indices:
                prev_row = df_prev.loc[candidate_idx]
                prev_castingkey = safe_str(safe_str(prev_row.get(COL_CASTINGKEY, "")))

                if C == prev_castingkey:
                    change_type = "No Change"
                else:
                    change_type = "CastingKey Change"

                prev_idx = candidate_idx
                marked_prev_indices.add(candidate_idx)
                matched = True

        if not matched and key_sec in prev_lookup_sec:
            candidate_idx = prev_lookup_sec[key_sec]
            if candidate_idx not in marked_prev_indices:
                prev_row = df_prev.loc[candidate_idx]

                # Check for StrOrigin and other field changes
                # Only compare columns that exist in BOTH dataframes
                common_cols = [col for col in df_curr.columns if col in df_prev.columns]
                differences = [
                    col for col in common_cols
                    if safe_str(curr_row[col]) != safe_str(prev_row[col])
                ]

                # Build important changes list
                important_changes = []
                if COL_STRORIGIN in differences:
                    important_changes.append("StrOrigin")
                if COL_DESC in differences:
                    important_changes.append("Desc")
                if COL_STARTFRAME in differences:
                    important_changes.append("TimeFrame")
                if COL_DIALOGTYPE in differences:
                    important_changes.append("DialogType")
                if COL_GROUP in differences:
                    important_changes.append("Group")

                if important_changes:
                    change_type = "+".join(important_changes) + " Change"
                else:
                    change_type = "No Change"

                prev_idx = candidate_idx
                marked_prev_indices.add(candidate_idx)
                matched = True

        if not matched and key_soc in prev_lookup_soc:
            candidate_idx = prev_lookup_soc[key_soc]
            if candidate_idx not in marked_prev_indices:
                prev_row = df_prev.loc[candidate_idx]

                if contains_korean(O):
                    change_type = "EventName Change"
                else:
                    change_type = "No Relevant Change"

                prev_idx = candidate_idx
                marked_prev_indices.add(candidate_idx)
                matched = True

        if not matched and key_eoc in prev_lookup_eoc:
            candidate_idx = prev_lookup_eoc[key_eoc]
            if candidate_idx not in marked_prev_indices:
                prev_row = df_prev.loc[candidate_idx]
                change_type = "SequenceName Change"
                prev_idx = candidate_idx
                marked_prev_indices.add(candidate_idx)
                matched = True

        # LEVEL 2: 2-Key Matches (Two+ fields changed)
        if not matched and key_se in prev_lookup_se:
            candidate_idx = prev_lookup_se[key_se]
            if candidate_idx not in marked_prev_indices:
                prev_row = df_prev.loc[candidate_idx]

                # Only compare columns that exist in BOTH dataframes
                common_cols = [col for col in df_curr.columns if col in df_prev.columns]
                differences = [
                    col for col in common_cols
                    if safe_str(curr_row[col]) != safe_str(prev_row[col])
                ]

                # Check for Character Group changes first (highest priority for SE match)
                from src.config import CHAR_GROUP_COLS
                char_group_diffs = [col for col in differences if col in CHAR_GROUP_COLS]
                if char_group_diffs:
                    change_type = "Character Group Change"
                else:
                    # Build important changes list
                    important_changes = []
                    if COL_STRORIGIN in differences:
                        important_changes.append("StrOrigin")
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

                    if important_changes:
                        change_type = "+".join(important_changes) + " Change"
                    else:
                        change_type = "No Change"

                prev_idx = candidate_idx
                marked_prev_indices.add(candidate_idx)
                matched = True

        if not matched and key_oc in prev_lookup_oc:
            candidate_idx = prev_lookup_oc[key_oc]
            if candidate_idx not in marked_prev_indices:
                prev_row = df_prev.loc[candidate_idx]
                changes = []
                if S != safe_str(prev_row.get(COL_SEQUENCE, "")):
                    changes.append("SequenceName")
                if E != safe_str(prev_row.get(COL_EVENTNAME, "")):
                    changes.append("EventName")

                change_type = "+".join(changes) + " Change" if changes else "No Relevant Change"
                prev_idx = candidate_idx
                marked_prev_indices.add(candidate_idx)
                matched = True

        if not matched and key_ec in prev_lookup_ec:
            candidate_idx = prev_lookup_ec[key_ec]
            if candidate_idx not in marked_prev_indices:
                prev_row = df_prev.loc[candidate_idx]
                changes = []
                if S != safe_str(prev_row.get(COL_SEQUENCE, "")):
                    changes.append("SequenceName")
                if O != safe_str(prev_row.get(COL_STRORIGIN, "")):
                    changes.append("StrOrigin")

                change_type = "+".join(changes) + " Change" if changes else "No Relevant Change"
                prev_idx = candidate_idx
                marked_prev_indices.add(candidate_idx)
                matched = True

        if not matched and key_sc in prev_lookup_sc:
            candidate_idx = prev_lookup_sc[key_sc]
            if candidate_idx not in marked_prev_indices:
                prev_row = df_prev.loc[candidate_idx]
                change_type = "EventName+StrOrigin Change"
                prev_idx = candidate_idx
                marked_prev_indices.add(candidate_idx)
                matched = True

        if not matched and key_so in prev_lookup_so:
            candidate_idx = prev_lookup_so[key_so]
            if candidate_idx not in marked_prev_indices:
                prev_row = df_prev.loc[candidate_idx]
                old_eventname = safe_str(prev_row.get(COL_EVENTNAME, ""))

                changes = []
                if E != old_eventname:
                    changes.append("EventName")
                if C != safe_str(prev_row.get(COL_CASTINGKEY, "")):
                    changes.append("CastingKey")

                if changes and contains_korean(O):
                    change_type = "+".join(changes) + " Change"
                else:
                    change_type = "No Relevant Change"

                prev_idx = candidate_idx
                marked_prev_indices.add(candidate_idx)
                matched = True

        if not matched and key_eo in prev_lookup_eo:
            candidate_idx = prev_lookup_eo[key_eo]
            if candidate_idx not in marked_prev_indices:
                prev_row = df_prev.loc[candidate_idx]
                change_type = "SequenceName Change"
                prev_idx = candidate_idx
                marked_prev_indices.add(candidate_idx)
                matched = True

        # If no match found in PASS 2, it's a NEW row
        if not matched:
            change_type = "New Row"
            prev_idx = None
            prev_strorigin = ""
        else:
            # Extract previous StrOrigin from matched row
            prev_row = df_prev.loc[prev_idx]
            prev_strorigin = safe_str(prev_row.get(COL_STRORIGIN, ""))

        # Store PASS 2 result
        pass1_results[curr_idx] = (change_type, prev_idx, prev_strorigin, [])

        progress_count += 1
        if progress_count % 500 == 0 or progress_count == total_rows:
            print_progress(progress_count, total_rows, "PASS 2: Detecting changes")

    finalize_progress()

    # ========================================
    # Apply import logic to all rows
    # ========================================
    log("Applying import logic...")
    results = []
    counter = {}
    previous_strorigins = []

    for curr_idx, curr_row in df_curr.iterrows():
        curr_dict = curr_row.to_dict()

        # Get detection result
        if curr_idx in pass1_results:
            change_type, prev_idx, prev_strorigin, _ = pass1_results[curr_idx]
            previous_strorigins.append(prev_strorigin)
        else:
            # Shouldn't happen
            change_type = "ERROR: Missing Classification"
            prev_idx = None
            prev_strorigin = ""
            previous_strorigins.append(prev_strorigin)

        # Get previous row if matched
        prev_row_dict = df_prev.loc[prev_idx].to_dict() if prev_idx is not None else None

        # Save mainline translation before import
        mainline_translation = safe_str(curr_dict.get(COL_TEXT, ""))

        # Apply import logic
        import_data = apply_import_logic(curr_dict, prev_row_dict, change_type)

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
            prev_row_dict, COL_TEXT, COL_STATUS, COL_FREEMEMO
        )

        # Check for DialogType and Group changes (post-processing safety net)
        # This catches DialogType/Group changes for pattern matches that don't check these fields
        if prev_row_dict is not None and change_type != "New Row":
            metadata_changes = []

            # Check DialogType change (only if not already detected)
            if "DialogType" not in change_type:
                curr_dialogtype = safe_str(curr_dict.get(COL_DIALOGTYPE, ""))
                prev_dialogtype = safe_str(prev_row_dict.get(COL_DIALOGTYPE, ""))
                if curr_dialogtype != prev_dialogtype:
                    metadata_changes.append("DialogType")

            # Check Group change (only if not already detected)
            if "Group" not in change_type:
                curr_group = safe_str(curr_dict.get(COL_GROUP, ""))
                prev_group = safe_str(prev_row_dict.get(COL_GROUP, ""))
                if curr_group != prev_group:
                    metadata_changes.append("Group")

            # Add metadata changes to change_type
            if metadata_changes:
                if change_type == "No Change":
                    # Only metadata changed
                    change_type = "+".join(metadata_changes) + " Change"
                else:
                    # Composite: existing changes + metadata changes
                    # Remove " Change" suffix, add metadata, re-add " Change"
                    if change_type.endswith(" Change"):
                        base_changes = change_type[:-7]  # Remove " Change"
                        all_changes = base_changes + "+" + "+".join(metadata_changes)
                        change_type = all_changes + " Change"

        # Set special columns
        curr_dict[COL_MAINLINE_TRANSLATION] = mainline_translation
        curr_dict["CHANGES"] = change_type

        results.append(curr_dict)
        counter[change_type] = counter.get(change_type, 0) + 1

    return pd.DataFrame(results), counter, marked_prev_indices, pass1_results, previous_strorigins
