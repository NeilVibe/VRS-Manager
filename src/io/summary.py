"""
Summary report generation module.

This module provides functions to create summary DataFrames for different
VRS processing operations.
"""

import os
import pandas as pd
from datetime import datetime

from src.config import COL_STRORIGIN, COL_TEXT
from src.utils.helpers import safe_str, log
from src.history.history_manager import load_update_history


def create_raw_summary(counter, prev_path, curr_path, df_res):
    """
    Create summary DataFrame for Raw VRS Check.

    Args:
        counter: Dictionary of change type counts
        prev_path: Path to previous file
        curr_path: Path to current file
        df_res: Result DataFrame

    Returns:
        DataFrame: Summary report
    """
    summary_rows = [
        ["RAW VRS CHECK SUMMARY", "", "", ""],
        ["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "", ""],
        ["Previous file", os.path.basename(prev_path), "", ""],
        ["Current file", os.path.basename(curr_path), "", ""],
        ["", "", "", ""],
        ["RESULT COUNTS", "Count", "Word Count (Korean)", "Word Count (Translation)"],
    ]

    sorted_keys = sorted([k for k in counter.keys() if k != "Deleted Rows"])
    for key in sorted_keys:
        word_count_korean = df_res.loc[df_res["CHANGES"] == key, COL_STRORIGIN].apply(
            lambda x: len(safe_str(x).split()) if safe_str(x) else 0
        ).sum()
        word_count_translation = df_res.loc[df_res["CHANGES"] == key, COL_TEXT].apply(
            lambda x: len(safe_str(x).split()) if safe_str(x) else 0
        ).sum()
        summary_rows.append([key, counter[key], word_count_korean, word_count_translation])

    if "Deleted Rows" in counter:
        summary_rows.append(["Deleted Rows", counter["Deleted Rows"], 0, 0])

    return pd.DataFrame(summary_rows, columns=["Metric", "Value", "Word Count (Korean)", "Word Count (Translation)"])


def create_working_summary(counter, prev_path, curr_path, df_res):
    """
    Create summary DataFrame for Working VRS Check.

    Args:
        counter: Dictionary of change type counts
        prev_path: Path to previous file
        curr_path: Path to current file
        df_res: Result DataFrame

    Returns:
        DataFrame: Summary report
    """
    summary_rows = [
        ["WORKING VRS CHECK SUMMARY", "", "", ""],
        ["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "", ""],
        ["Previous file", os.path.basename(prev_path), "", ""],
        ["Current file", os.path.basename(curr_path), "", ""],
        ["", "", "", ""],
        ["RESULT COUNTS", "Count", "Word Count (Korean)", "Word Count (Translation)"],
    ]

    sorted_keys = sorted([k for k in counter.keys() if k != "Deleted Rows"])
    for key in sorted_keys:
        word_count_korean = df_res.loc[df_res["CHANGES"] == key, COL_STRORIGIN].apply(
            lambda x: len(safe_str(x).split()) if safe_str(x) else 0
        ).sum()
        word_count_translation = df_res.loc[df_res["CHANGES"] == key, COL_TEXT].apply(
            lambda x: len(safe_str(x).split()) if safe_str(x) else 0
        ).sum()
        summary_rows.append([key, counter[key], word_count_korean, word_count_translation])

    if "Deleted Rows" in counter:
        summary_rows.append(["Deleted Rows", counter["Deleted Rows"], 0, 0])

    return pd.DataFrame(summary_rows, columns=["Metric", "Value", "Word Count (Korean)", "Word Count (Translation)"])


def create_working_update_history_sheet():
    """
    Create update history DataFrame for Working Process.

    Returns:
        DataFrame: Update history sheet
    """
    from src.config import WORKING_HISTORY_FILE

    history = load_update_history("working")

    history_data = [
        ["WORKING PROCESS - UPDATE HISTORY"],
        [""],
        ["This update history is tracked in: " + WORKING_HISTORY_FILE],
        ["Use 'View Update History' button in main GUI for complete details"],
        [""],
    ]

    if not history["updates"]:
        history_data.append(["No updates recorded yet"])
        history_data.append([""])
    else:
        latest = history["updates"][-1]
        history_data.append(["LATEST UPDATE"])
        history_data.append([f"Timestamp: {latest['timestamp']}"])
        history_data.append([f"Output File: {latest['output_file']}"])
        history_data.append([f"Previous: {latest['previous_file']}"])
        history_data.append([f"Current: {latest['current_file']}"])
        history_data.append([""])
        history_data.append([f"Total Rows: {latest['statistics']['total_rows']:,}"])
        history_data.append([""])
        history_data.append(["Change Breakdown:"])
        for key, value in latest['statistics'].items():
            if key != 'total_rows':
                history_data.append([f"  {key}: {value:,}"])
        history_data.append([""])
        history_data.append([f"Total Updates Recorded: {len(history['updates'])}"])

    history_data.append([""])
    history_data.append([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])

    return pd.DataFrame(history_data, columns=["Update History"])


def create_alllang_summary(counter, prev_kr, prev_en, prev_cn, curr_kr, df_res, has_kr, has_en, has_cn):
    """
    Create summary DataFrame for All Language Check.

    Args:
        counter: Dictionary of change type counts
        prev_kr: Path to previous Korean file (or None)
        prev_en: Path to previous English file (or None)
        prev_cn: Path to previous Chinese file (or None)
        curr_kr: Path to current Korean file
        df_res: Result DataFrame
        has_kr: Whether Korean was updated
        has_en: Whether English was updated
        has_cn: Whether Chinese was updated

    Returns:
        DataFrame: Summary report
    """
    summary_rows = [
        ["ALL LANGUAGE VRS CHECK SUMMARY", "", "", "", "", ""],
        ["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "", "", "", ""],
        ["", "", "", "", "", ""],
        ["CURRENT FILES (Complete Base)", "", "", "", "", ""],
        ["  Korean", os.path.basename(curr_kr), "", "", "", ""],
        ["", "", "", "", "", ""],
        ["PREVIOUS FILES (Updated)", "", "", "", "", ""],
        ["  Korean", os.path.basename(prev_kr) if prev_kr else "Not updated", "", "", "", ""],
        ["  English", os.path.basename(prev_en) if prev_en else "Not updated", "", "", "", ""],
        ["  Chinese", os.path.basename(prev_cn) if prev_cn else "Not updated", "", "", "", ""],
        ["", "", "", "", "", ""],
        ["RESULT COUNTS", "Count", "Word Count (Korean)", "Word Count KR", "Word Count EN", "Word Count CN"],
    ]

    sorted_keys = sorted([k for k in counter.keys() if k != "Deleted Rows"])
    for key in sorted_keys:
        word_count_korean = df_res.loc[df_res["CHANGES"] == key, COL_STRORIGIN].apply(
            lambda x: len(safe_str(x).split()) if safe_str(x) else 0
        ).sum()

        word_count_kr = df_res.loc[df_res["CHANGES"] == key, "Text_KR"].apply(
            lambda x: len(safe_str(x).split()) if safe_str(x) else 0
        ).sum() if has_kr else 0

        word_count_en = df_res.loc[df_res["CHANGES"] == key, "Text_EN"].apply(
            lambda x: len(safe_str(x).split()) if safe_str(x) else 0
        ).sum() if has_en else 0

        word_count_cn = df_res.loc[df_res["CHANGES"] == key, "Text_CN"].apply(
            lambda x: len(safe_str(x).split()) if safe_str(x) else 0
        ).sum() if has_cn else 0

        summary_rows.append([key, counter[key], word_count_korean, word_count_kr, word_count_en, word_count_cn])

    if "Deleted Rows" in counter:
        summary_rows.append(["Deleted Rows", counter["Deleted Rows"], 0, 0, 0, 0])

    return pd.DataFrame(summary_rows, columns=["Metric", "Value", "Word Count (Korean)", "Word Count KR", "Word Count EN", "Word Count CN"])


def create_alllang_update_history_sheet():
    """
    Create update history DataFrame for All Language Process.

    Returns:
        DataFrame: Update history sheet
    """
    from src.config import ALLLANG_HISTORY_FILE

    history = load_update_history("alllang")

    history_data = [
        ["ALL LANGUAGE PROCESS - UPDATE HISTORY"],
        [""],
        ["This update history is tracked in: " + ALLLANG_HISTORY_FILE],
        ["Use 'View Update History' button in main GUI for complete details"],
        [""],
    ]

    if not history["updates"]:
        history_data.append(["No updates recorded yet"])
        history_data.append([""])
    else:
        latest = history["updates"][-1]
        history_data.append(["LATEST UPDATE"])
        history_data.append([f"Timestamp: {latest['timestamp']}"])
        history_data.append([f"Output File: {latest['output_file']}"])
        history_data.append([""])
        history_data.append(["Languages Updated:"])
        for lang in ["KR", "EN", "CN"]:
            status = "✓ UPDATED" if latest["languages_updated"][lang] else "○ Preserved"
            history_data.append([f"  {lang}: {status}"])
        history_data.append([""])
        history_data.append(["Current Files:"])
        for lang in ["KR", "EN", "CN"]:
            history_data.append([f"  {lang}: {latest['current_files'][lang]}"])
        history_data.append([""])
        history_data.append([f"Total Rows: {latest['statistics']['total_rows']:,}"])
        history_data.append([""])
        history_data.append(["Change Breakdown:"])
        for key, value in latest['statistics'].items():
            if key != 'total_rows':
                history_data.append([f"  {key}: {value:,}"])
        history_data.append([""])
        history_data.append([f"Total Updates Recorded: {len(history['updates'])}"])

    history_data.append([""])
    history_data.append([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])

    return pd.DataFrame(history_data, columns=["Update History"])


def create_master_file_update_history_sheet():
    """
    Create update history DataFrame for Master File Update process.

    Returns:
        DataFrame: Update history sheet
    """
    from src.config import MASTER_HISTORY_FILE

    history = load_update_history("master")

    history_data = [
        ["MASTER FILE UPDATE - UPDATE HISTORY"],
        [""],
        ["This update history is tracked in: " + MASTER_HISTORY_FILE],
        ["Use 'View Update History' button in main GUI for complete details"],
        [""],
    ]

    if not history["updates"]:
        history_data.append(["No updates recorded yet"])
        history_data.append([""])
    else:
        latest = history["updates"][-1]
        history_data.append(["LATEST UPDATE"])
        history_data.append([f"Timestamp: {latest['timestamp']}"])
        history_data.append([f"Output File: {latest['output_file']}"])
        history_data.append([f"Source: {latest['source_file']}"])
        history_data.append([f"Target: {latest['target_file']}"])
        history_data.append([""])
        history_data.append([f"Total Rows: {latest['statistics']['total_rows']:,}"])
        history_data.append([""])
        history_data.append(["Change Breakdown:"])
        for key, value in latest['statistics'].items():
            if key != 'total_rows':
                history_data.append([f"  {key}: {value:,}"])
        history_data.append([""])
        history_data.append([f"Total Updates Recorded: {len(history['updates'])}"])

    history_data.append([""])
    history_data.append([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])

    return pd.DataFrame(history_data, columns=["Update History"])
