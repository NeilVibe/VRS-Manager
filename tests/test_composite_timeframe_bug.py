"""
Test for composite change detection bug: TimeFrame missing in composites.

BUG REPORT: When EventName, TimeFrame, and StrOrigin all change,
the output only shows "EventName+StrOrigin Change" - MISSING TimeFrame!

Expected: "EventName+StrOrigin+TimeFrame Change"
Actual:   "EventName+StrOrigin Change"

This test reproduces and verifies the bug.
"""

import pandas as pd
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.comparison import compare_rows
from src.core.working_comparison import process_working_comparison
from src.core.lookups import build_lookups
from src.core.working_helpers import build_working_lookups
from src.config import (
    COL_SEQUENCE, COL_EVENTNAME, COL_STRORIGIN, COL_CASTINGKEY,
    COL_STARTFRAME, COL_ENDFRAME, COL_DESC, COL_DIALOGTYPE, COL_GROUP
)


def create_test_data_for_composite_bug():
    """
    Create test data where:
    - Sequence and CastingKey stay the SAME
    - EventName, StrOrigin, and TimeFrame ALL change

    This triggers the SC (Sequence + CastingKey) 2-key match which
    should detect all three changes but currently only detects EventName+StrOrigin.
    """
    # Base row structure
    base_cols = {
        "SequenceName": "Seq1",
        "EventName": "Event_Original_001",
        "StrOrigin": "안녕하세요",  # Korean text
        "CharacterKey": "Char1",
        "DialogVoice": "Voice1",
        "Speaker|CharacterGroupKey": "GroupKey1",
        "DialogType": "Dialogue",
        "CastingKey": "Char1_Voice1_GroupKey1_Dialogue",
        "Text": "Hello",
        "STATUS": "POLISHED",
        "FREEMEMO": "Test memo",
        "Desc": "Original description",
        "StartFrame": "100",
        "EndFrame": "200",
        "Group": "Chapter1",
        "Tribe": "Human",
        "Age": "Adult",
        "Gender": "Male",
        "Job": "Warrior",
        "Region": "West"
    }

    # PREVIOUS data (single row)
    prev_data = [base_cols.copy()]

    # CURRENT data - change EventName, StrOrigin, AND TimeFrame
    curr_row = base_cols.copy()
    curr_row["EventName"] = "Event_Changed_001"        # Changed!
    curr_row["StrOrigin"] = "안녕하세요 수정됨"          # Changed!
    curr_row["StartFrame"] = "150"                     # Changed!
    curr_row["EndFrame"] = "250"                       # Changed!
    # NOTE: Sequence and CastingKey stay the SAME

    curr_data = [curr_row]

    return pd.DataFrame(prev_data), pd.DataFrame(curr_data)


def create_extended_test_data():
    """
    Extended test cases covering multiple composite scenarios.
    """
    base_cols = {
        "SequenceName": "Seq1",
        "EventName": "Event1",
        "StrOrigin": "안녕하세요",
        "CharacterKey": "Char1",
        "DialogVoice": "Voice1",
        "Speaker|CharacterGroupKey": "GroupKey1",
        "DialogType": "Dialogue",
        "CastingKey": "Char1_Voice1_GroupKey1_Dialogue",
        "Text": "Hello",
        "STATUS": "POLISHED",
        "FREEMEMO": "Memo",
        "Desc": "Desc",
        "StartFrame": "100",
        "EndFrame": "200",
        "Group": "Chapter1",
        "Tribe": "Human",
        "Age": "Adult",
        "Gender": "Male",
        "Job": "Warrior",
        "Region": "West"
    }

    prev_data = []
    curr_data = []

    # Test Case 1: EventName + StrOrigin + TimeFrame change (SC match)
    row1_prev = base_cols.copy()
    row1_prev["SequenceName"] = "TestSeq1"
    row1_prev["EventName"] = "Event_TC1_Original"
    prev_data.append(row1_prev)

    row1_curr = row1_prev.copy()
    row1_curr["EventName"] = "Event_TC1_Changed"       # Changed
    row1_curr["StrOrigin"] = "변경된 텍스트 1"          # Changed
    row1_curr["StartFrame"] = "150"                    # Changed
    curr_data.append(row1_curr)

    # Test Case 2: StrOrigin + TimeFrame + Desc change (SEC match - Seq+Event+CastingKey same)
    row2_prev = base_cols.copy()
    row2_prev["SequenceName"] = "TestSeq2"
    row2_prev["EventName"] = "Event_TC2"
    prev_data.append(row2_prev)

    row2_curr = row2_prev.copy()
    row2_curr["StrOrigin"] = "변경된 텍스트 2"          # Changed
    row2_curr["StartFrame"] = "200"                    # Changed
    row2_curr["Desc"] = "Modified Desc"                # Changed
    curr_data.append(row2_curr)

    # Test Case 3: EventName + TimeFrame (no StrOrigin change) - SOC match
    row3_prev = base_cols.copy()
    row3_prev["SequenceName"] = "TestSeq3"
    row3_prev["EventName"] = "Event_TC3_Original"
    prev_data.append(row3_prev)

    row3_curr = row3_prev.copy()
    row3_curr["EventName"] = "Event_TC3_Changed"       # Changed
    row3_curr["StartFrame"] = "300"                    # Changed
    # StrOrigin NOT changed
    curr_data.append(row3_curr)

    # Test Case 4: Control - No Change (perfect match)
    row4_prev = base_cols.copy()
    row4_prev["SequenceName"] = "TestSeq4"
    row4_prev["EventName"] = "Event_TC4"
    prev_data.append(row4_prev)

    row4_curr = row4_prev.copy()  # Exact copy
    curr_data.append(row4_curr)

    # Test Case 5: Only TimeFrame change (standalone)
    row5_prev = base_cols.copy()
    row5_prev["SequenceName"] = "TestSeq5"
    row5_prev["EventName"] = "Event_TC5"
    prev_data.append(row5_prev)

    row5_curr = row5_prev.copy()
    row5_curr["StartFrame"] = "500"                    # Only TimeFrame changed
    curr_data.append(row5_curr)

    return pd.DataFrame(prev_data), pd.DataFrame(curr_data)


def test_raw_composite_timeframe():
    """Test RAW processor for composite TimeFrame detection."""
    print("\n" + "=" * 70)
    print("TEST: RAW PROCESSOR - Composite TimeFrame Detection")
    print("=" * 70)

    df_prev, df_curr = create_test_data_for_composite_bug()

    print(f"\nPREVIOUS data:")
    print(f"  EventName:  {df_prev.iloc[0]['EventName']}")
    print(f"  StrOrigin:  {df_prev.iloc[0]['StrOrigin']}")
    print(f"  StartFrame: {df_prev.iloc[0]['StartFrame']}")
    print(f"  CastingKey: {df_prev.iloc[0]['CastingKey']}")

    print(f"\nCURRENT data:")
    print(f"  EventName:  {df_curr.iloc[0]['EventName']}")
    print(f"  StrOrigin:  {df_curr.iloc[0]['StrOrigin']}")
    print(f"  StartFrame: {df_curr.iloc[0]['StartFrame']}")
    print(f"  CastingKey: {df_curr.iloc[0]['CastingKey']}")

    # Build lookups and run comparison
    lookups = build_lookups(df_prev)
    changes, prev_strorigins, changed_cols_map, counter, marked, group_analysis, pass1_results = compare_rows(
        df_curr, df_prev, *lookups
    )

    detected_change = changes[0] if changes else "NOTHING"

    print(f"\nDETECTED CHANGE: {detected_change}")

    # Check expectations
    expected_parts = ["EventName", "StrOrigin", "TimeFrame"]
    missing_parts = [part for part in expected_parts if part not in detected_change]

    if missing_parts:
        print(f"\n❌ MISSING PARTS: {missing_parts}")
        print(f"   Expected: 'EventName+StrOrigin+TimeFrame Change' (or similar composite)")
        print(f"   Actual:   '{detected_change}'")
        return False, detected_change
    else:
        print(f"\n✓ ALL PARTS DETECTED: {expected_parts}")
        return True, detected_change


def test_working_composite_timeframe():
    """Test WORKING processor for composite TimeFrame detection."""
    print("\n" + "=" * 70)
    print("TEST: WORKING PROCESSOR - Composite TimeFrame Detection")
    print("=" * 70)

    df_prev, df_curr = create_test_data_for_composite_bug()

    print(f"\nPREVIOUS data:")
    print(f"  EventName:  {df_prev.iloc[0]['EventName']}")
    print(f"  StrOrigin:  {df_prev.iloc[0]['StrOrigin']}")
    print(f"  StartFrame: {df_prev.iloc[0]['StartFrame']}")
    print(f"  CastingKey: {df_prev.iloc[0]['CastingKey']}")

    print(f"\nCURRENT data:")
    print(f"  EventName:  {df_curr.iloc[0]['EventName']}")
    print(f"  StrOrigin:  {df_curr.iloc[0]['StrOrigin']}")
    print(f"  StartFrame: {df_curr.iloc[0]['StartFrame']}")
    print(f"  CastingKey: {df_curr.iloc[0]['CastingKey']}")

    # Build lookups and run comparison
    lookups = build_working_lookups(df_prev, "PREVIOUS")
    result, counter, marked, pass1_results, prev_strorigins = process_working_comparison(
        df_curr, df_prev, *lookups
    )

    detected_change = result.iloc[0]["CHANGES"] if len(result) > 0 else "NOTHING"

    print(f"\nDETECTED CHANGE: {detected_change}")

    # Check expectations
    expected_parts = ["EventName", "StrOrigin", "TimeFrame"]
    missing_parts = [part for part in expected_parts if part not in detected_change]

    if missing_parts:
        print(f"\n❌ MISSING PARTS: {missing_parts}")
        print(f"   Expected: 'EventName+StrOrigin+TimeFrame Change' (or similar composite)")
        print(f"   Actual:   '{detected_change}'")
        return False, detected_change
    else:
        print(f"\n✓ ALL PARTS DETECTED: {expected_parts}")
        return True, detected_change


def test_extended_scenarios():
    """Test multiple composite scenarios."""
    print("\n" + "=" * 70)
    print("TEST: EXTENDED COMPOSITE SCENARIOS")
    print("=" * 70)

    df_prev, df_curr = create_extended_test_data()

    # Expected results per test case
    expected = {
        "TestSeq1": ["EventName", "StrOrigin", "TimeFrame"],  # SC match - all 3 should be detected
        "TestSeq2": ["StrOrigin", "TimeFrame", "Desc"],        # SEC match - StrOrigin+TimeFrame+Desc
        "TestSeq3": ["EventName"],                             # SOC match - EventName only (TimeFrame not checked!)
        "TestSeq4": [],                                        # No Change
        "TestSeq5": ["TimeFrame"],                             # Perfect match with TimeFrame only
    }

    errors = []

    # Test RAW processor
    print("\n--- RAW PROCESSOR ---")
    lookups = build_lookups(df_prev)
    changes, _, _, counter, _, _, _ = compare_rows(df_curr, df_prev, *lookups)

    for i, (idx, row) in enumerate(df_curr.iterrows()):
        seq = row["SequenceName"]
        detected = changes[i]
        exp_parts = expected.get(seq, [])

        if not exp_parts:  # No Change expected
            if detected != "No Change":
                errors.append(f"RAW {seq}: Expected 'No Change', got '{detected}'")
            else:
                print(f"  ✓ {seq}: {detected}")
        else:
            missing = [part for part in exp_parts if part not in detected]
            if missing:
                errors.append(f"RAW {seq}: Missing {missing} in '{detected}'")
                print(f"  ❌ {seq}: {detected} (missing: {missing})")
            else:
                print(f"  ✓ {seq}: {detected}")

    # Test WORKING processor
    print("\n--- WORKING PROCESSOR ---")
    lookups_w = build_working_lookups(df_prev, "PREVIOUS")
    result_w, counter_w, _, _, _ = process_working_comparison(df_curr, df_prev, *lookups_w)

    for idx, row in result_w.iterrows():
        seq = row["SequenceName"]
        detected = row["CHANGES"]
        exp_parts = expected.get(seq, [])

        if not exp_parts:  # No Change expected
            if detected != "No Change":
                errors.append(f"WORKING {seq}: Expected 'No Change', got '{detected}'")
            else:
                print(f"  ✓ {seq}: {detected}")
        else:
            missing = [part for part in exp_parts if part not in detected]
            if missing:
                errors.append(f"WORKING {seq}: Missing {missing} in '{detected}'")
                print(f"  ❌ {seq}: {detected} (missing: {missing})")
            else:
                print(f"  ✓ {seq}: {detected}")

    return errors


def main():
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  COMPOSITE TIMEFRAME BUG TEST".center(68) + "║")
    print("║" + "  Bug: TimeFrame missing in composite changes".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")

    all_errors = []

    # Test 1: RAW processor - specific bug case
    raw_ok, raw_result = test_raw_composite_timeframe()
    if not raw_ok:
        all_errors.append(f"RAW: {raw_result}")

    # Test 2: WORKING processor - specific bug case
    working_ok, working_result = test_working_composite_timeframe()
    if not working_ok:
        all_errors.append(f"WORKING: {working_result}")

    # Test 3: Extended scenarios
    extended_errors = test_extended_scenarios()
    all_errors.extend(extended_errors)

    # Final report
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)

    if not all_errors:
        print("✓ ALL TESTS PASSED")
        print("✓ TimeFrame properly detected in composite changes")
        return 0
    else:
        print(f"❌ {len(all_errors)} TESTS FAILED")
        print("\nAll failures:")
        for error in all_errors:
            print(f"  • {error}")

        print("\n" + "-" * 70)
        print("BUG LOCATION: src/core/working_comparison.py")
        print("-" * 70)
        print("Line 356-363 (SC match): Hardcoded 'EventName+StrOrigin Change'")
        print("Line 260-272 (SOC match): No TimeFrame check for EventName changes")
        print("-" * 70)
        print("FIX NEEDED: Add field-level difference checking for TimeFrame")
        print("            Similar to how SEC match (lines 225-258) does it.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
