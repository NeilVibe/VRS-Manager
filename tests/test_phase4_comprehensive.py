"""
Phase 4 Comprehensive Test - Priority CHANGES, PreviousEventName, PreviousText
===============================================================================
Version: v12021XXX (Phase 4)
Created: 2025-12-02

PURPOSE:
    This test validates ALL Phase 4 features with REAL data structure:
    1. CHANGES column shows priority label (highest priority from composite)
    2. DETAILED_CHANGES column shows full composite
    3. PreviousEventName populated only when EventName changes
    4. PreviousText populated for all matched rows (not New Row)

TEST COVERAGE:
    - All 9 standalone change types
    - All composite combinations (sample of key ones)
    - Priority ranking validation (1-9)
    - New Row handling
    - No Change handling

USES PRODUCTION CODE FROM:
    - src/core/change_detection.py (get_priority_change)
    - src/core/working_comparison.py
    - src/core/comparison.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple

# Production imports
from src.config import (
    COL_DIALOGTYPE, COL_GROUP, COL_SEQUENCE, COL_CHARACTERNAME,
    COL_CHARACTERKEY, COL_DIALOGVOICE, COL_CASTINGKEY, COL_STRORIGIN,
    COL_STATUS, COL_TEXT, COL_DESC, COL_FREEMEMO,
    COL_EVENTNAME, COL_STARTFRAME, COL_ENDFRAME,
    COL_PREVIOUSDATA, COL_SPEAKER_GROUPKEY,
    COL_CHANGES, COL_DETAILED_CHANGES, COL_PREVIOUS_EVENTNAME, COL_PREVIOUS_TEXT
)
from src.core.change_detection import get_priority_change, PRIORITY_RANKING
from src.core.working_comparison import process_working_comparison
from src.core.working_helpers import build_working_lookups
from src.core.casting import generate_casting_key
from src.utils.data_processing import normalize_dataframe_status, remove_full_duplicates


# =============================================================================
# TRUE STRUCTURE DEFINITION (from VoiceRecordSheet)
# =============================================================================

TRUE_COLUMNS = [
    'DialogType', 'Group', 'SequenceName', 'CharacterName', 'CharacterKey',
    'DialogVoice', 'CastingKey', 'StrOrigin', 'STATUS', 'Text', 'Desc',
    'FREEMEMO', 'SubTimelineName', 'CHANGES', 'EventName', 'StartFrame',
    'EndFrame', 'Tribe', 'Age', 'Gender', 'Job', 'Region', 'UpdateTime',
    'PreviousData', 'Mainline Translation', 'Speaker|CharacterGroupKey'
]


def create_base_row(row_index: int, text_value: str = "") -> Dict:
    """Create a base row with TRUE structure and Korean StrOrigin."""
    return {
        'DialogType': 'Sequencer',
        'Group': 'Main',
        'SequenceName': f'cd_seq_quest_main_{row_index:04d}.seqc',
        'CharacterName': '테스트캐릭터',
        'CharacterKey': f'test_char_{row_index:04d}',
        'DialogVoice': 'Test_Voice_Male',
        'CastingKey': '',  # Will be generated
        'StrOrigin': f'안녕하세요 테스트 대사입니다 번호 {row_index}',  # Korean text
        'STATUS': 'NEW',
        'Text': text_value if text_value else f'Translation text for row {row_index}',
        'Desc': f'Description for row {row_index}',
        'FREEMEMO': '',
        'SubTimelineName': 'SCENE_1',
        'CHANGES': '',
        'EventName': f'event_test_{row_index:04d}_dialogue_{row_index:05d}',
        'StartFrame': '100',
        'EndFrame': '200',
        'Tribe': '인간',
        'Age': 'Adult',
        'Gender': '남성',
        'Job': '전사',
        'Region': '파이웰 대륙',
        'UpdateTime': datetime.now().isoformat(),
        'PreviousData': '',
        'Mainline Translation': '',
        'Speaker|CharacterGroupKey': ''
    }


# =============================================================================
# TEST 1: get_priority_change() function validation
# =============================================================================

def test_priority_change_function():
    """Test get_priority_change() returns correct priority for composites."""
    print("\n" + "=" * 70)
    print("TEST 1: get_priority_change() Function Validation")
    print("=" * 70)

    test_cases = [
        # (input, expected_output)
        ("New Row", "New Row"),
        ("No Change", "No Change"),
        ("No Relevant Change", "No Relevant Change"),

        # Standalone - should return as-is
        ("StrOrigin Change", "StrOrigin Change"),
        ("Desc Change", "Desc Change"),
        ("CastingKey Change", "CastingKey Change"),
        ("TimeFrame Change", "TimeFrame Change"),
        ("Group Change", "Group Change"),
        ("EventName Change", "EventName Change"),
        ("SequenceName Change", "SequenceName Change"),
        ("DialogType Change", "DialogType Change"),
        ("CharacterGroup Change", "CharacterGroup Change"),

        # Composites - should return highest priority
        ("EventName+StrOrigin Change", "StrOrigin Change"),  # StrOrigin (1) beats EventName (6)
        ("EventName+StrOrigin+Desc Change", "StrOrigin Change"),  # StrOrigin (1) beats all
        ("EventName+Desc Change", "Desc Change"),  # Desc (2) beats EventName (6)
        ("EventName+CastingKey Change", "CastingKey Change"),  # CastingKey (3) beats EventName (6)
        ("EventName+TimeFrame Change", "TimeFrame Change"),  # TimeFrame (4) beats EventName (6)
        ("EventName+Group Change", "Group Change"),  # Group (5) beats EventName (6)
        ("EventName+SequenceName Change", "EventName Change"),  # EventName (6) beats SequenceName (7)
        ("EventName+DialogType Change", "EventName Change"),  # EventName (6) beats DialogType (8)
        ("EventName+CharacterGroup Change", "EventName Change"),  # EventName (6) beats CharacterGroup (9)
        ("CharacterGroup+DialogType Change", "DialogType Change"),  # DialogType (8) beats CharacterGroup (9)

        # Full composite (all 9)
        ("CharacterGroup+EventName+StrOrigin+SequenceName+CastingKey+Desc+TimeFrame+DialogType+Group Change", "StrOrigin Change"),
    ]

    passed = 0
    failed = 0

    for input_label, expected in test_cases:
        result = get_priority_change(input_label)
        if result == expected:
            passed += 1
            print(f"  ✓ {input_label[:50]:<50} → {result}")
        else:
            failed += 1
            print(f"  ✗ {input_label[:50]:<50}")
            print(f"      Expected: {expected}")
            print(f"      Got:      {result}")

    print(f"\nResult: {passed}/{passed+failed} passed")
    return failed == 0


# =============================================================================
# TEST 2: Priority Ranking Validation
# =============================================================================

def test_priority_ranking():
    """Test that priority ranking is correct (1-9)."""
    print("\n" + "=" * 70)
    print("TEST 2: Priority Ranking Validation")
    print("=" * 70)

    expected_ranking = {
        "StrOrigin": 1,
        "Desc": 2,
        "CastingKey": 3,
        "TimeFrame": 4,
        "Group": 5,
        "EventName": 6,
        "SequenceName": 7,
        "DialogType": 8,
        "CharacterGroup": 9,
    }

    passed = 0
    failed = 0

    for change_type, expected_rank in expected_ranking.items():
        actual_rank = PRIORITY_RANKING.get(change_type)
        if actual_rank == expected_rank:
            passed += 1
            print(f"  ✓ {change_type:<20} = Rank {actual_rank}")
        else:
            failed += 1
            print(f"  ✗ {change_type:<20}")
            print(f"      Expected rank: {expected_rank}")
            print(f"      Actual rank:   {actual_rank}")

    print(f"\nResult: {passed}/{passed+failed} passed")
    return failed == 0


# =============================================================================
# TEST 3: Full Integration Test with WORKING Processor
# =============================================================================

def test_working_processor_phase4():
    """
    Test WORKING processor with Phase 4 columns.

    Validates:
    - CHANGES = priority label
    - DETAILED_CHANGES = full composite
    - PreviousEventName = only when EventName changes
    - PreviousText = always for matched rows
    """
    print("\n" + "=" * 70)
    print("TEST 3: WORKING Processor Phase 4 Integration")
    print("=" * 70)

    # Create test data
    prev_rows = []
    curr_rows = []
    test_expectations = []

    row_counter = 0

    # --- Case 1: No Change ---
    prev_row = create_base_row(row_counter, "Previous translation")
    prev_row['CastingKey'] = generate_casting_key(
        prev_row['CharacterKey'], prev_row['DialogVoice'], '', prev_row['DialogType']
    )
    curr_row = prev_row.copy()

    prev_rows.append(prev_row)
    curr_rows.append(curr_row)
    test_expectations.append({
        'row_idx': row_counter,
        'expected_changes': 'No Change',
        'expected_detailed': 'No Change',
        'has_prev_eventname': False,
        'has_prev_text': True,  # Matched row, not New Row
        'prev_text_value': 'Previous translation'
    })
    row_counter += 1

    # --- Case 2: Standalone EventName Change ---
    prev_row = create_base_row(row_counter, "Previous translation 2")
    prev_row['CastingKey'] = generate_casting_key(
        prev_row['CharacterKey'], prev_row['DialogVoice'], '', prev_row['DialogType']
    )
    curr_row = prev_row.copy()
    curr_row['EventName'] = 'modified_event_name_002'

    prev_rows.append(prev_row)
    curr_rows.append(curr_row)
    test_expectations.append({
        'row_idx': row_counter,
        'expected_changes': 'EventName Change',
        'expected_detailed': 'EventName Change',
        'has_prev_eventname': True,
        'prev_eventname_value': prev_row['EventName'],
        'has_prev_text': True,
        'prev_text_value': 'Previous translation 2'
    })
    row_counter += 1

    # --- Case 3: Composite EventName+StrOrigin (StrOrigin wins) ---
    prev_row = create_base_row(row_counter, "Previous translation 3")
    prev_row['CastingKey'] = generate_casting_key(
        prev_row['CharacterKey'], prev_row['DialogVoice'], '', prev_row['DialogType']
    )
    curr_row = prev_row.copy()
    curr_row['EventName'] = 'modified_event_003'
    curr_row['StrOrigin'] = '변경된 스트링 오리진 003'

    prev_rows.append(prev_row)
    curr_rows.append(curr_row)
    test_expectations.append({
        'row_idx': row_counter,
        'expected_changes': 'StrOrigin Change',  # Priority: StrOrigin (1) beats EventName (6)
        'expected_detailed': 'EventName+StrOrigin Change',
        'has_prev_eventname': True,  # EventName is in the change
        'prev_eventname_value': prev_row['EventName'],
        'has_prev_text': True,
        'prev_text_value': 'Previous translation 3'
    })
    row_counter += 1

    # --- Case 4: Composite EventName+Desc (Desc wins) ---
    prev_row = create_base_row(row_counter, "Previous translation 4")
    prev_row['CastingKey'] = generate_casting_key(
        prev_row['CharacterKey'], prev_row['DialogVoice'], '', prev_row['DialogType']
    )
    curr_row = prev_row.copy()
    curr_row['EventName'] = 'modified_event_004'
    curr_row['Desc'] = 'Modified description 004'

    prev_rows.append(prev_row)
    curr_rows.append(curr_row)
    test_expectations.append({
        'row_idx': row_counter,
        'expected_changes': 'Desc Change',  # Priority: Desc (2) beats EventName (6)
        'expected_detailed': 'EventName+Desc Change',
        'has_prev_eventname': True,
        'prev_eventname_value': prev_row['EventName'],
        'has_prev_text': True,
        'prev_text_value': 'Previous translation 4'
    })
    row_counter += 1

    # --- Case 5: New Row (no previous match) ---
    curr_row = create_base_row(row_counter, "")
    curr_row['CastingKey'] = generate_casting_key(
        curr_row['CharacterKey'], curr_row['DialogVoice'], '', curr_row['DialogType']
    )
    curr_row['EventName'] = 'brand_new_event_005'
    curr_row['StrOrigin'] = '완전히 새로운 대사 005'

    # Don't add to prev_rows - this is a NEW row
    curr_rows.append(curr_row)
    test_expectations.append({
        'row_idx': row_counter,
        'expected_changes': 'New Row',
        'expected_detailed': 'New Row',
        'has_prev_eventname': False,
        'has_prev_text': False,  # New Row has no previous
    })
    row_counter += 1

    # --- Case 6: TimeFrame only change (no EventName in label) ---
    prev_row = create_base_row(row_counter, "Previous translation 6")
    prev_row['CastingKey'] = generate_casting_key(
        prev_row['CharacterKey'], prev_row['DialogVoice'], '', prev_row['DialogType']
    )
    curr_row = prev_row.copy()
    curr_row['StartFrame'] = '999'

    prev_rows.append(prev_row)
    curr_rows.append(curr_row)
    test_expectations.append({
        'row_idx': row_counter,
        'expected_changes': 'TimeFrame Change',
        'expected_detailed': 'TimeFrame Change',
        'has_prev_eventname': False,  # No EventName in change
        'has_prev_text': True,
        'prev_text_value': 'Previous translation 6'
    })
    row_counter += 1

    # --- Case 7: Full composite (all 9 fields) - StrOrigin wins ---
    prev_row = create_base_row(row_counter, "Previous translation 7")
    prev_row['CastingKey'] = generate_casting_key(
        prev_row['CharacterKey'], prev_row['DialogVoice'], '', prev_row['DialogType']
    )
    curr_row = prev_row.copy()
    curr_row['Gender'] = '여성'  # CharacterGroup
    curr_row['EventName'] = 'modified_event_007'
    curr_row['StrOrigin'] = '변경된 스트링 007'
    curr_row['Desc'] = 'Modified desc 007'
    curr_row['StartFrame'] = '777'  # TimeFrame
    curr_row['DialogType'] = 'Cinematic'
    curr_row['Group'] = 'Side'
    # Note: SequenceName and CastingKey need to stay same for matching

    prev_rows.append(prev_row)
    curr_rows.append(curr_row)
    test_expectations.append({
        'row_idx': row_counter,
        'expected_changes': 'StrOrigin Change',  # StrOrigin (1) beats all
        'expected_detailed_contains': ['CharacterGroup', 'EventName', 'StrOrigin', 'Desc', 'TimeFrame', 'DialogType', 'Group'],
        'has_prev_eventname': True,
        'prev_eventname_value': prev_row['EventName'],
        'has_prev_text': True,
        'prev_text_value': 'Previous translation 7'
    })
    row_counter += 1

    # Create DataFrames
    df_prev = pd.DataFrame(prev_rows)
    df_curr = pd.DataFrame(curr_rows)

    # Ensure all columns exist
    for col in TRUE_COLUMNS:
        if col not in df_prev.columns:
            df_prev[col] = ''
        if col not in df_curr.columns:
            df_curr[col] = ''

    # Normalize
    df_prev = normalize_dataframe_status(df_prev)
    df_curr = normalize_dataframe_status(df_curr)
    df_prev = remove_full_duplicates(df_prev, "PREVIOUS")
    df_curr = remove_full_duplicates(df_curr, "CURRENT")

    # Generate CastingKeys
    for df in [df_prev, df_curr]:
        keys = []
        for idx, row in df.iterrows():
            keys.append(generate_casting_key(
                row.get(COL_CHARACTERKEY, ""), row.get(COL_DIALOGVOICE, ""),
                row.get(COL_SPEAKER_GROUPKEY, ""), row.get(COL_DIALOGTYPE, "")))
        df[COL_CASTINGKEY] = keys

    # Build lookups and run WORKING processor
    lookups = build_working_lookups(df_prev, "PREVIOUS")
    df_result, counter, marked, pass1_results, prev_strorigins = process_working_comparison(
        df_curr, df_prev, *lookups
    )

    # Validate results
    passed = 0
    failed = 0

    for exp in test_expectations:
        row_idx = exp['row_idx']
        if row_idx >= len(df_result):
            print(f"  ✗ Row {row_idx}: Index out of range")
            failed += 1
            continue

        row = df_result.iloc[row_idx]

        # Check CHANGES (priority)
        actual_changes = row.get(COL_CHANGES, '')
        expected_changes = exp['expected_changes']
        if actual_changes != expected_changes:
            print(f"  ✗ Row {row_idx}: CHANGES mismatch")
            print(f"      Expected: {expected_changes}")
            print(f"      Got:      {actual_changes}")
            failed += 1
            continue

        # Check DETAILED_CHANGES
        actual_detailed = row.get(COL_DETAILED_CHANGES, '')
        if 'expected_detailed' in exp:
            if actual_detailed != exp['expected_detailed']:
                print(f"  ✗ Row {row_idx}: DETAILED_CHANGES mismatch")
                print(f"      Expected: {exp['expected_detailed']}")
                print(f"      Got:      {actual_detailed}")
                failed += 1
                continue
        elif 'expected_detailed_contains' in exp:
            # Check that all expected components are in the label
            for component in exp['expected_detailed_contains']:
                if component not in actual_detailed:
                    print(f"  ✗ Row {row_idx}: DETAILED_CHANGES missing component '{component}'")
                    print(f"      Got: {actual_detailed}")
                    failed += 1
                    break
            else:
                pass  # All components found

        # Check PreviousEventName
        actual_prev_eventname = row.get(COL_PREVIOUS_EVENTNAME, '')
        if exp['has_prev_eventname']:
            if not actual_prev_eventname:
                print(f"  ✗ Row {row_idx}: PreviousEventName should be populated")
                failed += 1
                continue
            if 'prev_eventname_value' in exp and actual_prev_eventname != exp['prev_eventname_value']:
                print(f"  ✗ Row {row_idx}: PreviousEventName value mismatch")
                print(f"      Expected: {exp['prev_eventname_value']}")
                print(f"      Got:      {actual_prev_eventname}")
                failed += 1
                continue
        else:
            if actual_prev_eventname:
                print(f"  ✗ Row {row_idx}: PreviousEventName should be empty")
                print(f"      Got: {actual_prev_eventname}")
                failed += 1
                continue

        # Check PreviousText
        actual_prev_text = row.get(COL_PREVIOUS_TEXT, '')
        if exp['has_prev_text']:
            if 'prev_text_value' in exp and actual_prev_text != exp['prev_text_value']:
                print(f"  ✗ Row {row_idx}: PreviousText value mismatch")
                print(f"      Expected: {exp['prev_text_value']}")
                print(f"      Got:      {actual_prev_text}")
                failed += 1
                continue
        else:
            if actual_prev_text:
                print(f"  ✗ Row {row_idx}: PreviousText should be empty for New Row")
                failed += 1
                continue

        passed += 1
        print(f"  ✓ Row {row_idx}: {expected_changes} → DETAILED: {actual_detailed[:40]}...")

    print(f"\nResult: {passed}/{passed+failed} passed")
    return failed == 0


# =============================================================================
# TEST 4: All Standalone Change Types
# =============================================================================

def test_all_standalone_types():
    """Test all 9 standalone change types produce correct CHANGES/DETAILED_CHANGES."""
    print("\n" + "=" * 70)
    print("TEST 4: All 9 Standalone Change Types")
    print("=" * 70)

    standalone_changes = {
        'StrOrigin': lambda row: {'StrOrigin': '변경된 스트링'},
        'EventName': lambda row: {'EventName': 'modified_event'},
        'SequenceName': lambda row: {'SequenceName': 'modified_sequence.seqc'},
        'CastingKey': lambda row: {'CharacterKey': 'different_char', 'DialogVoice': 'Different_Voice'},
        'TimeFrame': lambda row: {'StartFrame': '999'},
        'Desc': lambda row: {'Desc': 'Modified description'},
        'DialogType': lambda row: {'DialogType': 'Cinematic'},
        'Group': lambda row: {'Group': 'Side'},
        'CharacterGroup': lambda row: {'Gender': '여성'},
    }

    prev_rows = []
    curr_rows = []
    expectations = []

    row_counter = 0
    for change_type, modifier in standalone_changes.items():
        prev_row = create_base_row(row_counter, f"Text {row_counter}")
        prev_row['CastingKey'] = generate_casting_key(
            prev_row['CharacterKey'], prev_row['DialogVoice'], '', prev_row['DialogType']
        )

        curr_row = prev_row.copy()
        curr_row.update(modifier(curr_row))

        if change_type == 'CastingKey':
            curr_row['CastingKey'] = generate_casting_key(
                curr_row['CharacterKey'], curr_row['DialogVoice'], '', curr_row['DialogType']
            )

        prev_rows.append(prev_row)
        curr_rows.append(curr_row)
        expectations.append({
            'row_idx': row_counter,
            'change_type': change_type,
            'expected_label': f'{change_type} Change'
        })
        row_counter += 1

    # Create DataFrames
    df_prev = pd.DataFrame(prev_rows)
    df_curr = pd.DataFrame(curr_rows)

    for col in TRUE_COLUMNS:
        if col not in df_prev.columns:
            df_prev[col] = ''
        if col not in df_curr.columns:
            df_curr[col] = ''

    df_prev = normalize_dataframe_status(df_prev)
    df_curr = normalize_dataframe_status(df_curr)

    for df in [df_prev, df_curr]:
        keys = []
        for idx, row in df.iterrows():
            keys.append(generate_casting_key(
                row.get(COL_CHARACTERKEY, ""), row.get(COL_DIALOGVOICE, ""),
                row.get(COL_SPEAKER_GROUPKEY, ""), row.get(COL_DIALOGTYPE, "")))
        df[COL_CASTINGKEY] = keys

    lookups = build_working_lookups(df_prev, "PREVIOUS")
    df_result, counter, marked, pass1_results, prev_strorigins = process_working_comparison(
        df_curr, df_prev, *lookups
    )

    passed = 0
    failed = 0

    for exp in expectations:
        row_idx = exp['row_idx']
        row = df_result.iloc[row_idx]

        actual_changes = row.get(COL_CHANGES, '')
        actual_detailed = row.get(COL_DETAILED_CHANGES, '')

        # For standalone, both should be the same
        if actual_changes == exp['expected_label'] and actual_detailed == exp['expected_label']:
            passed += 1
            print(f"  ✓ {exp['change_type']:<20} → CHANGES: {actual_changes}")
        else:
            failed += 1
            print(f"  ✗ {exp['change_type']:<20}")
            print(f"      Expected: {exp['expected_label']}")
            print(f"      CHANGES:  {actual_changes}")
            print(f"      DETAILED: {actual_detailed}")

    print(f"\nResult: {passed}/{passed+failed} passed")
    return failed == 0


# =============================================================================
# MAIN
# =============================================================================

def run_all_tests():
    """Run all Phase 4 tests."""
    print("\n" + "=" * 70)
    print("PHASE 4 COMPREHENSIVE TEST SUITE")
    print("Testing: Priority CHANGES, DETAILED_CHANGES, PreviousEventName, PreviousText")
    print("=" * 70)

    results = []

    results.append(("Priority Change Function", test_priority_change_function()))
    results.append(("Priority Ranking", test_priority_ranking()))
    results.append(("WORKING Processor Integration", test_working_processor_phase4()))
    results.append(("All Standalone Types", test_all_standalone_types()))

    # Summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    all_passed = True
    for name, passed in results:
        status = "✓" if passed else "✗"
        print(f"  {status} {name}")
        if not passed:
            all_passed = False

    print("\n" + ("ALL TESTS PASSED!" if all_passed else "SOME TESTS FAILED"))
    return all_passed


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
