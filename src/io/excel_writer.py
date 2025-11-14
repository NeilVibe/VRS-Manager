"""
Excel writing and column filtering module.

This module provides functionality to filter dataframe columns
before writing to Excel output files.
"""

from src.config import OUTPUT_COLUMNS


def filter_output_columns(df, column_list=OUTPUT_COLUMNS):
    """
    Filter a dataframe to only include columns that exist in both the
    dataframe and the specified column list.

    Args:
        df: DataFrame to filter
        column_list: List of column names to keep (default: OUTPUT_COLUMNS)

    Returns:
        DataFrame: Filtered dataframe with only the specified columns
    """
    available_cols = [col for col in column_list if col in df.columns]
    return df[available_cols]
