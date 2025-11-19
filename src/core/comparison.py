"""
Row comparison and change classification module.

This module provides functionality to compare rows between previous and
current VRS files, classify changes, and find deleted rows using the
TWO-PASS 10-key system.
"""

from src.config import (
    COL_SEQUENCE, COL_EVENTNAME, COL_STRORIGIN, COL_CASTINGKEY,
    COL_DESC, COL_STARTFRAME, COL_GROUP, COL_DIALOGTYPE, CHAR_GROUP_COLS
)
from src.utils.helpers import safe_str, contains_korean
from src.utils.progress import print_progress, finalize_progress


def compare_rows(df_curr, df_prev, prev_lookup_se, prev_lookup_so, prev_lookup_sc, prev_lookup_eo,
                 prev_lookup_ec, prev_lookup_oc, prev_lookup_seo, prev_lookup_sec,
                 prev_lookup_soc, prev_lookup_eoc):
    """
    Compare rows using TWO-PASS algorithm with 10-key pattern matching.

    TWO-PASS ALGORITHM prevents 1-to-many matching issues:
    - PASS 1: Detect and mark No Change/New rows (certainties)
    - PASS 2: Detect partial changes using only UNMARKED previous rows

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
        tuple: (changes, previous_strorigins, changed_columns_map, counter, marked_prev_indices, group_analysis, pass1_results)
    """
    changes = []
    previous_strorigins = []
    changed_columns_map = {}
    counter = {}
    marked_prev_indices = set()  # Track which previous rows are "used"
    group_analysis = {}  # NEW: Track word counts per group
    total_rows = len(df_curr)

    # ========================================
    # PASS 1: Detect No Change and New rows
    # ========================================
    pass1_results = {}  # curr_idx → (change_label, prev_idx_or_none, prev_strorigin, char_cols)

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

        # Check for perfect 4-key match (No Change or metadata-only changes)
        if key_seo in prev_lookup_seo:
            prev_idx = prev_lookup_seo[key_seo]
            if prev_idx not in marked_prev_indices:
                prev_row = df_prev.loc[prev_idx]
                prev_S = safe_str(prev_row.get(COL_SEQUENCE, ""))
                prev_E = safe_str(prev_row.get(COL_EVENTNAME, ""))
                prev_O = safe_str(prev_row.get(COL_STRORIGIN, ""))
                prev_C = safe_str(prev_row.get(COL_CASTINGKEY, ""))

                # Perfect match: All 4 keys identical
                if S == prev_S and E == prev_E and O == prev_O and C == prev_C:
                    # Check for DialogType and Group changes
                    metadata_changes = []
                    if COL_DIALOGTYPE in curr_row.index and COL_DIALOGTYPE in prev_row.index:
                        if safe_str(curr_row[COL_DIALOGTYPE]) != safe_str(prev_row[COL_DIALOGTYPE]):
                            metadata_changes.append("DialogType")
                    if COL_GROUP in curr_row.index and COL_GROUP in prev_row.index:
                        if safe_str(curr_row[COL_GROUP]) != safe_str(prev_row[COL_GROUP]):
                            metadata_changes.append("Group")

                    if metadata_changes:
                        change_label = "+".join(metadata_changes) + " Change"
                    else:
                        change_label = "No Change"

                    marked_prev_indices.add(prev_idx)
                    pass1_results[curr_idx] = (change_label, prev_idx, safe_str(prev_O), [])

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
        change_label = None
        prev_idx = None
        prev_strorigin = ""
        changed_char_cols = []

        # LEVEL 1: 3-Key Matches (One field changed)
        if not matched and key_seo in prev_lookup_seo:
            # Same Sequence, Event, StrOrigin → Check if CastingKey changed
            candidate_idx = prev_lookup_seo[key_seo]
            if candidate_idx not in marked_prev_indices:
                prev_row = df_prev.loc[candidate_idx]
                prev_strorigin = safe_str(safe_str(prev_row.get(COL_STRORIGIN, "")))
                prev_castingkey = safe_str(safe_str(prev_row.get(COL_CASTINGKEY, "")))

                if C == prev_castingkey:
                    # Check for DialogType and Group changes
                    metadata_changes = []
                    if COL_DIALOGTYPE in curr_row.index and COL_DIALOGTYPE in prev_row.index:
                        if safe_str(curr_row[COL_DIALOGTYPE]) != safe_str(prev_row[COL_DIALOGTYPE]):
                            metadata_changes.append("DialogType")
                    if COL_GROUP in curr_row.index and COL_GROUP in prev_row.index:
                        if safe_str(curr_row[COL_GROUP]) != safe_str(prev_row[COL_GROUP]):
                            metadata_changes.append("Group")

                    if metadata_changes:
                        change_label = "+".join(metadata_changes) + " Change"
                    else:
                        change_label = "No Change"
                else:
                    change_label = "CastingKey Change"

                prev_idx = candidate_idx
                marked_prev_indices.add(candidate_idx)  # Mark as matched
                matched = True

        if not matched and key_sec in prev_lookup_sec:
            # Same Sequence, Event, CastingKey → StrOrigin changed
            candidate_idx = prev_lookup_sec[key_sec]
            if candidate_idx not in marked_prev_indices:
                prev_row = df_prev.loc[candidate_idx]
                prev_strorigin = safe_str(safe_str(prev_row.get(COL_STRORIGIN, "")))

                # Only compare columns that exist in BOTH dataframes
                common_cols = [col for col in df_curr.columns if col in df_prev.columns]
                differences = [
                    col for col in common_cols
                    if safe_str(curr_row[col]) != safe_str(prev_row[col])
                ]

                # Check for composite changes
                important_changes = ["StrOrigin"]
                if COL_DESC in differences:
                    important_changes.append("Desc")
                if COL_STARTFRAME in differences:
                    important_changes.append("TimeFrame")
                if COL_DIALOGTYPE in differences:
                    important_changes.append("DialogType")
                if COL_GROUP in differences:
                    important_changes.append("Group")

                change_label = "+".join(important_changes) + " Change"
                prev_idx = candidate_idx
                marked_prev_indices.add(candidate_idx)  # Mark as matched
                matched = True

        if not matched and key_soc in prev_lookup_soc:
            # Same Sequence, StrOrigin, CastingKey → EventName changed
            candidate_idx = prev_lookup_soc[key_soc]
            if candidate_idx not in marked_prev_indices:
                prev_row = df_prev.loc[candidate_idx]
                prev_strorigin = safe_str(safe_str(prev_row.get(COL_STRORIGIN, "")))

                if contains_korean(O):
                    change_label = "EventName Change"
                else:
                    change_label = "No Relevant Change"

                prev_idx = candidate_idx
                marked_prev_indices.add(candidate_idx)  # Mark as matched
                matched = True

        if not matched and key_eoc in prev_lookup_eoc:
            # Same Event, StrOrigin, CastingKey → SequenceName changed
            candidate_idx = prev_lookup_eoc[key_eoc]
            if candidate_idx not in marked_prev_indices:
                prev_row = df_prev.loc[candidate_idx]
                prev_strorigin = safe_str(safe_str(prev_row.get(COL_STRORIGIN, "")))
                change_label = "SequenceName Change"
                prev_idx = candidate_idx
                marked_prev_indices.add(candidate_idx)  # Mark as matched
                matched = True

        # LEVEL 2: 2-Key Matches (Two+ fields changed)
        if not matched and key_se in prev_lookup_se:
            # Same Sequence + Event
            candidate_idx = prev_lookup_se[key_se]
            if candidate_idx not in marked_prev_indices:
                prev_row = df_prev.loc[candidate_idx]
                prev_strorigin = safe_str(safe_str(prev_row.get(COL_STRORIGIN, "")))

                # Only compare columns that exist in BOTH dataframes
                common_cols = [col for col in df_curr.columns if col in df_prev.columns]
                differences = [
                    col for col in common_cols
                    if safe_str(curr_row[col]) != safe_str(prev_row[col])
                ]

                # Check for char group changes first
                existing_char_cols = [col for col in CHAR_GROUP_COLS if col in df_curr.columns]
                char_group_diffs = [col for col in differences if col in existing_char_cols]

                if char_group_diffs:
                    change_label = "Character Group Change"
                    changed_char_cols = char_group_diffs
                else:
                    # Build composite change list
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

                    if not important_changes:
                        change_label = "No Change"
                    else:
                        change_label = "+".join(important_changes) + " Change"

                prev_idx = candidate_idx
                marked_prev_indices.add(candidate_idx)  # Mark as matched
                matched = True

        if not matched and key_oc in prev_lookup_oc:
            # Same StrOrigin + CastingKey → Sequence and/or Event changed
            candidate_idx = prev_lookup_oc[key_oc]
            if candidate_idx not in marked_prev_indices:
                prev_row = df_prev.loc[candidate_idx]
                prev_strorigin = safe_str(safe_str(prev_row.get(COL_STRORIGIN, "")))

                changes_list = []
                if S != safe_str(prev_row.get(COL_SEQUENCE, "")):
                    changes_list.append("SequenceName")
                if E != safe_str(prev_row.get(COL_EVENTNAME, "")):
                    changes_list.append("EventName")

                change_label = "+".join(changes_list) + " Change" if changes_list else "No Relevant Change"
                prev_idx = candidate_idx
                marked_prev_indices.add(candidate_idx)  # Mark as matched
                matched = True

        if not matched and key_ec in prev_lookup_ec:
            # Same Event + CastingKey → Sequence and/or StrOrigin changed
            candidate_idx = prev_lookup_ec[key_ec]
            if candidate_idx not in marked_prev_indices:
                prev_row = df_prev.loc[candidate_idx]
                prev_strorigin = safe_str(safe_str(prev_row.get(COL_STRORIGIN, "")))

                changes_list = []
                if S != safe_str(prev_row.get(COL_SEQUENCE, "")):
                    changes_list.append("SequenceName")
                if O != safe_str(prev_row.get(COL_STRORIGIN, "")):
                    changes_list.append("StrOrigin")

                change_label = "+".join(changes_list) + " Change" if changes_list else "No Relevant Change"
                prev_idx = candidate_idx
                marked_prev_indices.add(candidate_idx)  # Mark as matched
                matched = True

        if not matched and key_sc in prev_lookup_sc:
            # Same Sequence + CastingKey → Event and/or StrOrigin changed
            candidate_idx = prev_lookup_sc[key_sc]
            if candidate_idx not in marked_prev_indices:
                prev_row = df_prev.loc[candidate_idx]
                prev_strorigin = safe_str(safe_str(prev_row.get(COL_STRORIGIN, "")))
                change_label = "EventName+StrOrigin Change"
                prev_idx = candidate_idx
                marked_prev_indices.add(candidate_idx)  # Mark as matched
                matched = True

        if not matched and key_so in prev_lookup_so:
            # Same Sequence + StrOrigin → Event and/or CastingKey changed
            candidate_idx = prev_lookup_so[key_so]
            if candidate_idx not in marked_prev_indices:
                prev_row = df_prev.loc[candidate_idx]
                prev_strorigin = safe_str(safe_str(prev_row.get(COL_STRORIGIN, "")))
                old_eventname = safe_str(prev_row.get(COL_EVENTNAME, ""))

                changes_list = []
                if E != old_eventname:
                    changes_list.append("EventName")
                if C != safe_str(prev_row.get(COL_CASTINGKEY, "")):
                    changes_list.append("CastingKey")

                if changes_list and contains_korean(O):
                    change_label = "+".join(changes_list) + " Change"
                else:
                    change_label = "No Relevant Change"

                prev_idx = candidate_idx
                marked_prev_indices.add(candidate_idx)  # Mark as matched
                matched = True

        if not matched and key_eo in prev_lookup_eo:
            # Same Event + StrOrigin → SequenceName and/or CastingKey changed
            candidate_idx = prev_lookup_eo[key_eo]
            if candidate_idx not in marked_prev_indices:
                prev_row = df_prev.loc[candidate_idx]
                prev_strorigin = safe_str(safe_str(prev_row.get(COL_STRORIGIN, "")))
                change_label = "SequenceName Change"  # Most common case
                prev_idx = candidate_idx
                marked_prev_indices.add(candidate_idx)  # Mark as matched
                matched = True

        # If no match found in PASS 2, it's a NEW row
        if not matched:
            change_label = "New Row"
            prev_idx = None
            prev_strorigin = ""
            changed_char_cols = []

        # Store PASS 2 result
        pass1_results[curr_idx] = (change_label, prev_idx, prev_strorigin, changed_char_cols)

        progress_count += 1
        if progress_count % 500 == 0 or progress_count == total_rows:
            print_progress(progress_count, total_rows, "PASS 2: Detecting changes")

    finalize_progress()

    # ========================================
    # Consolidate results from both passes
    # ========================================
    for curr_idx in df_curr.index:
        if curr_idx in pass1_results:
            change_label, prev_idx, prev_strorigin, char_cols = pass1_results[curr_idx]
            changes.append(change_label)
            previous_strorigins.append(prev_strorigin)

            if char_cols:
                changed_columns_map[curr_idx] = char_cols

            counter[change_label] = counter.get(change_label, 0) + 1
        else:
            # Shouldn't happen, but fallback
            changes.append("ERROR: Missing Classification")
            previous_strorigins.append("")
            counter["ERROR: Missing Classification"] = counter.get("ERROR: Missing Classification", 0) + 1

    # ========================================
    # NEW: Group-level word count analysis
    # ========================================
    def _init_group_stats():
        """Initialize group statistics dictionary."""
        return {
            "total_words_prev": 0,
            "total_words_curr": 0,
            "deleted_words": 0,
            "added_words": 0,
            "changed_words": 0,
            "unchanged_words": 0,
            "migrated_in_words": 0,
            "migrated_out_words": 0
        }

    # Process current rows for group analysis
    for curr_idx, curr_row in df_curr.iterrows():
        curr_group = safe_str(curr_row.get(COL_GROUP, "Unknown"))
        curr_strorigin = safe_str(curr_row.get(COL_STRORIGIN, ""))
        curr_words = len(curr_strorigin.split()) if curr_strorigin else 0

        # Initialize group if not exists
        if curr_group not in group_analysis:
            group_analysis[curr_group] = _init_group_stats()

        # Get classification for this row
        change_label, prev_idx, prev_strorigin, _ = pass1_results.get(curr_idx, (None, None, "", []))

        if change_label == "New Row":
            # New row in this group
            group_analysis[curr_group]["added_words"] += curr_words
            group_analysis[curr_group]["total_words_curr"] += curr_words

        elif prev_idx is not None:
            # Row matched to previous
            prev_row = df_prev.loc[prev_idx]
            prev_group = safe_str(prev_row.get(COL_GROUP, "Unknown"))
            prev_strorigin_text = safe_str(prev_row.get(COL_STRORIGIN, ""))
            prev_words = len(prev_strorigin_text.split()) if prev_strorigin_text else 0

            # Initialize previous group if needed
            if prev_group not in group_analysis:
                group_analysis[prev_group] = _init_group_stats()

            # Add to previous group total
            group_analysis[prev_group]["total_words_prev"] += prev_words

            # Add to current group total
            group_analysis[curr_group]["total_words_curr"] += curr_words

            if curr_group == prev_group:
                # Same group - check for StrOrigin changes
                if "StrOrigin" in change_label:
                    group_analysis[curr_group]["changed_words"] += curr_words
                else:
                    group_analysis[curr_group]["unchanged_words"] += curr_words
            else:
                # GROUP MIGRATION DETECTED
                group_analysis[prev_group]["migrated_out_words"] += prev_words
                group_analysis[curr_group]["migrated_in_words"] += curr_words

    # Process deleted rows for group analysis
    deleted_indices = [idx for idx in df_prev.index if idx not in marked_prev_indices]
    for del_idx in deleted_indices:
        del_row = df_prev.loc[del_idx]
        del_group = safe_str(del_row.get(COL_GROUP, "Unknown"))
        del_strorigin = safe_str(del_row.get(COL_STRORIGIN, ""))
        del_words = len(del_strorigin.split()) if del_strorigin else 0

        # Initialize group if needed
        if del_group not in group_analysis:
            group_analysis[del_group] = _init_group_stats()

        group_analysis[del_group]["total_words_prev"] += del_words
        group_analysis[del_group]["deleted_words"] += del_words

    return changes, previous_strorigins, changed_columns_map, counter, marked_prev_indices, group_analysis, pass1_results


def find_deleted_rows(df_prev, df_curr, marked_prev_indices):
    """
    Find deleted rows using TWO-PASS algorithm.

    A row is considered deleted if it was NOT marked in PASS 1 or PASS 2.

    Args:
        df_prev: Previous DataFrame
        df_curr: Current DataFrame (not used but kept for compatibility)
        marked_prev_indices: Set of previous indices that were matched

    Returns:
        DataFrame: Deleted rows
    """
    deleted_indices = [idx for idx in df_prev.index if idx not in marked_prev_indices]
    return df_prev.loc[deleted_indices].copy() if deleted_indices else df_prev.iloc[0:0].copy()


# Note: classify_working_change and classify_alllang_change functions
# are used by working_comparison.py - keeping stub versions for compatibility
def classify_working_change(curr_row, prev_row, prev_lookup_cg, prev_lookup_cs):
    """Stub for backwards compatibility - not used in 10-key system."""
    return "No Change"


def classify_alllang_change(curr_row, prev_row, prev_lookup_cg, prev_lookup_cs):
    """Stub for backwards compatibility - not used in 10-key system."""
    return "No Change"
