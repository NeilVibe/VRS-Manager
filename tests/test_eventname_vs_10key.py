"""
Compare EventName-only matching vs 10-Key matching for word count accuracy.

This test runs BOTH approaches on the same data and compares results:
- Approach A: Simple EventName matching
- Approach B: Current 10-Key TWO-PASS system

Goal: Determine if EventName-only matching is sufficient for accurate word counting.
"""

import pandas as pd
import os
import sys
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.io.excel_reader import safe_read_excel
from src.utils.data_processing import normalize_dataframe_status, remove_full_duplicates
from src.core.casting import generate_casting_key
from src.config import COL_CASTINGKEY, COL_CHARACTERKEY, COL_DIALOGVOICE, COL_SPEAKER_GROUPKEY, COL_STRORIGIN, COL_TEXT, COL_EVENTNAME, COL_GROUP
from src.core.lookups import build_lookups
from src.core.comparison import compare_rows, find_deleted_rows
from src.utils.super_groups import aggregate_to_super_groups, classify_super_group
from src.utils.helpers import safe_str


def approach_a_eventname_matching(df_prev, df_curr):
    """
    Approach A: Simple EventName-only matching.

    Returns super group statistics using EventName as the only matching key.
    """
    print("\n" + "="*80)
    print("APPROACH A: EVENTNAME-ONLY MATCHING")
    print("="*80)

    # Initialize super group stats
    super_groups = [
        "Main Chapters", "Faction 1", "Faction 2", "Faction 3",
        "Quest Dialog", "AI Dialog", "Others", "Other", "Everything Else"
    ]

    stats = {}
    for sg in super_groups:
        stats[sg] = {
            "total_words_prev": 0,
            "total_words_curr": 0,
            "added_words": 0,
            "deleted_words": 0,
            "changed_words": 0,
            "unchanged_words": 0,
            "migrated_in_words": 0,
            "migrated_out_words": 0,
            "translated_words": 0,
            "untranslated_words": 0
        }

    # Create EventName lookup for PREVIOUS
    prev_lookup = {}
    for idx, row in df_prev.iterrows():
        event_name = safe_str(row.get(COL_EVENTNAME, ""))
        if event_name in prev_lookup:
            print(f"  ⚠️  WARNING: Duplicate EventName in PREVIOUS: '{event_name}'")
        prev_lookup[event_name] = idx

    print(f"  → Indexed {len(prev_lookup)} EventNames in PREVIOUS")

    # Create EventName lookup for CURRENT
    curr_lookup = {}
    for idx, row in df_curr.iterrows():
        event_name = safe_str(row.get(COL_EVENTNAME, ""))
        if event_name in curr_lookup:
            print(f"  ⚠️  WARNING: Duplicate EventName in CURRENT: '{event_name}'")
        curr_lookup[event_name] = idx

    print(f"  → Indexed {len(curr_lookup)} EventNames in CURRENT")

    matched_prev_indices = set()

    # Process CURRENT rows
    for curr_idx, curr_row in df_curr.iterrows():
        event_name = safe_str(curr_row.get(COL_EVENTNAME, ""))
        curr_group = curr_row.get(COL_GROUP, "Unknown")
        curr_super_group = classify_super_group(curr_row, curr_group)

        curr_strorigin = safe_str(curr_row.get(COL_STRORIGIN, ""))
        curr_words = len(curr_strorigin.split()) if curr_strorigin else 0

        # Check translation
        curr_text = safe_str(curr_row.get(COL_TEXT, "")).lower()
        is_translated = "no translation" not in curr_text

        if event_name in prev_lookup:
            # MATCHED by EventName
            prev_idx = prev_lookup[event_name]
            matched_prev_indices.add(prev_idx)

            prev_row = df_prev.loc[prev_idx]
            prev_group = prev_row.get(COL_GROUP, "Unknown")
            prev_super_group = classify_super_group(prev_row, prev_group)

            prev_strorigin = safe_str(prev_row.get(COL_STRORIGIN, ""))
            prev_words = len(prev_strorigin.split()) if prev_strorigin else 0

            # Add to totals
            stats[prev_super_group]["total_words_prev"] += prev_words
            stats[curr_super_group]["total_words_curr"] += curr_words

            # Track translation
            if is_translated:
                stats[curr_super_group]["translated_words"] += curr_words
            else:
                stats[curr_super_group]["untranslated_words"] += curr_words

            # Check if super group changed
            if curr_super_group == prev_super_group:
                # Same super group
                if curr_strorigin == prev_strorigin:
                    stats[curr_super_group]["unchanged_words"] += curr_words
                else:
                    stats[curr_super_group]["changed_words"] += curr_words
            else:
                # MIGRATION
                stats[prev_super_group]["migrated_out_words"] += prev_words
                stats[curr_super_group]["migrated_in_words"] += curr_words
        else:
            # NEW ROW (no match in PREVIOUS)
            stats[curr_super_group]["added_words"] += curr_words
            stats[curr_super_group]["total_words_curr"] += curr_words

            # Track translation
            if is_translated:
                stats[curr_super_group]["translated_words"] += curr_words
            else:
                stats[curr_super_group]["untranslated_words"] += curr_words

    # Process DELETED rows (in PREVIOUS but not matched)
    deleted_indices = [idx for idx in df_prev.index if idx not in matched_prev_indices]

    for del_idx in deleted_indices:
        del_row = df_prev.loc[del_idx]
        del_group = del_row.get(COL_GROUP, "Unknown")
        del_super_group = classify_super_group(del_row, del_group)

        del_strorigin = safe_str(del_row.get(COL_STRORIGIN, ""))
        del_words = len(del_strorigin.split()) if del_strorigin else 0

        stats[del_super_group]["total_words_prev"] += del_words
        stats[del_super_group]["deleted_words"] += del_words

    print(f"  → Matched {len(matched_prev_indices)} rows by EventName")
    print(f"  → Found {len(curr_lookup) - len(matched_prev_indices)} new rows")
    print(f"  → Found {len(deleted_indices)} deleted rows")

    return stats


def approach_b_10key_matching(df_prev, df_curr):
    """
    Approach B: Current 10-Key TWO-PASS matching system.

    Returns super group statistics using the full 10-key matching logic.
    """
    print("\n" + "="*80)
    print("APPROACH B: 10-KEY TWO-PASS MATCHING")
    print("="*80)

    # Generate CastingKey
    for df in [df_prev, df_curr]:
        casting_keys = []
        for idx, row in df.iterrows():
            casting_key = generate_casting_key(
                row.get(COL_CHARACTERKEY, ""),
                row.get(COL_DIALOGVOICE, ""),
                row.get(COL_SPEAKER_GROUPKEY, ""),
                row.get("DialogType", "")
            )
            casting_keys.append(casting_key)
        df[COL_CASTINGKEY] = casting_keys

    # Build lookups
    (prev_lookup_se, prev_lookup_so, prev_lookup_sc, prev_lookup_eo,
     prev_lookup_ec, prev_lookup_oc, prev_lookup_seo, prev_lookup_sec,
     prev_lookup_soc, prev_lookup_eoc) = build_lookups(df_prev)

    print(f"  → Built 10-key lookups for {len(prev_lookup_se)} unique PREVIOUS rows")

    # Run TWO-PASS comparison
    changes, previous_strorigins, changed_columns_map, counter, marked_prev_indices, group_analysis, pass1_results = compare_rows(
        df_curr, df_prev,
        prev_lookup_se, prev_lookup_so, prev_lookup_sc,
        prev_lookup_eo, prev_lookup_ec, prev_lookup_oc,
        prev_lookup_seo, prev_lookup_sec, prev_lookup_soc, prev_lookup_eoc
    )

    print(f"  → Matched {len(marked_prev_indices)} rows using 10-key system")

    # Find deleted rows
    df_deleted = find_deleted_rows(df_prev, df_curr, marked_prev_indices)
    print(f"  → Found {len(df_deleted)} deleted rows")

    # Aggregate to super groups
    stats, migration_details = aggregate_to_super_groups(df_curr, df_prev, pass1_results)

    return stats


def compare_results(stats_a, stats_b):
    """Compare results from both approaches and report differences."""
    print("\n" + "="*80)
    print("COMPARISON RESULTS")
    print("="*80)

    all_super_groups = sorted(set(list(stats_a.keys()) + list(stats_b.keys())))

    differences_found = False

    for sg in all_super_groups:
        a = stats_a.get(sg, {})
        b = stats_b.get(sg, {})

        # Skip if both are zero
        if (a.get("total_words_prev", 0) == 0 and a.get("total_words_curr", 0) == 0 and
            b.get("total_words_prev", 0) == 0 and b.get("total_words_curr", 0) == 0):
            continue

        print(f"\n{sg}:")
        print(f"{'Metric':<25} {'EventName':>12} {'10-Key':>12} {'Match':>8}")
        print(f"{'-'*25} {'-'*12} {'-'*12} {'-'*8}")

        metrics = [
            "total_words_prev",
            "total_words_curr",
            "added_words",
            "deleted_words",
            "changed_words",
            "unchanged_words",
            "migrated_in_words",
            "migrated_out_words",
            "translated_words",
            "untranslated_words"
        ]

        for metric in metrics:
            val_a = a.get(metric, 0)
            val_b = b.get(metric, 0)
            match = "✓" if val_a == val_b else "✗"

            if val_a != val_b:
                differences_found = True

            print(f"{metric:<25} {val_a:>12,} {val_b:>12,} {match:>8}")

    return differences_found


def main():
    """Run the comparison test."""
    print("="*80)
    print("WORD COUNT LOGIC COMPARISON TEST")
    print("EventName-Only Matching vs 10-Key TWO-PASS Matching")
    print("="*80)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    prev_path = os.path.join(script_dir, "test_supergroup_PREVIOUS.xlsx")
    curr_path = os.path.join(script_dir, "test_supergroup_CURRENT.xlsx")

    # Read files
    print("\nReading test files...")
    df_prev = safe_read_excel(prev_path, header=0, dtype=str)
    df_curr = safe_read_excel(curr_path, header=0, dtype=str)

    print(f"  PREVIOUS: {len(df_prev):,} rows")
    print(f"  CURRENT:  {len(df_curr):,} rows")

    # Normalize
    df_prev = normalize_dataframe_status(df_prev)
    df_curr = normalize_dataframe_status(df_curr)

    df_prev = remove_full_duplicates(df_prev, "PREVIOUS")
    df_curr = remove_full_duplicates(df_curr, "CURRENT")

    # Check for duplicate EventNames
    print("\nChecking EventName uniqueness...")
    prev_eventnames = df_prev[COL_EVENTNAME].tolist()
    curr_eventnames = df_curr[COL_EVENTNAME].tolist()

    prev_dupes = len(prev_eventnames) - len(set(prev_eventnames))
    curr_dupes = len(curr_eventnames) - len(set(curr_eventnames))

    if prev_dupes > 0:
        print(f"  ⚠️  PREVIOUS has {prev_dupes} duplicate EventNames")
    else:
        print(f"  ✓ PREVIOUS has NO duplicate EventNames")

    if curr_dupes > 0:
        print(f"  ⚠️  CURRENT has {curr_dupes} duplicate EventNames")
    else:
        print(f"  ✓ CURRENT has NO duplicate EventNames")

    # Run both approaches
    stats_a = approach_a_eventname_matching(df_prev.copy(), df_curr.copy())
    stats_b = approach_b_10key_matching(df_prev.copy(), df_curr.copy())

    # Compare results
    differences_found = compare_results(stats_a, stats_b)

    # Final verdict
    print("\n" + "="*80)
    print("FINAL VERDICT")
    print("="*80)

    if not differences_found:
        print("\n✓✓✓ RESULTS ARE IDENTICAL ✓✓✓")
        print("\nConclusion:")
        print("  EventName-only matching produces the same results as 10-key matching.")
        print("  For this dataset, the 10-key system may be unnecessary complexity.")
        print("  EventName appears to be unique and sufficient for accurate word counting.")
    else:
        print("\n✗✗✗ DIFFERENCES FOUND ✗✗✗")
        print("\nConclusion:")
        print("  EventName-only matching produces DIFFERENT results from 10-key matching.")
        print("  The 10-key system is necessary for accurate word counting.")
        print("  Possible reasons:")
        print("    - EventName duplicates exist")
        print("    - EventName changes between files")
        print("    - 10-key system finds matches that EventName misses")

    print("\n" + "="*80)

    return not differences_found


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
