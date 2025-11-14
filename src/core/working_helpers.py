"""
Helper functions for Working VRS Check process.

This module contains utility functions specific to Working process operations,
including building lookups and finding deleted rows with the 4-tier key system.
"""

import pandas as pd
from src.config import COL_SEQUENCE, COL_EVENTNAME, COL_STRORIGIN, COL_CASTINGKEY
from src.utils.helpers import log
from src.utils.progress import print_progress, finalize_progress


def build_working_lookups(df, label="PREVIOUS"):
    """
    Build 4 lookup dictionaries for Working Process (4-Tier Key System).

    Args:
        df: DataFrame to build lookups from
        label: Label for logging (default: "PREVIOUS")

    Returns:
        tuple: (lookup_cw, lookup_cg, lookup_es, lookup_cs) where:
            - lookup_cw: Dictionary keyed by (SequenceName, EventName)
            - lookup_cg: Dictionary keyed by (SequenceName, StrOrigin) -> EventName
            - lookup_es: Dictionary keyed by (EventName, StrOrigin)
            - lookup_cs: Dictionary keyed by (CastingKey, SequenceName)
    """
    lookup_cw = {}
    lookup_cg = {}
    lookup_es = {}
    lookup_cs = {}

    total = len(df)
    log(f"Building {label} lookup dictionaries...")

    for idx, row in df.iterrows():
        row_dict = row.to_dict()

        key_cw = (row[COL_SEQUENCE], row[COL_EVENTNAME])
        key_cg = (row[COL_SEQUENCE], row[COL_STRORIGIN])
        key_es = (row[COL_EVENTNAME], row[COL_STRORIGIN])
        key_cs = (row[COL_CASTINGKEY], row[COL_SEQUENCE])

        if key_cw not in lookup_cw:
            lookup_cw[key_cw] = row_dict
        if key_cg not in lookup_cg:
            lookup_cg[key_cg] = row[COL_EVENTNAME]
        if key_es not in lookup_es:
            lookup_es[key_es] = row_dict
        if key_cs not in lookup_cs:
            lookup_cs[key_cs] = row_dict

        if (idx + 1) % 500 == 0 or idx == total - 1:
            print_progress(idx + 1, total, f"Indexing {label}")

    finalize_progress()
    log(f"  → Indexed {len(lookup_cw):,} unique {label} rows")
    return lookup_cw, lookup_cg, lookup_es, lookup_cs


def find_working_deleted_rows(df_prev, df_curr):
    """
    Find deleted rows using 4-key system (4-Tier Key System).

    A row is only considered deleted if ALL 4 keys are missing from current.

    Args:
        df_prev: Previous DataFrame
        df_curr: Current DataFrame

    Returns:
        DataFrame: Deleted rows
    """
    log("Finding deleted rows (PREVIOUS rows not in CURRENT)...")

    # Build all 4 key types for current data
    curr_keys_cw = set((row[COL_SEQUENCE], row[COL_EVENTNAME]) for _, row in df_curr.iterrows())
    curr_keys_cg = set((row[COL_SEQUENCE], row[COL_STRORIGIN]) for _, row in df_curr.iterrows())
    curr_keys_es = set((row[COL_EVENTNAME], row[COL_STRORIGIN]) for _, row in df_curr.iterrows())
    curr_keys_cs = set((row[COL_CASTINGKEY], row[COL_SEQUENCE]) for _, row in df_curr.iterrows())

    deleted_rows = []

    for idx, row in df_prev.iterrows():
        key_cw = (row[COL_SEQUENCE], row[COL_EVENTNAME])
        key_cg = (row[COL_SEQUENCE], row[COL_STRORIGIN])
        key_es = (row[COL_EVENTNAME], row[COL_STRORIGIN])
        key_cs = (row[COL_CASTINGKEY], row[COL_SEQUENCE])

        # Only mark as deleted if ALL 4 keys are missing
        if (key_cw not in curr_keys_cw) and \
           (key_cg not in curr_keys_cg) and \
           (key_es not in curr_keys_es) and \
           (key_cs not in curr_keys_cs):
            deleted_rows.append(row.to_dict())

    log(f"  → Found {len(deleted_rows):,} deleted rows")
    return pd.DataFrame(deleted_rows) if deleted_rows else pd.DataFrame()
