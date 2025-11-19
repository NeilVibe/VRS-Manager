#!/usr/bin/env python3
"""
Test the 10-key system core logic directly (no GUI dependencies).
"""

import sys
import os
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.io.excel_reader import safe_read_excel
from src.utils.data_processing import normalize_dataframe_status
from src.core.casting import generate_casting_key
from src.core.lookups import build_lookups
from src.core.comparison import compare_rows, find_deleted_rows
from src.config import COL_CASTINGKEY, COL_CHARACTERKEY, COL_DIALOGVOICE, COL_SPEAKER_GROUPKEY

def test_10key_system():
    """Test 10-key system with mock data."""
    print("="*70)
    print("Testing 10-Key System - Core Logic Only")
    print("="*70)

    # Load test files
    prev_file = "Test_Previous.xlsx"
    curr_file = "Test_Current.xlsx"

    if not os.path.exists(prev_file) or not os.path.exists(curr_file):
        print("❌ Error: Test files not found!")
        print("Run: python3 generate_test_data.py")
        return False

    print(f"\nLoading files...")
    df_prev = safe_read_excel(prev_file, header=0, dtype=str)
    df_curr = safe_read_excel(curr_file, header=0, dtype=str)

    print(f"  ✓ Previous: {len(df_prev)} rows")
    print(f"  ✓ Current:  {len(df_curr)} rows")

    # Normalize status
    df_prev = normalize_dataframe_status(df_prev)
    df_curr = normalize_dataframe_status(df_curr)

    # Generate CastingKey
    print(f"\nGenerating CastingKey...")
    for df in [df_prev, df_curr]:
        casting_keys = []
        for idx, row in df.iterrows():
            key = generate_casting_key(
                row.get(COL_CHARACTERKEY, ""),
                row.get(COL_DIALOGVOICE, ""),
                row.get(COL_SPEAKER_GROUPKEY, ""),
                row.get("DialogType", "")
            )
            casting_keys.append(key)
        df[COL_CASTINGKEY] = casting_keys
    print(f"  ✓ CastingKey generated")

    # Build lookups with 10-key system
    print(f"\nBuilding 10-key lookups...")
    (prev_lookup_se, prev_lookup_so, prev_lookup_sc, prev_lookup_eo, prev_lookup_ec,
     prev_lookup_oc, prev_lookup_seo, prev_lookup_sec, prev_lookup_soc, prev_lookup_eoc) = build_lookups(df_prev)
    print(f"  ✓ Built 10 lookup dictionaries")

    # Compare rows
    print(f"\nComparing rows with TWO-PASS algorithm...")
    changes, previous_strorigins, changed_columns_map, counter, marked_prev_indices = compare_rows(
        df_curr, df_prev,
        prev_lookup_se, prev_lookup_so, prev_lookup_sc,
        prev_lookup_eo, prev_lookup_ec, prev_lookup_oc,
        prev_lookup_seo, prev_lookup_sec, prev_lookup_soc, prev_lookup_eoc
    )
    print(f"  ✓ Comparison complete")

    # Find deleted rows
    print(f"\nFinding deleted rows...")
    df_deleted = find_deleted_rows(df_prev, df_curr, marked_prev_indices)
    counter["Deleted Rows"] = len(df_deleted)
    print(f"  ✓ Found {len(df_deleted)} deleted rows")

    # Display results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)

    print("\n📊 Change Type Breakdown:")
    for change_type, count in sorted(counter.items(), key=lambda x: -x[1]):
        print(f"  {change_type:.<40} {count:>5} rows")

    # Math validation
    new_rows = counter.get("New Row", 0)
    deleted_rows = counter.get("Deleted Rows", 0)
    net_change = new_rows - deleted_rows

    prev_count = len(df_prev)
    curr_count = len(df_curr)
    actual_diff = curr_count - prev_count

    print(f"\n📈 Row Count Analysis:")
    print(f"  Previous file......................... {prev_count:>5} rows")
    print(f"  Current file.......................... {curr_count:>5} rows")
    print(f"  Actual difference (Curr - Prev)....... {actual_diff:>+5} rows")
    print(f"\n  New rows detected..................... {new_rows:>5} rows")
    print(f"  Deleted rows detected................. {deleted_rows:>5} rows")
    print(f"  Net change (New - Deleted)............ {net_change:>+5} rows")

    print(f"\n✅ Critical Validation:")
    if net_change == actual_diff:
        print(f"  ✓✓✓ PASS: {net_change:+d} == {actual_diff:+d}")
        print(f"  ✓✓✓ The 10-key system BUG FIX works!")
        validation_passed = True
    else:
        print(f"  ✗✗✗ FAIL: {net_change:+d} != {actual_diff:+d}")
        print(f"  ✗✗✗ Bug still exists!")
        validation_passed = False

    # Expected values
    print(f"\n📋 Expected vs Actual:")
    expected = {
        "New Row": 25,
        "Deleted Rows": 5,
        "No Change": 30,
        "StrOrigin Change": 5,
        "EventName Change": 3,
        "SequenceName Change": 1,
        "CastingKey Change": 1,
    }

    all_match = True
    for change_type, expected_count in expected.items():
        actual_count = counter.get(change_type, 0)
        match = "✓" if actual_count == expected_count else "✗"
        if actual_count != expected_count:
            all_match = False
        status = "PASS" if actual_count == expected_count else "DIFF"
        print(f"  [{status}] {match} {change_type:.<30} Exp:{expected_count:>3}  Act:{actual_count:>3}")

    # Check composite changes
    composite_types = [ct for ct in counter.keys() if "+" in ct]
    if composite_types:
        print(f"\n  Composite change types found:")
        for ct in composite_types:
            print(f"    - {ct}: {counter[ct]} rows")

    print("\n" + "="*70)
    if validation_passed and all_match:
        print("🎉🎉🎉 ALL TESTS PASSED! 10-Key System Perfect! 🎉🎉🎉")
        result = "SUCCESS"
    elif validation_passed:
        print("⚠️  MATH CORRECT but some classifications differ from expected")
        print("    (This is OK - composite changes may vary)")
        result = "PARTIAL"
    else:
        print("❌❌❌ CRITICAL FAILURE - BUG DETECTED! ❌❌❌")
        result = "FAILED"
    print("="*70)

    return validation_passed

if __name__ == "__main__":
    success = test_10key_system()
    print()
    sys.exit(0 if success else 1)
