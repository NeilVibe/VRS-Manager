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
    COL_DIALOGVOICE, COL_SPEAKER_GROUPKEY, COL_STARTFRAME
)
from src.utils.helpers import safe_str, contains_korean, log, get_script_dir
from src.utils.progress import print_progress, finalize_progress
from src.io.excel_reader import safe_read_excel
from src.utils.data_processing import normalize_dataframe_status
from src.core.casting import generate_casting_key, generate_previous_data
from src.core.import_logic import is_after_recording_status


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

    log(f"Reading EN Current: {os.path.basename(curr_en_path)}")
    df_en = safe_read_excel(curr_en_path, header=0, dtype=str)
    df_en = normalize_dataframe_status(df_en)
    log(f"  → {len(df_en):,} rows")

    log(f"Reading CN Current: {os.path.basename(curr_cn_path)}")
    df_cn = safe_read_excel(curr_cn_path, header=0, dtype=str)
    df_cn = normalize_dataframe_status(df_cn)
    log(f"  → {len(df_cn):,} rows")

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

    prev_status = prev_row.get(COL_STATUS, "") if prev_row else ""
    is_after_recording = is_after_recording_status(prev_status)

    if "StrOrigin" in change_type:
        if is_after_recording:
            result[text_col] = safe_str(prev_row.get(COL_TEXT, "")) if prev_row else ""
            result[status_col] = prev_status
        else:
            result[text_col] = safe_str(curr_row.get(text_col, ""))
            result[status_col] = "NEED CHECK"

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


def process_alllang_comparison(df_curr, lookup_kr, lookup_en, lookup_cn,
                               lookup_cg_kr, lookup_es_kr, lookup_cs_kr,
                               has_kr, has_en, has_cn):
    """
    Compare and import data for All Language process using 4-key system.

    Args:
        df_curr: Current merged DataFrame
        lookup_kr: Korean lookup dictionary (key: (SequenceName, EventName))
        lookup_en: English lookup dictionary
        lookup_cn: Chinese lookup dictionary
        lookup_cg_kr: Korean lookup for (SequenceName, StrOrigin) -> EventName
        lookup_es_kr: Korean lookup for (EventName, StrOrigin)
        lookup_cs_kr: Korean lookup for (CastingKey, SequenceName)
        has_kr: Whether Korean should be updated
        has_en: Whether English should be updated
        has_cn: Whether Chinese should be updated

    Returns:
        tuple: (df_result, counter) where:
            - df_result: DataFrame with imported data
            - counter: Dictionary of change type counts
    """
    log("\n" + "="*70)
    log("PHASE 2: IMPORTING DATA FROM PREVIOUS FILES")
    log("="*70)
    log(f"Languages to update: KR={has_kr}, EN={has_en}, CN={has_cn}")

    results = []
    counter = {}
    total_rows = len(df_curr)

    for idx, curr_row in df_curr.iterrows():
        curr_dict = curr_row.to_dict()
        key_cw = (curr_row[COL_SEQUENCE], curr_row[COL_EVENTNAME])
        key_cg = (curr_row[COL_SEQUENCE], curr_row[COL_STRORIGIN])
        key_es = (curr_row[COL_EVENTNAME], curr_row[COL_STRORIGIN])
        key_cs = (curr_row[COL_CASTINGKEY], curr_row[COL_SEQUENCE])

        mainline_kr = safe_str(curr_dict.get("Text_KR", ""))
        mainline_en = safe_str(curr_dict.get("Text_EN", ""))
        mainline_cn = safe_str(curr_dict.get("Text_CN", ""))

        if has_kr:
            # Stage 1: Direct match (SequenceName + EventName)
            if key_cw in lookup_kr:
                prev_kr = lookup_kr[key_cw]

                differences = [col for col in curr_dict.keys() if col in prev_kr and curr_dict[col] != prev_kr[col]]

                if not differences:
                    change_type = "No Change"
                else:
                    important_changes = []
                    if COL_STRORIGIN in differences:
                        important_changes.append("StrOrigin")
                    if COL_STARTFRAME in differences:
                        important_changes.append("TimeFrame")

                    if important_changes:
                        change_type = "+".join(important_changes) + " Change"
                    else:
                        change_type = "No Relevant Change"

            # Stage 2: StrOrigin+Sequence match - VERIFY with Key 4
            elif key_cg in lookup_cg_kr:
                # Check if same character (Key 4 verification)
                if key_cs in lookup_cs_kr:
                    # Same character → EventName Change
                    old_eventname = lookup_cg_kr[key_cg]
                    prev_kr = lookup_kr.get((curr_row[COL_SEQUENCE], old_eventname))

                    if prev_kr:
                        differences = [col for col in curr_dict.keys() if col in prev_kr and curr_dict[col] != prev_kr[col]]

                        important_changes = []
                        if COL_STRORIGIN in differences:
                            important_changes.append("StrOrigin")
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
                        prev_kr = None
                else:
                    # Different character → New Row (duplicate StrOrigin case)
                    change_type = "New Row"
                    prev_kr = None

            # Stage 3: SequenceName changed (EventName + StrOrigin match)
            elif key_es in lookup_es_kr:
                prev_kr = lookup_es_kr[key_es]
                change_type = "SequenceName Change"

            # Stage 4: Truly new (no keys match)
            else:
                change_type = "New Row"
                prev_kr = None
        else:
            change_type = "No Change"
            prev_kr = None

        if has_kr:
            import_kr = apply_import_logic_alllang_lang(curr_dict, prev_kr, change_type, "KR")
            for col, value in import_kr.items():
                curr_dict[col] = value

            curr_dict["PreviousData_KR"] = generate_previous_data(
                prev_kr, COL_TEXT, COL_STATUS, COL_FREEMEMO
            ) if prev_kr else ""
        else:
            curr_dict["PreviousData_KR"] = ""

        if has_en:
            prev_en = lookup_en.get(key_cw)
            import_en = apply_import_logic_alllang_lang(curr_dict, prev_en, change_type, "EN")
            for col, value in import_en.items():
                curr_dict[col] = value

            curr_dict["PreviousData_EN"] = generate_previous_data(
                prev_en, COL_TEXT, COL_STATUS, COL_FREEMEMO
            ) if prev_en else ""
        else:
            curr_dict["PreviousData_EN"] = ""

        if has_cn:
            prev_cn = lookup_cn.get(key_cw)
            import_cn = apply_import_logic_alllang_lang(curr_dict, prev_cn, change_type, "CN")
            for col, value in import_cn.items():
                curr_dict[col] = value

            curr_dict["PreviousData_CN"] = generate_previous_data(
                prev_cn, COL_TEXT, COL_STATUS, COL_FREEMEMO
            ) if prev_cn else ""
        else:
            curr_dict["PreviousData_CN"] = ""

        curr_dict[COL_CASTINGKEY] = generate_casting_key(
            curr_dict.get(COL_CHARACTERKEY, ""),
            curr_dict.get(COL_DIALOGVOICE, ""),
            curr_dict.get(COL_SPEAKER_GROUPKEY, ""),
            curr_dict.get("DialogType", "")
        )

        curr_dict["Mainline Translation_KR"] = mainline_kr
        curr_dict["Mainline Translation_EN"] = mainline_en
        curr_dict["Mainline Translation_CN"] = mainline_cn

        curr_dict["CHANGES"] = change_type

        results.append(curr_dict)
        counter[change_type] = counter.get(change_type, 0) + 1

        if (idx + 1) % 500 == 0 or idx == total_rows - 1:
            print_progress(idx + 1, total_rows, "Processing rows")

    finalize_progress()
    return pd.DataFrame(results), counter
