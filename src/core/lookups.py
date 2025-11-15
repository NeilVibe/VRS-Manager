"""
Lookup dictionary building module.

This module provides functionality to build lookup dictionaries for
efficient row matching using the 4-tier key system:
1. (SequenceName, EventName)
2. (SequenceName, StrOrigin)
3. (EventName, StrOrigin)
4. (CastingKey, SequenceName)
"""

from src.config import (
    COL_SEQUENCE, COL_EVENTNAME, COL_STRORIGIN, COL_CASTINGKEY
)
from src.utils.progress import print_progress, finalize_progress


def build_lookups(df):
    """
    Build 4 lookup dictionaries for matching (4-Tier Key System).

    Creates fast lookup dictionaries for the raw VRS check process using
    four different key combinations to match rows between previous and
    current files.

    Args:
        df: DataFrame to build lookups from

    Returns:
        tuple: (lookup_cw, lookup_cg, lookup_es, lookup_cs) where:
            - lookup_cw: dict with (SequenceName, EventName) keys
            - lookup_cg: dict with (SequenceName, StrOrigin) keys
            - lookup_es: dict with (EventName, StrOrigin) keys
            - lookup_cs: dict with (CastingKey, SequenceName) keys
    """
    lookup_cw = {}  # (SequenceName, EventName)
    lookup_cg = {}  # (SequenceName, StrOrigin)
    lookup_es = {}  # (EventName, StrOrigin)
    lookup_cs = {}  # (CastingKey, SequenceName)

    col_idx = {col: i for i, col in enumerate(df.columns)}

    total = len(df)
    for idx, row in enumerate(df.itertuples(index=False, name=None)):
        key_cw = (row[col_idx[COL_SEQUENCE]], row[col_idx[COL_EVENTNAME]])
        key_cg = (row[col_idx[COL_SEQUENCE]], row[col_idx[COL_STRORIGIN]])
        key_es = (row[col_idx[COL_EVENTNAME]], row[col_idx[COL_STRORIGIN]])
        key_cs = (row[col_idx[COL_CASTINGKEY]], row[col_idx[COL_SEQUENCE]])

        if key_cw not in lookup_cw:
            lookup_cw[key_cw] = row
        if key_cg not in lookup_cg:
            lookup_cg[key_cg] = row[col_idx[COL_EVENTNAME]]
        if key_es not in lookup_es:
            lookup_es[key_es] = row
        if key_cs not in lookup_cs:
            lookup_cs[key_cs] = row

        if (idx + 1) % 500 == 0 or idx == total - 1:
            print_progress(idx + 1, total, "Building lookups")

    finalize_progress()
    return lookup_cw, lookup_cg, lookup_es, lookup_cs


def build_working_lookups(df, label="PREVIOUS"):
    """
    Build 4 lookup dictionaries for Working Process (4-Tier Key System).

    Similar to build_lookups but optimized for the working process,
    using DataFrame iteration and providing logging feedback.

    Args:
        df: DataFrame to build lookups from
        label: Label for progress messages (default: "PREVIOUS")

    Returns:
        tuple: (lookup_cw, lookup_cg, lookup_es, lookup_cs) where:
            - lookup_cw: dict with (SequenceName, EventName) keys
            - lookup_cg: dict with (SequenceName, StrOrigin) keys
            - lookup_es: dict with (EventName, StrOrigin) keys
            - lookup_cs: dict with (CastingKey, SequenceName) keys
    """
    from src.utils.helpers import log

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
