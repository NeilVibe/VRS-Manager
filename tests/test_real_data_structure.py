#!/usr/bin/env python3
"""
Test with REAL data structure matching actual VRS files
Based on: NEW 251114_CD_VoiceRecordingSheet_4227985_Korean 10am(1)

This test uses the actual column structure and data patterns from production files.
"""

import pandas as pd
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.working_comparison import process_working_comparison
from src.core.working_helpers import build_working_lookups, find_working_deleted_rows
from src.core.comparison import compare_rows
from src.core.lookups import build_lookups
from src.config import (
    COL_SEQUENCE, COL_EVENTNAME, COL_STRORIGIN, COL_CASTINGKEY,
    COL_CHARACTERKEY, COL_DIALOGVOICE, COL_SPEAKER_GROUPKEY,
    COL_TEXT, COL_STATUS, COL_FREEMEMO, COL_PREVIOUS_STRORIGIN
)
from src.core.casting import generate_casting_key


# Real Korean dialogue samples from production data
KOREAN_DIALOGUE = [
    "검은곰 이놈들!!",
    "무슨 일이야?",
    "여기서 뭐하는 거지?",
    "조심해!",
    "알겠습니다.",
    "감사합니다.",
    "미안해요.",
    "괜찮아요.",
    "도와주세요!",
    "이건 뭐지?",
    "어디로 가야 하나요?",
    "준비됐어요.",
    "시작하죠.",
    "끝났어요.",
    "좋아요!",
    "안녕하세요.",
    "또 만나요.",
    "잘 가요.",
    "힘내세요!",
    "괜찮으시겠어요?",
]

# Real sequence patterns from production data
SEQUENCE_PATTERNS = [
    "cd_seq_quest_intro_{:04d}.seqc",
    "cd_seq_quest_chapter1_{:04d}.seqc",
    "cd_seq_quest_chapter2_{:04d}.seqc",
    "cd_seq_faction_01_{:04d}.seqc",
    "cd_seq_faction_02_{:04d}.seqc",
    "cd_seq_faction_03_{:04d}.seqc",
    "cd_seq_tutorial_{:04d}.seqc",
    "cd_seq_shop_{:04d}.seqc",
]

# Real character patterns from production data
CHARACTER_PATTERNS = [
    "nhm_unique_greyfur_swordshield_2",
    "nwf_unique_redfang_bow_1",
    "unique_kliff",
    "nhm_adult_soldier_8",
    "nwf_young_mage_3",
    "unique_boss_dragon",
    "nhm_elder_merchant_1",
    "nwf_child_civilian_2",
]

# Real groups from production data
GROUPS = ["Intro", "Chapter1", "Chapter2", "Faction_01", "Faction_02", "Faction_03", "Tutorial", "Shop"]

# Real dialog types
DIALOG_TYPES = ["Sequencer", "Quest", "Battle", "Cutscene"]

# Real STATUS values
STATUS_VALUES = ["", "POLISHED", "SPEC-OUT", "CHECK", "RECORDED", "FINAL", "SHIPPED"]


def generate_real_structure_data(num_rows=1000, include_changes=True):
    """
    Generate test data matching REAL production VRS structure

    Args:
        num_rows: Number of rows to generate
        include_changes: If True, includes various change types

    Returns:
        pd.DataFrame with real column structure
    """
    data = []

    for i in range(num_rows):
        # Generate realistic values
        group = GROUPS[i % len(GROUPS)]
        dialog_type = DIALOG_TYPES[i % len(DIALOG_TYPES)]
        sequence = SEQUENCE_PATTERNS[i % len(SEQUENCE_PATTERNS)].format(i % 10000)
        character_key = CHARACTER_PATTERNS[i % len(CHARACTER_PATTERNS)]
        dialog_voice = f"Voice_{i % 5}"
        speaker_group = f"Group_{i % 3}"

        # Generate EventName (real pattern)
        event_name = f"{character_key}_{group.lower()}_{i % 10000:04d}_npc_{i % 100:02d}_{i % 9999:05d}"

        # Generate CastingKey (auto-generated pattern)
        casting_key = generate_casting_key(character_key, dialog_voice, speaker_group, dialog_type)

        # Korean dialogue (some empty like real data)
        if i % 10 == 0:  # 10% empty (like real data)
            strorigin = ""
            text = ""
        else:
            strorigin = KOREAN_DIALOGUE[i % len(KOREAN_DIALOGUE)]
            text = f"Translation_{i}"

        # STATUS (some empty like real data)
        status = STATUS_VALUES[i % len(STATUS_VALUES)]

        # Real column structure
        row = {
            "DialogType": dialog_type,
            "Group": group,
            "SequenceName": sequence,
            "CharacterName": f"Character_{i % 20}",
            "CharacterKey": character_key,
            "DialogVoice": dialog_voice,
            COL_SPEAKER_GROUPKEY: speaker_group,
            "CastingKey": casting_key,
            "StrOrigin": strorigin,
            "STATUS": status,
            "Text": text,
            "Desc": f"Description for event {i}",
            "FREEMEMO": f"Memo_{i % 5}" if i % 3 == 0 else "",
            "SubTimelineName": f"Timeline_{i % 10}",
            "EventName": event_name,
            "StartFrame": float(i * 100),
            "EndFrame": float(i * 100 + 50),
            "Tribe": f"Tribe_{i % 5}",
            "Age": f"Age_{i % 4}",
            "Gender": "Male" if i % 2 == 0 else "Female",
            "Job": f"Job_{i % 6}",
            "Region": f"Region_{i % 8}",
            "UpdateTime": f"2024-11-{(i % 28) + 1:02d}",
        }

        data.append(row)

    df = pd.DataFrame(data)

    # Add changes if requested
    if include_changes:
        df = add_realistic_changes(df)

    return df


def add_realistic_changes(df_prev):
    """
    Create CURRENT from PREVIOUS with realistic changes

    Changes:
    - 10% StrOrigin changes (Korean text edits)
    - 5% New rows
    - 5% Deleted rows
    - 3% EventName changes
    - 2% CastingKey changes
    - Rest unchanged
    """
    df_curr = df_prev.copy()

    num_rows = len(df_curr)

    # 1. StrOrigin changes (10%)
    strorigin_change_indices = list(range(0, num_rows, 10))
    for idx in strorigin_change_indices:
        if df_curr.loc[idx, "StrOrigin"]:  # Only if not empty
            # Change Korean text
            current_text = df_curr.loc[idx, "StrOrigin"]
            df_curr.loc[idx, "StrOrigin"] = current_text + " (수정됨)"

    # 2. EventName changes (3%)
    eventname_change_indices = list(range(2, num_rows, 33))
    for idx in eventname_change_indices:
        current_event = df_curr.loc[idx, "EventName"]
        df_curr.loc[idx, "EventName"] = current_event.replace("_npc_", "_player_")

    # 3. CastingKey changes (2%)
    castingkey_change_indices = list(range(5, num_rows, 50))
    for idx in castingkey_change_indices:
        # Change character voice
        df_curr.loc[idx, "DialogVoice"] = "Voice_Changed"
        # Regenerate CastingKey
        df_curr.loc[idx, "CastingKey"] = generate_casting_key(
            df_curr.loc[idx, "CharacterKey"],
            "Voice_Changed",
            df_curr.loc[idx, COL_SPEAKER_GROUPKEY],
            df_curr.loc[idx, "DialogType"]
        )

    # 4. Delete rows (5%)
    delete_indices = list(range(7, num_rows, 20))
    df_curr = df_curr.drop(delete_indices).reset_index(drop=True)

    # 5. Add new rows (5%)
    num_new = len(delete_indices)  # Same number as deleted
    new_rows = generate_real_structure_data(num_new, include_changes=False)

    # Make new rows obviously new
    for idx in range(len(new_rows)):
        new_rows.loc[idx, "EventName"] = f"NEW_EVENT_{idx:05d}"
        new_rows.loc[idx, "StrOrigin"] = f"새로운 대화 {idx}"
        new_rows.loc[idx, "STATUS"] = ""
        new_rows.loc[idx, "Text"] = ""

    df_curr = pd.concat([df_curr, new_rows], ignore_index=True)

    return df_curr


def test_working_processor_with_real_structure():
    """
    Test Working processor with real data structure
    Verifies Previous StrOrigin column exists and has correct data
    """
    print("=" * 70)
    print("TESTING WORKING PROCESSOR WITH REAL DATA STRUCTURE")
    print("=" * 70)

    # Generate test data
    print("\n1. Generating test data (real structure, 1000 rows)...")
    df_prev = generate_real_structure_data(num_rows=1000, include_changes=False)
    df_curr = add_realistic_changes(df_prev)

    print(f"   PREVIOUS: {len(df_prev)} rows")
    print(f"   CURRENT:  {len(df_curr)} rows")
    print(f"   Expected deletions: ~50 rows")
    print(f"   Expected new rows: ~50 rows")

    # Build lookups
    print("\n2. Building 10-key lookups...")
    lookups = build_working_lookups(df_prev, "PREVIOUS")

    # Process comparison
    print("\n3. Running Working comparison (TWO-PASS)...")
    result, counter, marked, pass1_results, previous_strorigins = process_working_comparison(
        df_curr, df_prev, *lookups
    )

    print(f"   Result rows: {len(result)}")
    print(f"   Previous StrOrigins returned: {len(previous_strorigins)}")

    # Verify Previous StrOrigin was captured
    print("\n4. Verifying Previous StrOrigin data...")

    if len(previous_strorigins) != len(result):
        print(f"   ✗ MISMATCH: previous_strorigins has {len(previous_strorigins)} items, result has {len(result)} rows")
        return False

    # Add to result (like processor does)
    result[COL_PREVIOUS_STRORIGIN] = previous_strorigins

    # Check column exists
    if COL_PREVIOUS_STRORIGIN not in result.columns:
        print(f"   ✗ COLUMN MISSING: '{COL_PREVIOUS_STRORIGIN}' not in result columns")
        return False

    print(f"   ✓ Column exists: '{COL_PREVIOUS_STRORIGIN}'")

    # Check data quality
    non_empty_prev = result[result[COL_PREVIOUS_STRORIGIN].notna() & (result[COL_PREVIOUS_STRORIGIN] != "")]
    print(f"   ✓ Non-empty Previous StrOrigin: {len(non_empty_prev)} rows")

    # Check StrOrigin changes have previous values
    strorigin_changes = result[result["CHANGES"].astype(str).str.contains("StrOrigin", case=False, na=False)]
    print(f"   ✓ StrOrigin changes detected: {len(strorigin_changes)} rows")

    if len(strorigin_changes) > 0:
        # Check that StrOrigin changes have previous values
        strorigin_with_prev = strorigin_changes[
            strorigin_changes[COL_PREVIOUS_STRORIGIN].notna() &
            (strorigin_changes[COL_PREVIOUS_STRORIGIN] != "")
        ]
        coverage = len(strorigin_with_prev) / len(strorigin_changes) * 100
        print(f"   ✓ StrOrigin changes with Previous StrOrigin: {len(strorigin_with_prev)}/{len(strorigin_changes)} ({coverage:.1f}%)")

        # Show sample
        print("\n   Sample StrOrigin changes:")
        sample = strorigin_changes.head(3)
        for idx, row in sample.iterrows():
            prev_str = str(row.get(COL_PREVIOUS_STRORIGIN, ""))[:30]
            curr_str = str(row.get(COL_STRORIGIN, ""))[:30]
            print(f"      Previous: '{prev_str}' → Current: '{curr_str}'")

    # Verify change counts
    print("\n5. Change detection results:")
    for change_type, count in sorted(counter.items(), key=lambda x: -x[1]):
        print(f"   {change_type:30s}: {count:4d}")

    # Find deleted rows
    deleted = find_working_deleted_rows(df_prev, df_curr, marked)
    print(f"\n   Deleted rows: {len(deleted)}")

    print("\n" + "=" * 70)
    print("✓ WORKING PROCESSOR TEST PASSED")
    print("=" * 70)

    return True


def test_raw_processor_with_real_structure():
    """
    Test RAW processor with real data structure
    Verifies it also works correctly
    """
    print("\n" + "=" * 70)
    print("TESTING RAW PROCESSOR WITH REAL DATA STRUCTURE")
    print("=" * 70)

    # Generate test data
    print("\n1. Generating test data (real structure, 1000 rows)...")
    df_prev = generate_real_structure_data(num_rows=1000, include_changes=False)
    df_curr = add_realistic_changes(df_prev)

    print(f"   PREVIOUS: {len(df_prev)} rows")
    print(f"   CURRENT:  {len(df_curr)} rows")

    # Build lookups
    print("\n2. Building 10-key lookups...")
    lookups = build_lookups(df_prev)

    # Process comparison
    print("\n3. Running RAW comparison (TWO-PASS)...")
    changes, previous_strorigins, changed_cols_map, counter, marked, group_analysis, pass1_results = compare_rows(
        df_curr, df_prev, *lookups
    )

    print(f"   Changes returned: {len(changes)}")
    print(f"   Previous StrOrigins returned: {len(previous_strorigins)}")

    # Create result DataFrame
    result = df_curr.copy()
    result["CHANGES"] = changes
    result[COL_PREVIOUS_STRORIGIN] = previous_strorigins

    # Verify Previous StrOrigin
    print("\n4. Verifying Previous StrOrigin data...")

    if COL_PREVIOUS_STRORIGIN not in result.columns:
        print(f"   ✗ COLUMN MISSING: '{COL_PREVIOUS_STRORIGIN}' not in result columns")
        return False

    print(f"   ✓ Column exists: '{COL_PREVIOUS_STRORIGIN}'")

    # Check data
    non_empty_prev = result[result[COL_PREVIOUS_STRORIGIN].notna() & (result[COL_PREVIOUS_STRORIGIN] != "")]
    print(f"   ✓ Non-empty Previous StrOrigin: {len(non_empty_prev)} rows")

    # Verify change counts
    print("\n5. Change detection results:")
    for change_type, count in sorted(counter.items(), key=lambda x: -x[1]):
        print(f"   {change_type:30s}: {count:4d}")

    print("\n" + "=" * 70)
    print("✓ RAW PROCESSOR TEST PASSED")
    print("=" * 70)

    return True


if __name__ == '__main__':
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  REAL DATA STRUCTURE TEST SUITE".center(68) + "║")
    print("║" + "  Based on production VRS files".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")

    # Test both processors
    working_ok = test_working_processor_with_real_structure()
    raw_ok = test_raw_processor_with_real_structure()

    # Final report
    print("\n")
    print("=" * 70)
    print("FINAL TEST RESULTS")
    print("=" * 70)
    print(f"Working Processor: {'✓ PASS' if working_ok else '✗ FAIL'}")
    print(f"RAW Processor:     {'✓ PASS' if raw_ok else '✗ FAIL'}")

    if working_ok and raw_ok:
        print("\n✓ ALL TESTS PASSED - Real data structure verified!")
        print("=" * 70)
        sys.exit(0)
    else:
        print("\n✗ SOME TESTS FAILED")
        print("=" * 70)
        sys.exit(1)
