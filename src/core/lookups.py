"""
Lookup dictionary building module.

This module provides functionality to build lookup dictionaries for
efficient row matching using the 10-key system:
1. (S, E) - Sequence + Event
2. (S, O) - Sequence + StrOrigin
3. (S, C) - Sequence + CastingKey
4. (E, O) - Event + StrOrigin
5. (E, C) - Event + CastingKey
6. (O, C) - StrOrigin + CastingKey
7. (S, E, O) - Sequence + Event + StrOrigin
8. (S, E, C) - Sequence + Event + CastingKey
9. (S, O, C) - Sequence + StrOrigin + CastingKey
10. (E, O, C) - Event + StrOrigin + CastingKey
"""

from src.config import (
    COL_SEQUENCE, COL_EVENTNAME, COL_STRORIGIN, COL_CASTINGKEY
)
from src.utils.progress import print_progress, finalize_progress
from src.utils.data_processing import safe_str


def build_lookups(df):
    """
    Build 10 lookup dictionaries for comprehensive matching (10-Key System).

    Creates fast lookup dictionaries for the raw VRS check process using
    all possible 2-field and 3-field key combinations to precisely identify
    what changed between previous and current files.

    TWO-PASS ALGORITHM: Lookups now store DataFrame INDEX only (not full rows).
    This prevents 1-to-many matching issues with duplicate StrOrigin/CastingKey.

    Args:
        df: DataFrame to build lookups from

    Returns:
        tuple: (lookup_se, lookup_so, lookup_sc, lookup_eo, lookup_ec,
                lookup_oc, lookup_seo, lookup_sec, lookup_soc, lookup_eoc) where:
            - Each lookup maps keys to DataFrame INDEX (int)
            - Use df.loc[index] to retrieve row when needed
    """
    # Initialize all 10 lookups (2-key combinations)
    lookup_se = {}   # (Sequence, Event) → DataFrame index
    lookup_so = {}   # (Sequence, StrOrigin) → DataFrame index
    lookup_sc = {}   # (Sequence, CastingKey) → DataFrame index
    lookup_eo = {}   # (Event, StrOrigin) → DataFrame index
    lookup_ec = {}   # (Event, CastingKey) → DataFrame index
    lookup_oc = {}   # (StrOrigin, CastingKey) → DataFrame index

    # 3-key combinations
    lookup_seo = {}  # (Sequence, Event, StrOrigin) → DataFrame index
    lookup_sec = {}  # (Sequence, Event, CastingKey) → DataFrame index
    lookup_soc = {}  # (Sequence, StrOrigin, CastingKey) → DataFrame index
    lookup_eoc = {}  # (Event, StrOrigin, CastingKey) → DataFrame index

    total = len(df)
    progress_count = 0

    for df_idx, row in df.iterrows():
        S = safe_str(row.get(COL_SEQUENCE, ""))
        E = safe_str(row.get(COL_EVENTNAME, ""))
        O = safe_str(row.get(COL_STRORIGIN, ""))
        C = safe_str(row.get(COL_CASTINGKEY, ""))

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

        # Store DataFrame INDEX in each lookup (first occurrence only)
        if key_se not in lookup_se:
            lookup_se[key_se] = df_idx
        if key_so not in lookup_so:
            lookup_so[key_so] = df_idx
        if key_sc not in lookup_sc:
            lookup_sc[key_sc] = df_idx
        if key_eo not in lookup_eo:
            lookup_eo[key_eo] = df_idx
        if key_ec not in lookup_ec:
            lookup_ec[key_ec] = df_idx
        if key_oc not in lookup_oc:
            lookup_oc[key_oc] = df_idx
        if key_seo not in lookup_seo:
            lookup_seo[key_seo] = df_idx
        if key_sec not in lookup_sec:
            lookup_sec[key_sec] = df_idx
        if key_soc not in lookup_soc:
            lookup_soc[key_soc] = df_idx
        if key_eoc not in lookup_eoc:
            lookup_eoc[key_eoc] = df_idx

        progress_count += 1
        if progress_count % 500 == 0 or progress_count == total:
            print_progress(progress_count, total, "Building 10-key lookups")

    finalize_progress()
    return (lookup_se, lookup_so, lookup_sc, lookup_eo, lookup_ec,
            lookup_oc, lookup_seo, lookup_sec, lookup_soc, lookup_eoc)
