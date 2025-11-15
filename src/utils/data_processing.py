"""
Data processing utility functions.

This module provides common data processing functions used across processors,
including status normalization, column filtering, and dataframe cleaning.
"""

import pandas as pd
from src.config import OUTPUT_COLUMNS
from src.utils.helpers import safe_str


def find_status_column(columns):
    """
    Find the STATUS column in a list of columns (case-insensitive).

    Args:
        columns: List of column names

    Returns:
        str: The STATUS column name, or None if not found
    """
    for col in columns:
        if col.upper() == "STATUS":
            return col
    return None


def normalize_status(status_value):
    """
    Normalize a status value to uppercase.

    Args:
        status_value: Status value to normalize

    Returns:
        str: Normalized status (uppercase, empty if null)
    """
    clean_val = safe_str(status_value)
    if not clean_val:
        return ""
    return clean_val.upper()


def normalize_dataframe_status(df):
    """
    Normalize all STATUS columns in a DataFrame to uppercase and rename to 'STATUS'.

    Args:
        df: DataFrame to normalize

    Returns:
        DataFrame: DataFrame with normalized STATUS column
    """
    status_col = find_status_column(df.columns)
    if status_col:
        df[status_col] = df[status_col].apply(normalize_status)
        if status_col != "STATUS":
            df.rename(columns={status_col: "STATUS"}, inplace=True)
    return df


def filter_output_columns(df, column_list=OUTPUT_COLUMNS):
    """
    Filter DataFrame to only include columns that exist in the specified column list.

    Args:
        df: DataFrame to filter
        column_list: List of desired output columns

    Returns:
        DataFrame: Filtered DataFrame
    """
    available_cols = [col for col in column_list if col in df.columns]
    return df[available_cols]


def clean_numeric_columns(df):
    """
    Clean numeric columns by removing trailing zeros after decimal points.

    Args:
        df: DataFrame to clean

    Returns:
        DataFrame: DataFrame with cleaned numeric columns
    """
    from src.config import COL_STARTFRAME, COL_ENDFRAME

    numeric_cols = [COL_STARTFRAME, COL_ENDFRAME]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: safe_str(x).rstrip('0').rstrip('.') if '.' in safe_str(x) else safe_str(x))

    return df


def clean_dataframe_none_values(df):
    """
    Replace None, NaN, and 'NONE' string values with empty strings.

    Args:
        df: DataFrame to clean

    Returns:
        DataFrame: DataFrame with cleaned values
    """
    for col in df.columns:
        df[col] = df[col].apply(lambda x: "" if safe_str(x).upper() in ["NONE", "NAN", ""] else safe_str(x))
    return df
