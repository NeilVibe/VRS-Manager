"""
Update history management module.

This module provides functionality to track, save, and load update history
for different VRS Manager processes (Working, AllLang, Master).
"""

import os
import json
from datetime import datetime

from src.config import (
    WORKING_HISTORY_FILE,
    MASTER_HISTORY_FILE,
    ALLLANG_HISTORY_FILE
)
from src.utils.helpers import get_script_dir, log


def get_history_file_path(process_type="master"):
    """
    Get the path to the history file for a specific process type.

    Args:
        process_type: Type of process ("working", "alllang", or "master")

    Returns:
        str: Full path to the history file
    """
    script_dir = get_script_dir()
    if process_type == "working":
        return os.path.join(script_dir, WORKING_HISTORY_FILE)
    elif process_type == "alllang":
        return os.path.join(script_dir, ALLLANG_HISTORY_FILE)
    else:
        return os.path.join(script_dir, MASTER_HISTORY_FILE)


def load_update_history(process_type="master"):
    """
    Load update history from JSON file.

    Args:
        process_type: Type of process ("working", "alllang", or "master")

    Returns:
        dict: History data with "process_type" and "updates" keys
    """
    history_path = get_history_file_path(process_type)

    if not os.path.exists(history_path):
        return {"process_type": process_type, "updates": []}

    try:
        with open(history_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log(f"Warning: Could not load {process_type} history file: {e}")
        return {"process_type": process_type, "updates": []}


def save_update_history(history, process_type="master"):
    """
    Save update history to JSON file.

    Args:
        history: History data dictionary to save
        process_type: Type of process ("working", "alllang", or "master")
    """
    history_path = get_history_file_path(process_type)

    try:
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        log(f"✓ Update history saved")
    except Exception as e:
        log(f"Warning: Could not save {process_type} history file: {e}")


def add_working_update_record(output_filename, prev_path, curr_path, counter, total_rows):
    """
    Add a new update record for the Working process.

    Args:
        output_filename: Name of the output file created
        prev_path: Path to the previous file
        curr_path: Path to the current file
        counter: Dictionary of change type counts
        total_rows: Total number of rows processed

    Returns:
        dict: The created record
    """
    history = load_update_history("working")

    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "process_type": "Working",
        "output_file": output_filename,
        "previous_file": os.path.basename(prev_path),
        "current_file": os.path.basename(curr_path),
        "statistics": {
            "total_rows": total_rows,
            **{k: v for k, v in counter.items()}
        }
    }

    history["updates"].append(record)
    save_update_history(history, "working")
    return record


def add_alllang_update_record(output_filename, prev_kr, prev_en, prev_cn, curr_kr, curr_en, curr_cn,
                              counter, total_rows):
    """
    Add a new update record for the AllLanguage process.

    Args:
        output_filename: Name of the output file created
        prev_kr: Path to previous Korean file (or None)
        prev_en: Path to previous English file (or None)
        prev_cn: Path to previous Chinese file (or None)
        curr_kr: Path to current Korean file
        curr_en: Path to current English file
        curr_cn: Path to current Chinese file
        counter: Dictionary of change type counts
        total_rows: Total number of rows processed

    Returns:
        dict: The created record
    """
    history = load_update_history("alllang")

    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "process_type": "AllLanguage",
        "output_file": output_filename,
        "languages_updated": {
            "KR": prev_kr is not None,
            "EN": prev_en is not None,
            "CN": prev_cn is not None
        },
        "previous_files": {
            "KR": os.path.basename(prev_kr) if prev_kr else None,
            "EN": os.path.basename(prev_en) if prev_en else None,
            "CN": os.path.basename(prev_cn) if prev_cn else None
        },
        "current_files": {
            "KR": os.path.basename(curr_kr),
            "EN": os.path.basename(curr_en),
            "CN": os.path.basename(curr_cn)
        },
        "statistics": {
            "total_rows": total_rows,
            **{k: v for k, v in counter.items()}
        }
    }

    history["updates"].append(record)
    save_update_history(history, "alllang")
    return record


def add_master_file_update_record(output_filename, source_path, target_path, counter, total_rows):
    """
    Add a new update record for the Master File Update process.

    Args:
        output_filename: Name of the output file created
        source_path: Path to the source file
        target_path: Path to the target file
        counter: Dictionary of change type counts
        total_rows: Total number of rows processed

    Returns:
        dict: The created record
    """
    history = load_update_history("master")

    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "process_type": "MasterFileUpdate",
        "output_file": output_filename,
        "source_file": os.path.basename(source_path),
        "target_file": os.path.basename(target_path),
        "statistics": {
            "total_rows": total_rows,
            **{k: v for k, v in counter.items()}
        }
    }

    history["updates"].append(record)
    save_update_history(history, "master")
    return record


def clear_update_history(process_type="master"):
    """
    Clear all update history for a specific process type.

    This function is designed to be called from a GUI context where
    user confirmation is available.

    Args:
        process_type: Type of process ("working", "alllang", or "master")

    Returns:
        bool: True if history was cleared, False if cancelled
    """
    # Note: This function expects to be called from a GUI context
    # The actual messagebox import and confirmation should be handled by the caller
    history = {"process_type": process_type, "updates": []}
    save_update_history(history, process_type)
    return True


def delete_specific_update(index, process_type="master"):
    """
    Delete a specific update record by index.

    Args:
        index: Index of the update to delete
        process_type: Type of process ("working", "alllang", or "master")

    Returns:
        tuple: (success, deleted_record) where:
            - success: True if deletion succeeded, False otherwise
            - deleted_record: The deleted record, or None if failed
    """
    history = load_update_history(process_type)

    if 0 <= index < len(history["updates"]):
        deleted = history["updates"].pop(index)
        save_update_history(history, process_type)
        return True, deleted
    return False, None
