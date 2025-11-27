"""
Create comprehensive 1000-row test with all edge cases.

Test cases:
1. Full duplicates (should be cleaned before processing)
2. Duplicate StrOrigin (different rows, same StrOrigin)
3. Duplicate CastingKey (different rows, same CastingKey)
4. No changes (perfect 4-key match)
5. Unique changes (one field changes)
6. Composite changes (multiple fields change)
7. New rows (all 10 keys missing)
8. Deleted rows (in PREVIOUS but not in CURRENT)
"""

import pandas as pd
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import (
    COL_SEQUENCE, COL_EVENTNAME, COL_STRORIGIN, COL_CASTINGKEY,
    COL_CHARACTERKEY, COL_DIALOGVOICE, COL_SPEAKER_GROUPKEY,
    COL_TEXT, COL_STATUS, COL_STARTFRAME, COL_ENDFRAME,
    COL_DIALOGTYPE, COL_GROUP
)
from src.core.casting import generate_casting_key


def create_row(seq_num, event_num, origin_text, char_key, dialog_voice, speaker_group, text, status="NEW", dialog_type=None, group=None):
    """Create a single row dictionary."""
    casting_key = generate_casting_key(char_key, dialog_voice, speaker_group, dialog_type or "")

    # Default DialogType and Group if not provided
    if dialog_type is None:
        # Vary dialog types for testing
        types = ["questdialog", "aidialog", "normaldialog", "cutscenedialog"]
        dialog_type = types[seq_num % len(types)]

    if group is None:
        # Vary groups for testing
        groups = ["Chapter1", "Chapter2", "Chapter3", "Faction_01", "Police", "Shop"]
        group = groups[seq_num % len(groups)]

    return {
        COL_DIALOGTYPE: dialog_type,
        COL_GROUP: group,
        COL_SEQUENCE: f"SEQ{seq_num:04d}",
        COL_EVENTNAME: f"Event{event_num:04d}",
        COL_STRORIGIN: origin_text,
        COL_CHARACTERKEY: char_key,
        COL_DIALOGVOICE: dialog_voice,
        COL_SPEAKER_GROUPKEY: speaker_group,
        COL_CASTINGKEY: casting_key,
        COL_TEXT: text,
        COL_STATUS: status,
        COL_STARTFRAME: str(seq_num * 100),
        COL_ENDFRAME: str(seq_num * 100 + 50)
    }


def create_comprehensive_test():
    """Create comprehensive test files with 1000+ rows."""

    print("Creating comprehensive test with 1000+ rows...")
    print("="*70)

    prev_rows = []
    curr_rows = []

    row_id = 1

    # ===================================================================
    # CASE 1: FULL DUPLICATES (50 rows → 25 unique after cleanup)
    # ===================================================================
    print(f"\n1. Creating FULL DUPLICATES: 50 rows (25 unique)")
    for i in range(25):
        row = create_row(
            seq_num=row_id,
            event_num=row_id,
            origin_text=f"FullDupe_{i}",
            char_key=f"CHAR_{i}",
            dialog_voice=f"VOICE_{i}",
            speaker_group=f"GROUP_{i}",
            text=f"Fully duplicated text {i}",
            status="NEW"
        )
        # Add same row TWICE to both PREVIOUS and CURRENT
        prev_rows.append(row.copy())
        prev_rows.append(row.copy())  # Duplicate
        curr_rows.append(row.copy())
        curr_rows.append(row.copy())  # Duplicate
        row_id += 1

    # ===================================================================
    # CASE 2: DUPLICATE STRORIGIN (100 rows with 10 repeated StrOrigins)
    # ===================================================================
    print(f"2. Creating DUPLICATE STRORIGIN: 100 rows (10 StrOrigins, each used 10 times)")
    for strorigin_idx in range(10):
        strorigin_text = f"RepeatedOrigin_{strorigin_idx}"
        for instance in range(10):
            prev_rows.append(create_row(
                seq_num=row_id,
                event_num=row_id,
                origin_text=strorigin_text,  # SAME StrOrigin
                char_key=f"CHAR_{row_id}",  # Different CastingKey
                dialog_voice=f"VOICE_{row_id}",
                speaker_group=f"GROUP_{row_id}",
                text=f"Previous text {row_id}",
                status="NEW"
            ))
            curr_rows.append(create_row(
                seq_num=row_id,
                event_num=row_id,
                origin_text=strorigin_text,  # SAME StrOrigin
                char_key=f"CHAR_{row_id}",  # Different CastingKey
                dialog_voice=f"VOICE_{row_id}",
                speaker_group=f"GROUP_{row_id}",
                text=f"Current text {row_id}",  # Changed text
                status="RECORDING"
            ))
            row_id += 1

    # ===================================================================
    # CASE 3: DUPLICATE CASTINGKEY (100 rows with 10 repeated CastingKeys)
    # ===================================================================
    print(f"3. Creating DUPLICATE CASTINGKEY: 100 rows (10 CastingKeys, each used 10 times)")
    for casting_idx in range(10):
        char_key = f"DUPECASTING_CHAR_{casting_idx}"
        dialog_voice = f"DUPECASTING_VOICE_{casting_idx}"
        speaker_group = f"DUPECASTING_GROUP_{casting_idx}"

        for instance in range(10):
            prev_rows.append(create_row(
                seq_num=row_id,
                event_num=row_id,
                origin_text=f"Origin_{row_id}",  # Different StrOrigin
                char_key=char_key,  # SAME CastingKey
                dialog_voice=dialog_voice,
                speaker_group=speaker_group,
                text=f"Previous text {row_id}",
                status="NEW"
            ))
            curr_rows.append(create_row(
                seq_num=row_id,
                event_num=row_id,
                origin_text=f"Origin_{row_id}",  # Different StrOrigin
                char_key=char_key,  # SAME CastingKey
                dialog_voice=dialog_voice,
                speaker_group=speaker_group,
                text=f"Current text {row_id}",
                status="RECORDING"
            ))
            row_id += 1

    # ===================================================================
    # CASE 4: NO CHANGES (perfect 4-key match) - 200 rows
    # ===================================================================
    print(f"4. Creating NO CHANGES: 200 rows (perfect 4-key match)")
    for i in range(200):
        row = create_row(
            seq_num=row_id,
            event_num=row_id,
            origin_text=f"NoChange_{row_id}",
            char_key=f"CHAR_{row_id}",
            dialog_voice=f"VOICE_{row_id}",
            speaker_group=f"GROUP_{row_id}",
            text=f"Unchanged text {row_id}",
            status="NEW"
        )
        prev_rows.append(row.copy())
        curr_rows.append(row.copy())  # Exact same row
        row_id += 1

    # ===================================================================
    # CASE 5: UNIQUE CHANGES (one field changes) - 200 rows
    # ===================================================================
    print(f"5. Creating UNIQUE CHANGES: 200 rows (50 each: StrOrigin, CastingKey, EventName, Sequence)")

    # 5a. StrOrigin Change (50 rows)
    for i in range(50):
        prev_rows.append(create_row(
            seq_num=row_id,
            event_num=row_id,
            origin_text=f"OldOrigin_{row_id}",
            char_key=f"CHAR_{row_id}",
            dialog_voice=f"VOICE_{row_id}",
            speaker_group=f"GROUP_{row_id}",
            text=f"Text {row_id}",
            status="NEW"
        ))
        curr_rows.append(create_row(
            seq_num=row_id,
            event_num=row_id,
            origin_text=f"NewOrigin_{row_id}",  # Changed StrOrigin
            char_key=f"CHAR_{row_id}",
            dialog_voice=f"VOICE_{row_id}",
            speaker_group=f"GROUP_{row_id}",
            text=f"Text {row_id}",
            status="NEW"
        ))
        row_id += 1

    # 5b. CastingKey Change (50 rows)
    for i in range(50):
        prev_rows.append(create_row(
            seq_num=row_id,
            event_num=row_id,
            origin_text=f"Origin_{row_id}",
            char_key=f"OLDCHAR_{row_id}",
            dialog_voice=f"OLDVOICE_{row_id}",
            speaker_group=f"OLDGROUP_{row_id}",
            text=f"Text {row_id}",
            status="NEW"
        ))
        curr_rows.append(create_row(
            seq_num=row_id,
            event_num=row_id,
            origin_text=f"Origin_{row_id}",
            char_key=f"NEWCHAR_{row_id}",  # Changed casting
            dialog_voice=f"NEWVOICE_{row_id}",
            speaker_group=f"NEWGROUP_{row_id}",
            text=f"Text {row_id}",
            status="NEW"
        ))
        row_id += 1

    # 5c. EventName Change (50 rows)
    for i in range(50):
        prev_rows.append(create_row(
            seq_num=row_id,
            event_num=9000 + i,  # Old event
            origin_text=f"Origin_{row_id}",
            char_key=f"CHAR_{row_id}",
            dialog_voice=f"VOICE_{row_id}",
            speaker_group=f"GROUP_{row_id}",
            text=f"Text {row_id}",
            status="NEW"
        ))
        curr_rows.append(create_row(
            seq_num=row_id,
            event_num=row_id,  # Changed EventName
            origin_text=f"Origin_{row_id}",
            char_key=f"CHAR_{row_id}",
            dialog_voice=f"VOICE_{row_id}",
            speaker_group=f"GROUP_{row_id}",
            text=f"Text {row_id}",
            status="NEW"
        ))
        row_id += 1

    # 5d. SequenceName Change (50 rows)
    for i in range(50):
        prev_rows.append(create_row(
            seq_num=8000 + i,  # Old sequence
            event_num=row_id,
            origin_text=f"Origin_{row_id}",
            char_key=f"CHAR_{row_id}",
            dialog_voice=f"VOICE_{row_id}",
            speaker_group=f"GROUP_{row_id}",
            text=f"Text {row_id}",
            status="NEW"
        ))
        curr_rows.append(create_row(
            seq_num=row_id,  # Changed SequenceName
            event_num=row_id,
            origin_text=f"Origin_{row_id}",
            char_key=f"CHAR_{row_id}",
            dialog_voice=f"VOICE_{row_id}",
            speaker_group=f"GROUP_{row_id}",
            text=f"Text {row_id}",
            status="NEW"
        ))
        row_id += 1

    # ===================================================================
    # CASE 6: COMPOSITE CHANGES (multiple fields) - 100 rows
    # ===================================================================
    print(f"6. Creating COMPOSITE CHANGES: 100 rows")

    # 6a. StrOrigin + CastingKey Change (50 rows)
    for i in range(50):
        prev_rows.append(create_row(
            seq_num=row_id,
            event_num=row_id,
            origin_text=f"OldOrigin_{row_id}",
            char_key=f"OLDCHAR_{row_id}",
            dialog_voice=f"OLDVOICE_{row_id}",
            speaker_group=f"OLDGROUP_{row_id}",
            text=f"Text {row_id}",
            status="NEW"
        ))
        curr_rows.append(create_row(
            seq_num=row_id,
            event_num=row_id,
            origin_text=f"NewOrigin_{row_id}",  # Changed
            char_key=f"NEWCHAR_{row_id}",  # Changed
            dialog_voice=f"NEWVOICE_{row_id}",
            speaker_group=f"NEWGROUP_{row_id}",
            text=f"Text {row_id}",
            status="NEW"
        ))
        row_id += 1

    # 6b. EventName + StrOrigin Change (50 rows)
    for i in range(50):
        prev_rows.append(create_row(
            seq_num=row_id,
            event_num=7000 + i,  # Old
            origin_text=f"OldOrigin_{row_id}",
            char_key=f"CHAR_{row_id}",
            dialog_voice=f"VOICE_{row_id}",
            speaker_group=f"GROUP_{row_id}",
            text=f"Text {row_id}",
            status="NEW"
        ))
        curr_rows.append(create_row(
            seq_num=row_id,
            event_num=row_id,  # Changed
            origin_text=f"NewOrigin_{row_id}",  # Changed
            char_key=f"CHAR_{row_id}",
            dialog_voice=f"VOICE_{row_id}",
            speaker_group=f"GROUP_{row_id}",
            text=f"Text {row_id}",
            status="NEW"
        ))
        row_id += 1

    # ===================================================================
    # CASE 7: NEW ROWS (all 10 keys missing in PREVIOUS) - 100 rows
    # ===================================================================
    print(f"7. Creating NEW ROWS: 100 rows (only in CURRENT)")
    for i in range(100):
        curr_rows.append(create_row(
            seq_num=row_id,
            event_num=row_id,
            origin_text=f"BrandNewOrigin_{row_id}",
            char_key=f"NEWCHAR_{row_id}",
            dialog_voice=f"NEWVOICE_{row_id}",
            speaker_group=f"NEWGROUP_{row_id}",
            text=f"New text {row_id}",
            status="NEW"
        ))
        row_id += 1

    # ===================================================================
    # CASE 8: DELETED ROWS (only in PREVIOUS) - 100 rows
    # ===================================================================
    print(f"8. Creating DELETED ROWS: 100 rows (only in PREVIOUS)")
    for i in range(100):
        prev_rows.append(create_row(
            seq_num=row_id,
            event_num=row_id,
            origin_text=f"DeletedOrigin_{row_id}",
            char_key=f"DELETEDCHAR_{row_id}",
            dialog_voice=f"DELETEDVOICE_{row_id}",
            speaker_group=f"DELETEDGROUP_{row_id}",
            text=f"Deleted text {row_id}",
            status="NEW"
        ))
        row_id += 1

    # ===================================================================
    # Create DataFrames
    # ===================================================================
    df_prev = pd.DataFrame(prev_rows)
    df_curr = pd.DataFrame(curr_rows)

    print("\n" + "="*70)
    print(f"SUMMARY:")
    print(f"  PREVIOUS: {len(df_prev):,} rows (before duplicate cleanup)")
    print(f"  CURRENT:  {len(df_curr):,} rows (before duplicate cleanup)")
    print(f"\nExpected after cleanup:")
    print(f"  PREVIOUS: ~{len(df_prev) - 25:,} rows (50 full dupes → 25 unique)")
    print(f"  CURRENT:  ~{len(df_curr) - 25:,} rows (50 full dupes → 25 unique)")
    print("="*70)

    # Save files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    prev_path = os.path.join(script_dir, "test_comprehensive_PREVIOUS.xlsx")
    curr_path = os.path.join(script_dir, "test_comprehensive_CURRENT.xlsx")

    df_prev.to_excel(prev_path, index=False, engine='openpyxl')
    df_curr.to_excel(curr_path, index=False, engine='openpyxl')

    print(f"\n✓ Created: {prev_path}")
    print(f"✓ Created: {curr_path}")

    print("\nTest cases breakdown:")
    print(f"  1. Full duplicates: 50 rows (25 unique)")
    print(f"  2. Duplicate StrOrigin: 100 rows")
    print(f"  3. Duplicate CastingKey: 100 rows")
    print(f"  4. No changes: 200 rows")
    print(f"  5. Unique changes: 200 rows")
    print(f"  6. Composite changes: 100 rows")
    print(f"  7. New rows: 100 rows")
    print(f"  8. Deleted rows: 100 rows")
    print(f"  TOTAL: {len(df_prev):,} PREVIOUS, {len(df_curr):,} CURRENT")


if __name__ == "__main__":
    create_comprehensive_test()
