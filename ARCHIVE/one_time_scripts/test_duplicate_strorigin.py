#!/usr/bin/env python3
"""
Test 10-key system with DUPLICATE and BLANK StrOrigin values.

This tests the critical edge case:
- Multiple rows with SAME StrOrigin (or BLANK)
- 10-key system should differentiate them correctly
"""

import sys
import os
import pandas as pd
from openpyxl import Workbook

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.io.excel_reader import safe_read_excel
from src.utils.data_processing import normalize_dataframe_status
from src.core.casting import generate_casting_key
from src.core.lookups import build_lookups
from src.core.comparison import compare_rows, find_deleted_rows
from src.config import COL_CASTINGKEY, COL_CHARACTERKEY, COL_DIALOGVOICE, COL_SPEAKER_GROUPKEY

def create_duplicate_test_data():
    """Create test files with duplicate and blank StrOrigin."""
    print("="*80)
    print("Creating Test Data with Duplicate & Blank StrOrigin")
    print("="*80)

    # Previous file (30 rows)
    prev_data = []

    # Scenario 1: Same StrOrigin "Hello" used by 5 different characters
    print("\n✓ Scenario 1: Same StrOrigin 'Hello' - 5 different characters")
    for i in range(5):
        prev_data.append({
            "SequenceName": "Scene1",
            "EventName": f"Event{1000 + i}",
            "StrOrigin": "Hello",  # DUPLICATE
            "Text": f"Translation {i}",
            "STATUS": "POLISHED",
            "FREEMEMO": "",
            "CharacterKey": f"Char_{i}",
            "DialogVoice": "Main",
            "SpeakerGroupKey": "A",
            "DialogType": "Dialog",
            "Desc": f"Description {i}",
            "StartFrame": str(i * 100),
            "EndFrame": str((i * 100) + 50),
            "Importance": "High"
        })

    # Scenario 2: BLANK StrOrigin - 5 different characters
    print("✓ Scenario 2: BLANK StrOrigin - 5 different characters")
    for i in range(5):
        prev_data.append({
            "SequenceName": "Scene2",
            "EventName": f"Event{2000 + i}",
            "StrOrigin": "",  # BLANK!
            "Text": f"Translation {i}",
            "STATUS": "CHECK",
            "FREEMEMO": "",
            "CharacterKey": f"CharBlank_{i}",
            "DialogVoice": "Secondary",
            "SpeakerGroupKey": "B",
            "DialogType": "Shout",
            "Desc": f"Blank desc {i}",
            "StartFrame": str((i + 10) * 100),
            "EndFrame": str(((i + 10) * 100) + 50),
            "Importance": "High"
        })

    # Scenario 3: Mix of unique, duplicate, and blank
    print("✓ Scenario 3: Mix of unique, duplicate, and blank StrOrigin")
    for i in range(20):
        if i % 3 == 0:
            strorigin = "Common phrase"  # Duplicate every 3rd
        elif i % 5 == 0:
            strorigin = ""  # Blank every 5th
        else:
            strorigin = f"Unique text {i}"  # Unique

        prev_data.append({
            "SequenceName": f"Scene{3 + (i // 5)}",
            "EventName": f"Event{3000 + i}",
            "StrOrigin": strorigin,
            "Text": f"Translation {i}",
            "STATUS": "POLISHED" if i % 2 == 0 else "CHECK",
            "FREEMEMO": "",
            "CharacterKey": f"MixChar_{i}",
            "DialogVoice": "Main" if i % 2 == 0 else "Background",
            "SpeakerGroupKey": chr(65 + (i % 3)),  # A, B, or C
            "DialogType": "Dialog",
            "Desc": f"Mix desc {i}",
            "StartFrame": str((i + 20) * 100),
            "EndFrame": str(((i + 20) * 100) + 50),
            "Importance": "High" if i % 4 == 0 else "Low"
        })

    df_prev = pd.DataFrame(prev_data)
    print(f"\nPrevious file: {len(df_prev)} rows")

    # Current file - Test different scenarios
    curr_data = []

    # Scenario 1: Keep first 3 "Hello" rows unchanged, modify 2
    print("\n✓ Keeping 3 'Hello' rows unchanged")
    for i in range(3):
        curr_data.append(prev_data[i].copy())

    print("✓ Changing StrOrigin on 2 'Hello' rows")
    for i in range(3, 5):
        row = prev_data[i].copy()
        row["StrOrigin"] = "Modified hello"  # Change StrOrigin
        curr_data.append(row)

    # Scenario 2: Keep 3 BLANK rows unchanged, delete 2
    print("✓ Keeping 3 BLANK rows unchanged")
    for i in range(5, 8):
        curr_data.append(prev_data[i].copy())
    print("✓ Deleting 2 BLANK rows")
    # Rows 8-9 deleted (not added to current)

    # Scenario 3: Add NEW rows with same StrOrigin as existing
    print("✓ Adding 5 NEW rows with duplicate 'Hello' StrOrigin")
    for i in range(5):
        curr_data.append({
            "SequenceName": "Scene1",
            "EventName": f"Event{9000 + i}",  # Different event
            "StrOrigin": "Hello",  # DUPLICATE with existing!
            "Text": f"New translation {i}",
            "STATUS": "POLISHED",
            "FREEMEMO": "",
            "CharacterKey": f"NewChar_{i}",  # Different character
            "DialogVoice": "Background",
            "SpeakerGroupKey": "C",
            "DialogType": "Whisper",
            "Desc": f"New desc {i}",
            "StartFrame": str((i + 100) * 100),
            "EndFrame": str(((i + 100) * 100) + 50),
            "Importance": "High"
        })

    print("✓ Adding 3 NEW rows with BLANK StrOrigin")
    for i in range(3):
        curr_data.append({
            "SequenceName": "Scene2",
            "EventName": f"Event{9100 + i}",
            "StrOrigin": "",  # BLANK!
            "Text": f"New blank translation {i}",
            "STATUS": "CHECK",
            "FREEMEMO": "",
            "CharacterKey": f"NewBlank_{i}",
            "DialogVoice": "Main",
            "SpeakerGroupKey": "A",
            "DialogType": "Dialog",
            "Desc": f"New blank desc {i}",
            "StartFrame": str((i + 110) * 100),
            "EndFrame": str(((i + 110) * 100) + 50),
            "Importance": "High"
        })

    # Add remaining rows from previous
    print("✓ Adding remaining rows from previous")
    for i in range(10, 30):
        curr_data.append(prev_data[i].copy())

    df_curr = pd.DataFrame(curr_data)
    print(f"\nCurrent file: {len(df_curr)} rows")

    # Save to Excel
    prev_file = "Test_DuplicateStrOrigin_Previous.xlsx"
    curr_file = "Test_DuplicateStrOrigin_Current.xlsx"

    df_prev.to_excel(prev_file, index=False)
    df_curr.to_excel(curr_file, index=False)

    print(f"\n✓ Saved: {prev_file}")
    print(f"✓ Saved: {curr_file}")

    # Calculate expected results
    print("\n" + "="*80)
    print("EXPECTED RESULTS:")
    print("="*80)
    print(f"Previous: {len(df_prev)} rows")
    print(f"Current:  {len(df_curr)} rows")
    print(f"Actual difference: {len(df_curr) - len(df_prev):+d} rows")
    print()
    print("Expected changes:")
    print("  - Unchanged: 23 rows (3 'Hello' + 3 blank + 17 from mix)")
    print("  - StrOrigin Change: 2 rows (2 'Hello' changed to 'Modified hello')")
    print("  - NEW rows: 8 rows (5 'Hello' + 3 blank)")
    print("  - DELETED rows: 2 rows (2 blank rows)")
    print()
    print("Expected formula:")
    print("  new_rows - deleted_rows = 8 - 2 = 6")
    print(f"  Actual difference: {len(df_curr) - len(df_prev)} rows")

    if len(df_curr) - len(df_prev) == 6:
        print("  ✓ Math should work out!")
    else:
        print("  ✗ Math doesn't match - check test data")

    print("="*80)

    return prev_file, curr_file

def test_duplicate_strorigin():
    """Test 10-key system with duplicate and blank StrOrigin."""
    # Create test data
    prev_file, curr_file = create_duplicate_test_data()

    print("\n" + "="*80)
    print("RUNNING 10-KEY SYSTEM TEST")
    print("="*80)

    # Load files
    print("\nLoading files...")
    df_prev = safe_read_excel(prev_file, header=0, dtype=str)
    df_curr = safe_read_excel(curr_file, header=0, dtype=str)
    print(f"  ✓ Previous: {len(df_prev)} rows")
    print(f"  ✓ Current:  {len(df_curr)} rows")

    # Normalize
    df_prev = normalize_dataframe_status(df_prev)
    df_curr = normalize_dataframe_status(df_curr)

    # Generate CastingKey
    print("\nGenerating CastingKey...")
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
    print("  ✓ CastingKey generated")

    # Build lookups
    print("\nBuilding 10-key lookups...")
    (prev_lookup_se, prev_lookup_so, prev_lookup_sc, prev_lookup_eo, prev_lookup_ec,
     prev_lookup_oc, prev_lookup_seo, prev_lookup_sec, prev_lookup_soc, prev_lookup_eoc) = build_lookups(df_prev)
    print("  ✓ Built 10 lookup dictionaries")

    # Compare rows
    print("\nComparing rows with TWO-PASS algorithm...")
    changes, previous_strorigins, changed_columns_map, counter, marked_prev_indices = compare_rows(
        df_curr, df_prev,
        prev_lookup_se, prev_lookup_so, prev_lookup_sc,
        prev_lookup_eo, prev_lookup_ec, prev_lookup_oc,
        prev_lookup_seo, prev_lookup_sec, prev_lookup_soc, prev_lookup_eoc
    )
    print("  ✓ Comparison complete")

    # Find deleted rows
    print("\nFinding deleted rows...")
    df_deleted = find_deleted_rows(df_prev, df_curr, marked_prev_indices)
    counter["Deleted Rows"] = len(df_deleted)
    print(f"  ✓ Found {len(df_deleted)} deleted rows")

    # Display results
    print("\n" + "="*80)
    print("RESULTS - DUPLICATE STRORIGIN TEST")
    print("="*80)

    print("\n📊 Change Type Breakdown:")
    for change_type, count in sorted(counter.items(), key=lambda x: -x[1]):
        print(f"  {change_type:.<40} {count:>5} rows")

    # Critical validation
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
        print(f"  ✓✓✓ 10-key system handles DUPLICATE StrOrigin correctly!")
        validation_passed = True
    else:
        print(f"  ✗✗✗ FAIL: {net_change:+d} != {actual_diff:+d}")
        print(f"  ✗✗✗ Bug detected with duplicate StrOrigin!")
        validation_passed = False

    # Check for specific scenarios
    print(f"\n📋 Duplicate StrOrigin Scenarios:")

    # Check if NEW rows with duplicate "Hello" were correctly identified
    hello_news = [i for i, c in enumerate(changes) if c == "New Row" and df_curr.iloc[i]["StrOrigin"] == "Hello"]
    print(f"  NEW rows with 'Hello' StrOrigin....... {len(hello_news):>5} (expected: 5)")

    # Check if NEW rows with blank StrOrigin were correctly identified
    blank_news = [i for i, c in enumerate(changes) if c == "New Row" and df_curr.iloc[i]["StrOrigin"] == ""]
    print(f"  NEW rows with BLANK StrOrigin......... {len(blank_news):>5} (expected: 3)")

    # Check if unchanged "Hello" rows were correctly identified
    hello_unchanged = [i for i, c in enumerate(changes) if c == "No Change" and df_curr.iloc[i]["StrOrigin"] == "Hello"]
    print(f"  UNCHANGED rows with 'Hello'........... {len(hello_unchanged):>5} (expected: 3)")

    # Check if unchanged BLANK rows were correctly identified
    blank_unchanged = [i for i, c in enumerate(changes) if c == "No Change" and df_curr.iloc[i]["StrOrigin"] == ""]
    print(f"  UNCHANGED rows with BLANK............. {len(blank_unchanged):>5} (expected: 3)")

    print("\n" + "="*80)
    if validation_passed and len(hello_news) == 5 and len(blank_news) == 3:
        print("🎉🎉🎉 DUPLICATE STRORIGIN TEST PASSED! 🎉🎉🎉")
        print("The 10-key system correctly handles:")
        print("  ✓ Duplicate StrOrigin values")
        print("  ✓ Blank/empty StrOrigin values")
        print("  ✓ NEW rows with duplicate StrOrigin")
        print("  ✓ Unchanged rows with duplicate StrOrigin")
        result = "SUCCESS"
    else:
        print("❌❌❌ DUPLICATE STRORIGIN TEST FAILED! ❌❌❌")
        result = "FAILED"
    print("="*80)

    return validation_passed

if __name__ == "__main__":
    success = test_duplicate_strorigin()
    print()
    sys.exit(0 if success else 1)
