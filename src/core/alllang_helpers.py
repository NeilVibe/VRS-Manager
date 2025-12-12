"""
Helper functions for All Language VRS Check process.

This module contains utility functions specific to All Language process operations,
including file finding, merging, and comparison logic with the 4-tier key system.
"""

import os
import pandas as pd
from src.config import (
    COL_SEQUENCE, COL_EVENTNAME, COL_STRORIGIN, COL_CASTINGKEY,
    COL_TEXT, COL_STATUS, COL_FREEMEMO, COL_CHARACTERNAME, COL_CHARACTERKEY,
    COL_DIALOGVOICE, COL_SPEAKER_GROUPKEY,
    COL_CHANGES, COL_DETAILED_CHANGES, COL_PREVIOUS_EVENTNAME, COL_PREVIOUS_TEXT
)
from src.utils.helpers import safe_str, log, get_script_dir, generate_previous_data
from src.utils.progress import print_progress, finalize_progress
from src.io.excel_reader import safe_read_excel
from src.utils.data_processing import normalize_dataframe_status, remove_full_duplicates
from src.core.casting import generate_casting_key
from src.core.change_detection import detect_all_field_changes, get_priority_change
from src.settings import get_use_priority_change


def find_alllang_files():
    """
    Auto-detect All Language files from Previous/ and Current/ folders.

    Returns:
        tuple: (curr_kr, curr_en, curr_cn, prev_kr, prev_en, prev_cn)
            Current files are required, previous files are optional (can be None)

    Raises:
        FileNotFoundError: If required folders or current files are missing
    """
    script_dir = get_script_dir()
    previous_folder = os.path.join(script_dir, "Previous")
    current_folder = os.path.join(script_dir, "Current")

    if not os.path.exists(previous_folder):
        raise FileNotFoundError(f"Previous folder not found: {previous_folder}")
    if not os.path.exists(current_folder):
        raise FileNotFoundError(f"Current folder not found: {current_folder}")

    current_files = [f for f in os.listdir(current_folder) if f.endswith(('.xlsx', '.xlsm', '.xls'))]

    curr_kr = None
    curr_en = None
    curr_cn = None

    for filename in current_files:
        if '_KR' in filename:
            curr_kr = os.path.join(current_folder, filename)
        elif '_EN' in filename:
            curr_en = os.path.join(current_folder, filename)
        elif '_CN' in filename:
            curr_cn = os.path.join(current_folder, filename)

    if not curr_kr:
        raise FileNotFoundError("Korean current file (_KR) not found in Current folder")
    if not curr_en:
        raise FileNotFoundError("English current file (_EN) not found in Current folder")
    if not curr_cn:
        raise FileNotFoundError("Chinese current file (_CN) not found in Current folder")

    previous_files = [f for f in os.listdir(previous_folder) if f.endswith(('.xlsx', '.xlsm', '.xls'))]

    prev_kr = None
    prev_en = None
    prev_cn = None

    for filename in previous_files:
        if '_KR' in filename:
            prev_kr = os.path.join(previous_folder, filename)
        elif '_EN' in filename:
            prev_en = os.path.join(previous_folder, filename)
        elif '_CN' in filename:
            prev_cn = os.path.join(previous_folder, filename)

    return curr_kr, curr_en, curr_cn, prev_kr, prev_en, prev_cn


def merge_current_files(curr_kr_path, curr_en_path, curr_cn_path):
    """
    Merge current KR, EN, CN files into a unified tri-lingual structure.

    Args:
        curr_kr_path: Path to current Korean file
        curr_en_path: Path to current English file
        curr_cn_path: Path to current Chinese file

    Returns:
        DataFrame: Merged DataFrame with tri-lingual columns
    """
    log("\n" + "="*70)
    log("PHASE 1: MERGING CURRENT FILES")
    log("="*70)

    log(f"Reading KR Current: {os.path.basename(curr_kr_path)}")
    df_kr = safe_read_excel(curr_kr_path, header=0, dtype=str)
    df_kr = normalize_dataframe_status(df_kr)
    log(f"  → {len(df_kr):,} rows")
    df_kr = remove_full_duplicates(df_kr, "KR CURRENT")

    log(f"Reading EN Current: {os.path.basename(curr_en_path)}")
    df_en = safe_read_excel(curr_en_path, header=0, dtype=str)
    df_en = normalize_dataframe_status(df_en)
    log(f"  → {len(df_en):,} rows")
    df_en = remove_full_duplicates(df_en, "EN CURRENT")

    log(f"Reading CN Current: {os.path.basename(curr_cn_path)}")
    df_cn = safe_read_excel(curr_cn_path, header=0, dtype=str)
    df_cn = normalize_dataframe_status(df_cn)
    log(f"  → {len(df_cn):,} rows")
    df_cn = remove_full_duplicates(df_cn, "CN CURRENT")

    log("Generating CastingKey for current files...")
    for df in [df_kr, df_en, df_cn]:
        casting_keys = []
        for idx, row in df.iterrows():
            casting_key = generate_casting_key(
                row.get(COL_CHARACTERKEY, ""),
                row.get(COL_DIALOGVOICE, ""),
                row.get(COL_SPEAKER_GROUPKEY, ""),
                row.get("DialogType", "")
            )
            casting_keys.append(casting_key)
        df[COL_CASTINGKEY] = casting_keys
    log(f"  → Generated CastingKey for KR/EN/CN current files")

    log("Building EN/CN lookup dictionaries...")
    lookup_en = {}
    lookup_cn = {}

    for _, row in df_en.iterrows():
        key = (row[COL_SEQUENCE], row[COL_EVENTNAME])
        lookup_en[key] = row.to_dict()

    for _, row in df_cn.iterrows():
        key = (row[COL_SEQUENCE], row[COL_EVENTNAME])
        lookup_cn[key] = row.to_dict()

    log(f"  → EN: {len(lookup_en):,} rows indexed")
    log(f"  → CN: {len(lookup_cn):,} rows indexed")

    log("Merging data into unified structure...")
    merged_rows = []
    total = len(df_kr)

    for idx, kr_row in df_kr.iterrows():
        merged = kr_row.to_dict()
        key = (kr_row[COL_SEQUENCE], kr_row[COL_EVENTNAME])

        merged["Text_KR"] = safe_str(merged.pop(COL_TEXT, ""))
        merged["FREEMEMO_KR"] = safe_str(merged.pop(COL_FREEMEMO, ""))
        merged["STATUS_KR"] = safe_str(merged.pop(COL_STATUS, ""))
        merged["CharacterName_KR"] = safe_str(merged.pop(COL_CHARACTERNAME, ""))

        if key in lookup_en:
            en_row = lookup_en[key]
            merged["Text_EN"] = safe_str(en_row.get(COL_TEXT, ""))
            merged["FREEMEMO_EN"] = safe_str(en_row.get(COL_FREEMEMO, ""))
            merged["STATUS_EN"] = safe_str(en_row.get(COL_STATUS, ""))
            merged["CharacterName_EN"] = safe_str(en_row.get(COL_CHARACTERNAME, ""))
        else:
            merged["Text_EN"] = ""
            merged["FREEMEMO_EN"] = ""
            merged["STATUS_EN"] = ""
            merged["CharacterName_EN"] = ""

        if key in lookup_cn:
            cn_row = lookup_cn[key]
            merged["Text_CN"] = safe_str(cn_row.get(COL_TEXT, ""))
            merged["FREEMEMO_CN"] = safe_str(cn_row.get(COL_FREEMEMO, ""))
            merged["STATUS_CN"] = safe_str(cn_row.get(COL_STATUS, ""))
            merged["CharacterName_CN"] = safe_str(cn_row.get(COL_CHARACTERNAME, ""))
        else:
            merged["Text_CN"] = ""
            merged["FREEMEMO_CN"] = ""
            merged["STATUS_CN"] = ""
            merged["CharacterName_CN"] = ""

        merged_rows.append(merged)

        if (idx + 1) % 500 == 0 or idx == total - 1:
            print_progress(idx + 1, total, "Merging")

    finalize_progress()

    df_merged = pd.DataFrame(merged_rows)
    log(f"✓ Unified structure created: {len(df_merged):,} rows with tri-lingual columns")

    return df_merged


def apply_import_logic_alllang_lang(curr_row, prev_row, change_type, lang_suffix):
    """
    Apply import logic for a specific language in All Language process.

    Args:
        curr_row: Current row dictionary
        prev_row: Previous row dictionary (or None)
        change_type: Type of change detected
        lang_suffix: Language suffix ("KR", "EN", or "CN")

    Returns:
        dict: Dictionary of column values to import
    """
    result = {}

    text_col = f"Text_{lang_suffix}"
    status_col = f"STATUS_{lang_suffix}"
    freememo_col = f"FREEMEMO_{lang_suffix}"

    if prev_row:
        result[freememo_col] = safe_str(prev_row.get(COL_FREEMEMO, ""))

    if change_type == "New Row":
        return result

    prev_status = safe_str(prev_row.get(COL_STATUS, "")) if prev_row else ""

    if "StrOrigin" in change_type:
        if prev_status:
            # ANY status exists: preserve previous translation + StrOrigin
            result[text_col] = safe_str(prev_row.get(COL_TEXT, "")) if prev_row else ""
            result[status_col] = prev_status
            result[COL_STRORIGIN] = safe_str(prev_row.get(COL_STRORIGIN, "")) if prev_row else ""
        else:
            # No status: use current/mainline translation
            result[text_col] = safe_str(curr_row.get(text_col, ""))

    elif "TimeFrame" in change_type:
        result[text_col] = safe_str(prev_row.get(COL_TEXT, "")) if prev_row else ""
        result[status_col] = prev_status

    elif change_type in ["No Change", "No Relevant Change", "EventName Change", "SequenceName Change"]:
        result[text_col] = safe_str(prev_row.get(COL_TEXT, "")) if prev_row else ""
        result[status_col] = prev_status

    else:
        result[text_col] = safe_str(prev_row.get(COL_TEXT, "")) if prev_row else ""
        result[status_col] = prev_status

    return result


def process_alllang_comparison_twopass(df_curr, df_kr, prev_lookup_se, prev_lookup_so, prev_lookup_sc,
                               prev_lookup_eo, prev_lookup_ec, prev_lookup_oc,
                               prev_lookup_seo, prev_lookup_sec, prev_lookup_soc, prev_lookup_eoc,
                               lookup_en, lookup_cn,
                               has_kr, has_en, has_cn):
    """
    Compare and import data for All Language process using TWO-PASS 10-key system.

    TWO-PASS ALGORITHM prevents 1-to-many matching issues (for KR only):
    - PASS 1: Detect and mark No Change/New rows (certainties)
    - PASS 2: Detect partial changes using only UNMARKED previous rows

    Args:
        df_curr: Current merged DataFrame
        df_kr: KR Previous DataFrame (needed for TWO-PASS, can be None if not has_kr)
        prev_lookup_se: KR Previous lookup for (Sequence, Event) → DataFrame index
        prev_lookup_so: KR Previous lookup for (Sequence, StrOrigin) → DataFrame index
        prev_lookup_sc: KR Previous lookup for (Sequence, CastingKey) → DataFrame index
        prev_lookup_eo: KR Previous lookup for (Event, StrOrigin) → DataFrame index
        prev_lookup_ec: KR Previous lookup for (Event, CastingKey) → DataFrame index
        prev_lookup_oc: KR Previous lookup for (StrOrigin, CastingKey) → DataFrame index
        prev_lookup_seo: KR Previous lookup for (Sequence, Event, StrOrigin) → DataFrame index
        prev_lookup_sec: KR Previous lookup for (Sequence, Event, CastingKey) → DataFrame index
        prev_lookup_soc: KR Previous lookup for (Sequence, StrOrigin, CastingKey) → DataFrame index
        prev_lookup_eoc: KR Previous lookup for (Event, StrOrigin, CastingKey) → DataFrame index
        lookup_en: English lookup dictionary (key: (SequenceName, EventName)) → DataFrame index
        lookup_cn: Chinese lookup dictionary (key: (SequenceName, EventName)) → DataFrame index
        has_kr: Whether Korean should be updated
        has_en: Whether English should be updated
        has_cn: Whether Chinese should be updated

    Returns:
        tuple: (df_result, counter, marked_prev_indices) where:
            - df_result: DataFrame with imported data
            - counter: Dictionary of change type counts
            - marked_prev_indices: Set of KR previous DataFrame indices that were matched
    """
    log("\n" + "="*70)
    log("PHASE 2: IMPORTING DATA FROM PREVIOUS FILES (TWO-PASS)")
    log("="*70)
    log(f"Languages to update: KR={has_kr}, EN={has_en}, CN={has_cn}")

    marked_prev_indices = set()
    total_rows = len(df_curr)

    # Import apply_import_logic_alllang_lang here to avoid circular import
    from src.core.alllang_helpers import apply_import_logic_alllang_lang

    # ========================================
    # PASS 1: Detect No Change and New rows (KR only if has_kr)
    # ========================================
    pass1_results = {}  # curr_idx → (change_type, prev_idx_or_none)

    if has_kr:
        log("PASS 1: Detecting certainties for KR...")
        progress_count = 0
        for curr_idx, curr_row in df_curr.iterrows():
            S = safe_str(curr_row.get(COL_SEQUENCE, ""))
            E = safe_str(curr_row.get(COL_EVENTNAME, ""))
            O = safe_str(curr_row.get(COL_STRORIGIN, ""))
            C = safe_str(curr_row.get(COL_CASTINGKEY, ""))

            # Defensive check: ensure all values are strings
            if isinstance(S, dict) or isinstance(E, dict) or isinstance(O, dict) or isinstance(C, dict):
                log(f"ERROR at row {curr_idx}: Found dict value in keys!")
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
                    prev_row = df_kr.loc[prev_idx]
                    prev_S = safe_str(prev_row.get(COL_SEQUENCE, ""))
                    prev_E = safe_str(prev_row.get(COL_EVENTNAME, ""))
                    prev_O = safe_str(prev_row.get(COL_STRORIGIN, ""))
                    prev_C = safe_str(prev_row.get(COL_CASTINGKEY, ""))

                    # Perfect match: All 4 keys identical
                    if S == prev_S and E == prev_E and O == prev_O and C == prev_C:
                        # Use universal detection for consistent labeling
                        change_type = detect_all_field_changes(curr_row, prev_row, df_curr, df_kr)

                        marked_prev_indices.add(prev_idx)
                        pass1_results[curr_idx] = (change_type, prev_idx)

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
                    pass1_results[curr_idx] = ("New Row", None)

            progress_count += 1
            if progress_count % 500 == 0 or progress_count == total_rows:
                print_progress(progress_count, total_rows, "PASS 1: Detecting certainties")

        finalize_progress()

        # ========================================
        # PASS 2: Detect partial changes using UNMARKED rows (KR only)
        # ========================================
        log("PASS 2: Detecting changes for KR...")
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

            # ========================================
            # LEVEL 1: 3-Key Matches (One core field changed)
            # ========================================

            # SEO Match: Same Sequence + Event + StrOrigin
            if not matched and key_seo in prev_lookup_seo:
                candidate_idx = prev_lookup_seo[key_seo]
                if candidate_idx not in marked_prev_indices:
                    prev_row = df_kr.loc[candidate_idx]
                    # Use universal detection
                    change_type = detect_all_field_changes(curr_row, prev_row, df_curr, df_kr)
                    prev_idx = candidate_idx
                    marked_prev_indices.add(candidate_idx)
                    matched = True

            # SEC Match: Same Sequence + Event + CastingKey
            if not matched and key_sec in prev_lookup_sec:
                candidate_idx = prev_lookup_sec[key_sec]
                if candidate_idx not in marked_prev_indices:
                    prev_row = df_kr.loc[candidate_idx]
                    # Use universal detection
                    change_type = detect_all_field_changes(curr_row, prev_row, df_curr, df_kr)
                    prev_idx = candidate_idx
                    marked_prev_indices.add(candidate_idx)
                    matched = True

            # SOC Match: Same Sequence + StrOrigin + CastingKey
            if not matched and key_soc in prev_lookup_soc:
                candidate_idx = prev_lookup_soc[key_soc]
                if candidate_idx not in marked_prev_indices:
                    prev_row = df_kr.loc[candidate_idx]
                    # Use universal detection with Korean relevance filter
                    change_type = detect_all_field_changes(curr_row, prev_row, df_curr, df_kr, require_korean=O)
                    prev_idx = candidate_idx
                    marked_prev_indices.add(candidate_idx)
                    matched = True

            # EOC Match: Same Event + StrOrigin + CastingKey
            if not matched and key_eoc in prev_lookup_eoc:
                candidate_idx = prev_lookup_eoc[key_eoc]
                if candidate_idx not in marked_prev_indices:
                    prev_row = df_kr.loc[candidate_idx]
                    # Use universal detection
                    change_type = detect_all_field_changes(curr_row, prev_row, df_curr, df_kr)
                    prev_idx = candidate_idx
                    marked_prev_indices.add(candidate_idx)
                    matched = True

            # ========================================
            # LEVEL 2: 2-Key Matches (Two+ core fields changed)
            # ========================================

            # SE Match: Same Sequence + Event
            if not matched and key_se in prev_lookup_se:
                candidate_idx = prev_lookup_se[key_se]
                if candidate_idx not in marked_prev_indices:
                    prev_row = df_kr.loc[candidate_idx]
                    # Use universal detection
                    change_type = detect_all_field_changes(curr_row, prev_row, df_curr, df_kr)
                    prev_idx = candidate_idx
                    marked_prev_indices.add(candidate_idx)
                    matched = True

            # OC Match: Same StrOrigin + CastingKey
            if not matched and key_oc in prev_lookup_oc:
                candidate_idx = prev_lookup_oc[key_oc]
                if candidate_idx not in marked_prev_indices:
                    prev_row = df_kr.loc[candidate_idx]
                    # Use universal detection
                    change_type = detect_all_field_changes(curr_row, prev_row, df_curr, df_kr)
                    prev_idx = candidate_idx
                    marked_prev_indices.add(candidate_idx)
                    matched = True

            # EC Match: Same Event + CastingKey
            if not matched and key_ec in prev_lookup_ec:
                candidate_idx = prev_lookup_ec[key_ec]
                if candidate_idx not in marked_prev_indices:
                    prev_row = df_kr.loc[candidate_idx]
                    # Use universal detection
                    change_type = detect_all_field_changes(curr_row, prev_row, df_curr, df_kr)
                    prev_idx = candidate_idx
                    marked_prev_indices.add(candidate_idx)
                    matched = True

            # SC Match: Same Sequence + CastingKey
            if not matched and key_sc in prev_lookup_sc:
                candidate_idx = prev_lookup_sc[key_sc]
                if candidate_idx not in marked_prev_indices:
                    prev_row = df_kr.loc[candidate_idx]
                    # Use universal detection
                    change_type = detect_all_field_changes(curr_row, prev_row, df_curr, df_kr)
                    prev_idx = candidate_idx
                    marked_prev_indices.add(candidate_idx)
                    matched = True

            # SO Match: Same Sequence + StrOrigin
            if not matched and key_so in prev_lookup_so:
                candidate_idx = prev_lookup_so[key_so]
                if candidate_idx not in marked_prev_indices:
                    prev_row = df_kr.loc[candidate_idx]
                    # Use universal detection with Korean relevance filter
                    change_type = detect_all_field_changes(curr_row, prev_row, df_curr, df_kr, require_korean=O)
                    prev_idx = candidate_idx
                    marked_prev_indices.add(candidate_idx)
                    matched = True

            # EO Match: Same Event + StrOrigin
            if not matched and key_eo in prev_lookup_eo:
                candidate_idx = prev_lookup_eo[key_eo]
                if candidate_idx not in marked_prev_indices:
                    prev_row = df_kr.loc[candidate_idx]
                    # Use universal detection
                    change_type = detect_all_field_changes(curr_row, prev_row, df_curr, df_kr)
                    prev_idx = candidate_idx
                    marked_prev_indices.add(candidate_idx)
                    matched = True

            # If no match found in PASS 2, it's a NEW row
            if not matched:
                change_type = "New Row"
                prev_idx = None

            # Store PASS 2 result
            pass1_results[curr_idx] = (change_type, prev_idx)

            progress_count += 1
            if progress_count % 500 == 0 or progress_count == total_rows:
                print_progress(progress_count, total_rows, "PASS 2: Detecting changes")

        finalize_progress()

    # ========================================
    # Apply import logic to all rows
    # ========================================
    log("Applying tri-lingual import logic...")
    results = []
    counter = {}

    for curr_idx, curr_row in df_curr.iterrows():
        curr_dict = curr_row.to_dict()

        S = safe_str(curr_row.get(COL_SEQUENCE, ""))
        E = safe_str(curr_row.get(COL_EVENTNAME, ""))

        # Get KR detection result
        if has_kr and curr_idx in pass1_results:
            change_type, prev_idx = pass1_results[curr_idx]
            prev_kr_dict = df_kr.loc[prev_idx].to_dict() if prev_idx is not None else None
        elif has_kr:
            # Shouldn't happen
            change_type = "ERROR: Missing Classification"
            prev_kr_dict = None
        else:
            change_type = "No Change"
            prev_kr_dict = None

        # Apply KR import logic
        if has_kr:
            import_kr = apply_import_logic_alllang_lang(curr_dict, prev_kr_dict, change_type, "KR")
            for col, value in import_kr.items():
                curr_dict[col] = value

            curr_dict["PreviousData_KR"] = generate_previous_data(
                prev_kr_dict, COL_TEXT, COL_STATUS, COL_FREEMEMO
            ) if prev_kr_dict else ""
        else:
            curr_dict["PreviousData_KR"] = ""

        # Apply EN import logic (simple SE lookup)
        if has_en:
            key_se = (S, E)
            prev_en_idx = lookup_en.get(key_se)
            # Note: lookup_en should also store indices, but for now assume it stores dict
            # This will need updating when EN/CN lookups are converted to indices
            prev_en_dict = prev_en_idx if isinstance(prev_en_idx, dict) else None

            import_en = apply_import_logic_alllang_lang(curr_dict, prev_en_dict, change_type, "EN")
            for col, value in import_en.items():
                curr_dict[col] = value

            curr_dict["PreviousData_EN"] = generate_previous_data(
                prev_en_dict, COL_TEXT, COL_STATUS, COL_FREEMEMO
            ) if prev_en_dict else ""
        else:
            curr_dict["PreviousData_EN"] = ""

        # Apply CN import logic (simple SE lookup)
        if has_cn:
            key_se = (S, E)
            prev_cn_idx = lookup_cn.get(key_se)
            # Note: lookup_cn should also store indices, but for now assume it stores dict
            prev_cn_dict = prev_cn_idx if isinstance(prev_cn_idx, dict) else None

            import_cn = apply_import_logic_alllang_lang(curr_dict, prev_cn_dict, change_type, "CN")
            for col, value in import_cn.items():
                curr_dict[col] = value

            curr_dict["PreviousData_CN"] = generate_previous_data(
                prev_cn_dict, COL_TEXT, COL_STATUS, COL_FREEMEMO
            ) if prev_cn_dict else ""
        else:
            curr_dict["PreviousData_CN"] = ""

        # Phase 4: Set change type columns (respects Priority Change setting)
        actual_change = change_type if has_kr else "No Change"
        curr_dict[COL_DETAILED_CHANGES] = actual_change
        if get_use_priority_change():
            curr_dict[COL_CHANGES] = get_priority_change(actual_change)
        else:
            curr_dict[COL_CHANGES] = actual_change  # Legacy mode: show full composite

        # Phase 4.1: PreviousEventName - only when EventName changed
        if prev_kr_dict and "EventName" in actual_change:
            curr_dict[COL_PREVIOUS_EVENTNAME] = safe_str(prev_kr_dict.get(COL_EVENTNAME, ""))
        else:
            curr_dict[COL_PREVIOUS_EVENTNAME] = ""

        # Phase 4.3: PreviousText - always for matched rows (not New Row)
        # For ALLLANG, store KR previous text
        if prev_kr_dict and actual_change != "New Row":
            curr_dict[COL_PREVIOUS_TEXT] = safe_str(prev_kr_dict.get(COL_TEXT, ""))
        else:
            curr_dict[COL_PREVIOUS_TEXT] = ""

        results.append(curr_dict)
        counter[actual_change] = counter.get(actual_change, 0) + 1

    import pandas as pd
    return pd.DataFrame(results), counter, marked_prev_indices
