"""
Utility helper functions for VRS Manager
"""
import os
import sys
import pandas as pd
from datetime import datetime
from src.config import (
    COL_STARTFRAME, COL_ENDFRAME, COL_STRORIGIN,
    AFTER_RECORDING_STATUSES
)


def log(msg):
    """Print timestamped log message"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def get_script_dir():
    """
    Get the directory where the script is running from.

    When running as PyInstaller executable: returns directory containing .exe
    When running as script: returns project root directory
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable - return exe directory
        return os.path.dirname(sys.executable)
    else:
        # Running as script - return project root (2 levels up from src/utils/)
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def find_status_column(columns):
    """Find the STATUS column regardless of case"""
    for col in columns:
        if col.upper() == "STATUS":
            return col
    return None


def safe_str(value):
    """Safely convert value to string, handling None and NaN"""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    if str(value).strip().upper() == "NAN":
        return ""
    return str(value).strip()


def normalize_status(status_value):
    """Normalize status to uppercase"""
    clean_val = safe_str(status_value)
    if not clean_val:
        return ""
    return clean_val.upper()


def is_after_recording_status(status_value):
    """Check if status is an after-recording status"""
    if not status_value:
        return False
    normalized = normalize_status(status_value)
    return normalized in AFTER_RECORDING_STATUSES


def contains_korean(text):
    """Check if text contains Korean characters"""
    if not text:
        return False
    text_str = safe_str(text)
    for char in text_str:
        code = ord(char)
        if (0xAC00 <= code <= 0xD7A3) or (0x1100 <= code <= 0x11FF) or (0x3130 <= code <= 0x318F):
            return True
    return False


def generate_color_for_value(value):
    """Generate a color based on hash of value"""
    fallback_colors = [
        "FFB3BA", "BAFFC9", "BAE1FF", "FFFFBA", "FFD9BA",
        "E0BBE4", "FFDFD3", "D4F1F4", "C9E4DE", "F7D9C4",
    ]
    hash_val = hash(str(value))
    return fallback_colors[hash_val % len(fallback_colors)]


def clean_numeric_columns(df):
    """Clean numeric columns (remove trailing zeros/dots)"""
    numeric_cols = [COL_STARTFRAME, COL_ENDFRAME]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: safe_str(x).rstrip('0').rstrip('.') if '.' in safe_str(x) else safe_str(x)
            )

    return df


def clean_dataframe_none_values(df):
    """Replace None/NaN/NONE with empty strings"""
    for col in df.columns:
        df[col] = df[col].apply(
            lambda x: "" if safe_str(x).upper() in ["NONE", "NAN", ""] else safe_str(x)
        )
    return df


def generate_previous_data(prev_row, text_col, status_col, freememo_col):
    """Generate PreviousData string from previous row"""
    if not prev_row:
        return ""

    parts = [
        safe_str(prev_row.get(COL_STRORIGIN, "")),
        safe_str(prev_row.get(text_col, "")),
        safe_str(prev_row.get(status_col, "")),
        safe_str(prev_row.get(freememo_col, "")),
        safe_str(prev_row.get(COL_STARTFRAME, ""))
    ]

    return "|".join(parts)
