"""
Generate comprehensive 5000-row test files with edge cases.

This script creates PREVIOUS and CURRENT Excel files with:
- 5000 rows each
- Multiple edge cases (duplicates, empty StrOrigin, migrations, etc.)
- All types of changes (StrOrigin, CastingKey, SequenceName, EventName, etc.)
- Composite changes (multiple columns changing)
- Group migrations (Chapter3 → Chapter6, etc.)
- Super group data (Quest Dialog, AI Dialog)
"""

import pandas as pd
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import COL_STRORIGIN, COL_EVENTNAME, COL_CASTINGKEY, COL_CHARACTERKEY, COL_DIALOGVOICE, COL_SPEAKER_GROUPKEY, COL_SEQUENCE, COL_GROUP, COL_TEXT


def generate_test_files():
    """Generate 5000-row PREVIOUS and CURRENT test files."""

    script_dir = os.path.dirname(os.path.abspath(__file__))
    prev_path = os.path.join(script_dir, "test_5000row_PREVIOUS.xlsx")
    curr_path = os.path.join(script_dir, "test_5000row_CURRENT.xlsx")

    # Define groups and super groups
    groups = [
        "Intro", "Prolog",
        "Chapter1", "Chapter2", "Chapter3", "Chapter4", "Chapter5", "Chapter6",
        "Final Chapter",
        "faction_01", "faction_02", "faction_03", "faction_etc"
    ]

    rows_prev = []
    rows_curr = []

    # Track expected counts
    expected = {
        "No Change": 0,
        "StrOrigin Change": 0,
        "CastingKey Change": 0,
        "SequenceName Change": 0,
        "EventName Change": 0,
        "StrOrigin+CastingKey Change": 0,
        "StrOrigin+SequenceName Change": 0,
        "EventName+StrOrigin Change": 0,
        "No Relevant Change": 0,
        "New Row": 0,
        "Deleted Rows": 0,
        "Full Duplicates Removed": 0
    }

    row_id = 1

    # ===================================================================
    # SECTION 1: No Change rows (1000 rows)
    # ===================================================================
    for i in range(1000):
        group = groups[i % len(groups)]

        # Add Quest Dialog and AI Dialog via SequenceName
        if i % 50 == 0:
            sequence_name = f"questdialog_scene_{i}"
        elif i % 51 == 0:
            sequence_name = f"aidialog_conversation_{i}"
        else:
            sequence_name = f"scene_{i}"

        row = {
            COL_STRORIGIN: f"This is dialogue line {row_id} with no changes",
            COL_EVENTNAME: f"Event_{i}",
            COL_SEQUENCE: sequence_name,
            COL_CHARACTERKEY: f"Char_{i % 20}",
            COL_DIALOGVOICE: f"Voice_{i % 10}",
            COL_SPEAKER_GROUPKEY: f"SpeakerGroup_{i % 5}",
            "DialogType": "Standard",
            COL_GROUP: group
        }

        rows_prev.append(row.copy())
        rows_curr.append(row.copy())
        row_id += 1

    expected["No Change"] = 1000

    # ===================================================================
    # SECTION 2: StrOrigin Change only (500 rows)
    # ===================================================================
    for i in range(500):
        group = groups[i % len(groups)]
        sequence_name = f"scene_{row_id}"

        row_prev = {
            COL_STRORIGIN: f"Original text {row_id}",
            COL_EVENTNAME: f"Event_{i}",
            COL_SEQUENCE: sequence_name,
            COL_CHARACTERKEY: f"Char_{i % 20}",
            COL_DIALOGVOICE: f"Voice_{i % 10}",
            COL_SPEAKER_GROUPKEY: f"SpeakerGroup_{i % 5}",
            "DialogType": "Standard",
            COL_GROUP: group
        }

        row_curr = row_prev.copy()
        row_curr[COL_STRORIGIN] = f"Changed text {row_id}"

        rows_prev.append(row_prev)
        rows_curr.append(row_curr)
        row_id += 1

    expected["StrOrigin Change"] = 500

    # ===================================================================
    # SECTION 3: CastingKey Change only (300 rows)
    # ===================================================================
    for i in range(300):
        group = groups[i % len(groups)]
        sequence_name = f"scene_{row_id}"

        row_prev = {
            COL_STRORIGIN: f"Same text {row_id}",
            COL_EVENTNAME: f"Event_{i}",
            COL_SEQUENCE: sequence_name,
            COL_CHARACTERKEY: f"Char_{i % 20}",
            COL_DIALOGVOICE: f"Voice_A",
            COL_SPEAKER_GROUPKEY: f"SpeakerGroup_{i % 5}",
            "DialogType": "Standard",
            COL_GROUP: group
        }

        row_curr = row_prev.copy()
        row_curr[COL_DIALOGVOICE] = "Voice_B"  # Changes CastingKey

        rows_prev.append(row_prev)
        rows_curr.append(row_curr)
        row_id += 1

    expected["CastingKey Change"] = 300

    # ===================================================================
    # SECTION 4: SequenceName Change only (200 rows)
    # ===================================================================
    for i in range(200):
        group = groups[i % len(groups)]

        row_prev = {
            COL_STRORIGIN: f"Same text {row_id}",
            COL_EVENTNAME: f"Event_{i}",
            COL_SEQUENCE: f"scene_A_{i}",
            COL_CHARACTERKEY: f"Char_{i % 20}",
            COL_DIALOGVOICE: f"Voice_{i % 10}",
            COL_SPEAKER_GROUPKEY: f"SpeakerGroup_{i % 5}",
            "DialogType": "Standard",
            COL_GROUP: group
        }

        row_curr = row_prev.copy()
        row_curr[COL_SEQUENCE] = f"scene_B_{i}"

        rows_prev.append(row_prev)
        rows_curr.append(row_curr)
        row_id += 1

    expected["SequenceName Change"] = 200

    # ===================================================================
    # SECTION 5: EventName Change only (200 rows)
    # ===================================================================
    for i in range(200):
        group = groups[i % len(groups)]
        sequence_name = f"scene_{row_id}"

        row_prev = {
            COL_STRORIGIN: f"Same text {row_id}",
            COL_EVENTNAME: f"Event_Old_{i}",
            COL_SEQUENCE: sequence_name,
            COL_CHARACTERKEY: f"Char_{i % 20}",
            COL_DIALOGVOICE: f"Voice_{i % 10}",
            COL_SPEAKER_GROUPKEY: f"SpeakerGroup_{i % 5}",
            "DialogType": "Standard",
            COL_GROUP: group
        }

        row_curr = row_prev.copy()
        row_curr[COL_EVENTNAME] = f"Event_New_{i}"

        rows_prev.append(row_prev)
        rows_curr.append(row_curr)
        row_id += 1

    expected["No Relevant Change"] = 200

    # ===================================================================
    # SECTION 6: StrOrigin + CastingKey Change (200 rows)
    # ===================================================================
    for i in range(200):
        group = groups[i % len(groups)]
        sequence_name = f"scene_{row_id}"

        row_prev = {
            COL_STRORIGIN: f"Original composite text {row_id}",
            COL_EVENTNAME: f"Event_{i}",
            COL_SEQUENCE: sequence_name,
            COL_CHARACTERKEY: f"Char_{i % 20}",
            COL_DIALOGVOICE: f"Voice_A",
            COL_SPEAKER_GROUPKEY: f"SpeakerGroup_{i % 5}",
            "DialogType": "Standard",
            COL_GROUP: group
        }

        row_curr = row_prev.copy()
        row_curr[COL_STRORIGIN] = f"Changed composite text {row_id}"
        row_curr[COL_DIALOGVOICE] = "Voice_B"

        rows_prev.append(row_prev)
        rows_curr.append(row_curr)
        row_id += 1

    expected["StrOrigin+CastingKey Change"] = 200

    # ===================================================================
    # SECTION 7: StrOrigin + SequenceName Change (150 rows)
    # ===================================================================
    for i in range(150):
        group = groups[i % len(groups)]

        row_prev = {
            COL_STRORIGIN: f"Original sequence text {row_id}",
            COL_EVENTNAME: f"Event_{i}",
            COL_SEQUENCE: f"scene_old_{i}",
            COL_CHARACTERKEY: f"Char_{i % 20}",
            COL_DIALOGVOICE: f"Voice_{i % 10}",
            COL_SPEAKER_GROUPKEY: f"SpeakerGroup_{i % 5}",
            "DialogType": "Standard",
            COL_GROUP: group
        }

        row_curr = row_prev.copy()
        row_curr[COL_STRORIGIN] = f"Changed sequence text {row_id}"
        row_curr[COL_SEQUENCE] = f"scene_new_{i}"

        rows_prev.append(row_prev)
        rows_curr.append(row_curr)
        row_id += 1

    expected["StrOrigin+SequenceName Change"] = 150

    # ===================================================================
    # SECTION 8: EventName + StrOrigin Change (150 rows)
    # ===================================================================
    for i in range(150):
        group = groups[i % len(groups)]
        sequence_name = f"scene_{row_id}"

        row_prev = {
            COL_STRORIGIN: f"Original event text {row_id}",
            COL_EVENTNAME: f"Event_Old_{i}",
            COL_SEQUENCE: sequence_name,
            COL_CHARACTERKEY: f"Char_{i % 20}",
            COL_DIALOGVOICE: f"Voice_{i % 10}",
            COL_SPEAKER_GROUPKEY: f"SpeakerGroup_{i % 5}",
            "DialogType": "Standard",
            COL_GROUP: group
        }

        row_curr = row_prev.copy()
        row_curr[COL_STRORIGIN] = f"Changed event text {row_id}"
        row_curr[COL_EVENTNAME] = f"Event_New_{i}"

        rows_prev.append(row_prev)
        rows_curr.append(row_curr)
        row_id += 1

    expected["EventName+StrOrigin Change"] = 150

    # ===================================================================
    # SECTION 9: Group Migrations (300 rows - Chapter3 → Chapter6)
    # ===================================================================
    for i in range(300):
        sequence_name = f"scene_{row_id}"

        row_prev = {
            COL_STRORIGIN: f"Migration text {row_id}",
            COL_EVENTNAME: f"Event_{i}",
            COL_SEQUENCE: sequence_name,
            COL_CHARACTERKEY: f"Char_{i % 20}",
            COL_DIALOGVOICE: f"Voice_{i % 10}",
            COL_SPEAKER_GROUPKEY: f"SpeakerGroup_{i % 5}",
            "DialogType": "Standard",
            COL_GROUP: "Chapter3"
        }

        row_curr = row_prev.copy()
        row_curr[COL_GROUP] = "Chapter6"

        rows_prev.append(row_prev)
        rows_curr.append(row_curr)
        row_id += 1

    expected["No Change"] += 300  # Content same, only Group changed

    # ===================================================================
    # SECTION 10: Empty StrOrigin rows (100 rows)
    # ===================================================================
    for i in range(100):
        group = groups[i % len(groups)]
        sequence_name = f"scene_{row_id}"

        row = {
            COL_STRORIGIN: "",  # Empty StrOrigin
            COL_EVENTNAME: f"Event_{i}",
            COL_SEQUENCE: sequence_name,
            COL_CHARACTERKEY: f"Char_{i % 20}",
            COL_DIALOGVOICE: f"Voice_{i % 10}",
            COL_SPEAKER_GROUPKEY: f"SpeakerGroup_{i % 5}",
            "DialogType": "Standard",
            COL_GROUP: group
        }

        rows_prev.append(row.copy())
        rows_curr.append(row.copy())
        row_id += 1

    expected["No Change"] += 100

    # ===================================================================
    # SECTION 11: Full Duplicates (200 rows = 100 unique + 100 dupes)
    # ===================================================================
    for i in range(100):
        group = groups[i % len(groups)]
        sequence_name = f"scene_dup_{i}"

        row = {
            COL_STRORIGIN: f"Duplicate text {i}",
            COL_EVENTNAME: f"Event_Dup_{i}",
            COL_SEQUENCE: sequence_name,
            COL_CHARACTERKEY: f"Char_{i % 20}",
            COL_DIALOGVOICE: f"Voice_{i % 10}",
            COL_SPEAKER_GROUPKEY: f"SpeakerGroup_{i % 5}",
            "DialogType": "Standard",
            COL_GROUP: group
        }

        # Add original
        rows_prev.append(row.copy())
        rows_curr.append(row.copy())

        # Add duplicate
        rows_prev.append(row.copy())
        rows_curr.append(row.copy())
        row_id += 2

    expected["No Change"] += 100  # After deduplication
    expected["Full Duplicates Removed"] = 200  # 100 from PREV + 100 from CURR

    # ===================================================================
    # SECTION 12: Duplicate StrOrigin (different keys) (200 rows)
    # ===================================================================
    for i in range(100):
        group = groups[i % len(groups)]
        sequence_name = f"scene_{row_id}"

        # Row 1: Same StrOrigin, different EventName
        row1_prev = {
            COL_STRORIGIN: f"Shared text {i}",
            COL_EVENTNAME: f"Event_A_{i}",
            COL_SEQUENCE: sequence_name,
            COL_CHARACTERKEY: f"Char_{i % 20}",
            COL_DIALOGVOICE: f"Voice_{i % 10}",
            COL_SPEAKER_GROUPKEY: f"SpeakerGroup_{i % 5}",
            "DialogType": "Standard",
            COL_GROUP: group
        }

        row1_curr = row1_prev.copy()

        # Row 2: Same StrOrigin, different EventName
        row2_prev = {
            COL_STRORIGIN: f"Shared text {i}",
            COL_EVENTNAME: f"Event_B_{i}",
            COL_SEQUENCE: sequence_name,
            COL_CHARACTERKEY: f"Char_{i % 20}",
            COL_DIALOGVOICE: f"Voice_{i % 10}",
            COL_SPEAKER_GROUPKEY: f"SpeakerGroup_{i % 5}",
            "DialogType": "Standard",
            COL_GROUP: group
        }

        row2_curr = row2_prev.copy()

        rows_prev.append(row1_prev)
        rows_prev.append(row2_prev)
        rows_curr.append(row1_curr)
        rows_curr.append(row2_curr)
        row_id += 2

    expected["No Change"] += 200

    # ===================================================================
    # SECTION 13: Duplicate CastingKey (different StrOrigin) (200 rows)
    # ===================================================================
    for i in range(100):
        group = groups[i % len(groups)]
        sequence_name = f"scene_{row_id}"

        # Row 1: Same keys, different StrOrigin
        row1_prev = {
            COL_STRORIGIN: f"Text A {i}",
            COL_EVENTNAME: f"Event_{i}",
            COL_SEQUENCE: sequence_name,
            COL_CHARACTERKEY: f"Char_Shared_{i}",
            COL_DIALOGVOICE: f"Voice_Shared_{i}",
            COL_SPEAKER_GROUPKEY: f"SpeakerGroup_Shared_{i}",
            "DialogType": "Standard",
            COL_GROUP: group
        }

        row1_curr = row1_prev.copy()

        # Row 2: Same keys, different StrOrigin
        row2_prev = {
            COL_STRORIGIN: f"Text B {i}",
            COL_EVENTNAME: f"Event_{i}",
            COL_SEQUENCE: sequence_name,
            COL_CHARACTERKEY: f"Char_Shared_{i}",
            COL_DIALOGVOICE: f"Voice_Shared_{i}",
            COL_SPEAKER_GROUPKEY: f"SpeakerGroup_Shared_{i}",
            "DialogType": "Standard",
            COL_GROUP: group
        }

        row2_curr = row2_prev.copy()

        rows_prev.append(row1_prev)
        rows_prev.append(row2_prev)
        rows_curr.append(row1_curr)
        rows_curr.append(row2_curr)
        row_id += 2

    expected["No Change"] += 200

    # ===================================================================
    # SECTION 14: New Rows (500 rows - only in CURRENT)
    # ===================================================================
    for i in range(500):
        group = groups[i % len(groups)]

        # Add Quest Dialog and AI Dialog
        if i % 25 == 0:
            sequence_name = f"questdialog_new_{i}"
        elif i % 26 == 0:
            sequence_name = f"aidialog_new_{i}"
        else:
            sequence_name = f"scene_new_{i}"

        row_curr = {
            COL_STRORIGIN: f"New row text {row_id}",
            COL_EVENTNAME: f"Event_New_{i}",
            COL_SEQUENCE: sequence_name,
            COL_CHARACTERKEY: f"Char_{i % 20}",
            COL_DIALOGVOICE: f"Voice_{i % 10}",
            COL_SPEAKER_GROUPKEY: f"SpeakerGroup_{i % 5}",
            "DialogType": "Standard",
            COL_GROUP: group
        }

        rows_curr.append(row_curr)
        row_id += 1

    expected["New Row"] = 500

    # ===================================================================
    # SECTION 15: Deleted Rows (500 rows - only in PREVIOUS)
    # ===================================================================
    for i in range(500):
        group = groups[i % len(groups)]
        sequence_name = f"scene_deleted_{i}"

        row_prev = {
            COL_STRORIGIN: f"Deleted row text {row_id}",
            COL_EVENTNAME: f"Event_Del_{i}",
            COL_SEQUENCE: sequence_name,
            COL_CHARACTERKEY: f"Char_{i % 20}",
            COL_DIALOGVOICE: f"Voice_{i % 10}",
            COL_SPEAKER_GROUPKEY: f"SpeakerGroup_{i % 5}",
            "DialogType": "Standard",
            COL_GROUP: group
        }

        rows_prev.append(row_prev)
        row_id += 1

    expected["Deleted Rows"] = 500

    # Create DataFrames
    df_prev = pd.DataFrame(rows_prev)
    df_curr = pd.DataFrame(rows_curr)

    print(f"Generated PREVIOUS: {len(df_prev):,} rows")
    print(f"Generated CURRENT:  {len(df_curr):,} rows")
    print(f"\nExpected counts (after deduplication):")
    for change_type, count in sorted(expected.items()):
        print(f"  {change_type:30s}: {count:,}")

    # Write to Excel
    df_prev.to_excel(prev_path, index=False, engine="openpyxl")
    df_curr.to_excel(curr_path, index=False, engine="openpyxl")

    print(f"\n✓ Files saved:")
    print(f"  {prev_path}")
    print(f"  {curr_path}")

    return expected


if __name__ == "__main__":
    expected_counts = generate_test_files()
