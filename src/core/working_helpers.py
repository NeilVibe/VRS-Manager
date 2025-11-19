"""
Helper functions for Working VRS Check process.

This module contains utility functions specific to Working process operations,
including building lookups and finding deleted rows with the 10-key system.
"""

import pandas as pd
from src.config import COL_SEQUENCE, COL_EVENTNAME, COL_STRORIGIN, COL_CASTINGKEY
from src.utils.helpers import log
from src.utils.progress import print_progress, finalize_progress


def build_working_lookups(df, label="PREVIOUS"):
    """
    Build 10 lookup dictionaries for Working Process (10-Key System).

    Args:
        df: DataFrame to build lookups from
        label: Label for logging (default: "PREVIOUS")

    Returns:
        tuple: (lookup_se, lookup_so, lookup_sc, lookup_eo, lookup_ec,
                lookup_oc, lookup_seo, lookup_sec, lookup_soc, lookup_eoc)
    """
    # Initialize all 10 lookups
    lookup_se = {}
    lookup_so = {}
    lookup_sc = {}
    lookup_eo = {}
    lookup_ec = {}
    lookup_oc = {}
    lookup_seo = {}
    lookup_sec = {}
    lookup_soc = {}
    lookup_eoc = {}

    total = len(df)
    log(f"Building {label} lookup dictionaries (10-key system)...")

    for idx, row in df.iterrows():
        row_dict = row.to_dict()

        S = row[COL_SEQUENCE]
        E = row[COL_EVENTNAME]
        O = row[COL_STRORIGIN]
        C = row[COL_CASTINGKEY]

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

        # Store row_dict in each lookup (first occurrence only)
        if key_se not in lookup_se:
            lookup_se[key_se] = row_dict
        if key_so not in lookup_so:
            lookup_so[key_so] = row[COL_EVENTNAME]  # Store EventName for backwards compat
        if key_sc not in lookup_sc:
            lookup_sc[key_sc] = row_dict
        if key_eo not in lookup_eo:
            lookup_eo[key_eo] = row_dict
        if key_ec not in lookup_ec:
            lookup_ec[key_ec] = row_dict
        if key_oc not in lookup_oc:
            lookup_oc[key_oc] = row_dict
        if key_seo not in lookup_seo:
            lookup_seo[key_seo] = row_dict
        if key_sec not in lookup_sec:
            lookup_sec[key_sec] = row_dict
        if key_soc not in lookup_soc:
            lookup_soc[key_soc] = row_dict
        if key_eoc not in lookup_eoc:
            lookup_eoc[key_eoc] = row_dict

        if (idx + 1) % 500 == 0 or idx == total - 1:
            print_progress(idx + 1, total, f"Indexing {label}")

    finalize_progress()
    log(f"  → Indexed {len(lookup_se):,} unique {label} rows (10-key system)")
    return (lookup_se, lookup_so, lookup_sc, lookup_eo, lookup_ec,
            lookup_oc, lookup_seo, lookup_sec, lookup_soc, lookup_eoc)


def find_working_deleted_rows(df_prev, df_curr, marked_prev_indices):
    """
    Find deleted rows using TWO-PASS algorithm.

    A row is considered deleted if it was NOT marked in PASS 1/2.

    Args:
        df_prev: Previous DataFrame
        df_curr: Current DataFrame (not used but kept for compatibility)
        marked_prev_indices: Set of previous indices that were matched

    Returns:
        DataFrame: Deleted rows
    """
    log("Finding deleted rows (TWO-PASS algorithm)...")

    deleted_indices = [idx for idx in df_prev.index if idx not in marked_prev_indices]

    if deleted_indices:
        result = df_prev.loc[deleted_indices].copy()
        log(f"  → Found {len(result)} deleted rows")
        return result
    else:
        log("  → No deleted rows")
        return df_prev.iloc[0:0].copy()  # Return empty DataFrame with same columns
