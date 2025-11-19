#!/usr/bin/env python3
"""
Generate mock test data for 10-key system validation.

Creates Previous.xlsx (50 rows) and Current.xlsx (70 rows) with various change types.
Expected: new_rows - deleted_rows = 20 (actual difference)
"""

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
import random

# Column configuration (matching VRS Manager structure)
COLUMNS = [
    "SequenceName",
    "EventName",
    "StrOrigin",
    "Text",
    "STATUS",
    "FREEMEMO",
    "CharacterKey",
    "DialogVoice",
    "SpeakerGroupKey",
    "DialogType",
    "Desc",
    "StartFrame",
    "EndFrame",
    "Importance"
]

def generate_casting_key(char_key, dialog_voice, group_key, dialog_type):
    """Generate CastingKey matching VRS Manager logic."""
    parts = [char_key, dialog_voice, group_key, dialog_type]
    return "_".join(p for p in parts if p)

def create_previous_data():
    """Create Previous file with 50 rows."""
    print("Creating Previous data (50 rows)...")

    rows = []

    # We'll create different scenarios:
    # - 25 rows that will remain unchanged
    # - 10 rows that will be modified (various change types)
    # - 15 rows that will be deleted

    sequences = ["Seq_Intro", "Seq_Battle", "Seq_Ending", "Seq_Cutscene", "Seq_Tutorial"]
    characters = ["Hero_Male", "Villain_Female", "NPC_Elder", "Companion_Young", "Boss_Dragon"]
    voices = ["Main", "Secondary", "Background"]
    groups = ["A", "B", "C"]
    dialog_types = ["Dialog", "Shout", "Whisper"]

    korean_phrases = [
        "안녕하세요", "감사합니다", "미안합니다", "괜찮습니다", "좋아요",
        "어서오세요", "도와주세요", "알겠습니다", "잘 부탁합니다", "수고하셨습니다"
    ]

    statuses = ["POLISHED", "RECORDED", "FINAL", "CHECK", "NEED CHECK"]

    for i in range(50):
        # Rows 35-39 will be deleted - give them COMPLETELY UNIQUE keys
        if 35 <= i <= 39:
            row = {
                "SequenceName": f"Seq_DELETED_{i}",
                "EventName": f"Event_DELETED_{i}",
                "StrOrigin": f"삭제될_대사_{i}",
                "Text": f"Will be deleted - Row {i+1}",
                "STATUS": "DELETED",
                "FREEMEMO": f"This row will be deleted",
                "CharacterKey": f"DELETED_CHAR_{i}",
                "DialogVoice": f"DELETED_VOICE_{i}",
                "SpeakerGroupKey": f"DELETED_GROUP_{i}",
                "DialogType": "DELETED",
                "Desc": f"Deleted scene {i+1}",
                "StartFrame": str(i * 100),
                "EndFrame": str((i * 100) + 50),
                "Importance": "Low"
            }
        else:
            seq = sequences[i % len(sequences)]
            event_num = (i * 100) + 1000  # Event1000, Event1100, etc.
            event = f"Event{event_num}"

            char = characters[i % len(characters)]
            voice = voices[i % len(voices)]
            group = groups[i % len(groups)]
            dtype = dialog_types[i % len(dialog_types)]

            # Korean phrase
            korean = korean_phrases[i % len(korean_phrases)]

            row = {
                "SequenceName": seq,
                "EventName": event,
                "StrOrigin": korean,
                "Text": f"Translation of {korean} - Row {i+1}",
                "STATUS": statuses[i % len(statuses)],
                "FREEMEMO": f"Memo for row {i+1}" if i % 3 == 0 else "",
                "CharacterKey": char,
                "DialogVoice": voice,
                "SpeakerGroupKey": group,
                "DialogType": dtype,
                "Desc": f"Scene description {i+1}",
                "StartFrame": str(i * 100),
                "EndFrame": str((i * 100) + 50),
                "Importance": "High" if i % 4 == 0 else "Low"
            }

        rows.append(row)

    df = pd.DataFrame(rows, columns=COLUMNS)

    print(f"  → Created {len(df)} rows")
    return df

def create_current_data(df_prev):
    """Create Current file with 70 rows based on Previous."""
    print("\nCreating Current data (70 rows)...")

    rows = []

    # Strategy:
    # - Rows 0-24 (25 rows): Keep UNCHANGED from Previous
    # - Rows 25-29 (5 rows): StrOrigin Change
    # - Rows 30-32 (3 rows): EventName Change
    # - Row 33 (1 row): SequenceName Change
    # - Row 34 (1 row): CastingKey Change (same S,E,O but different character)
    # - Rows 35-39 (5 rows): DELETED (not in Current)
    # - Rows 40-49 (10 rows): Modified with composite changes
    # - Rows 50-69 (20 NEW rows): Brand new content

    print("  → Adding unchanged rows (0-24)...")
    # Unchanged rows (25 rows)
    for i in range(25):
        rows.append(df_prev.iloc[i].to_dict())

    print("  → Adding StrOrigin changes (25-29)...")
    # StrOrigin Change (5 rows)
    for i in range(25, 30):
        row = df_prev.iloc[i].to_dict()
        row["StrOrigin"] = "변경된 대사"  # Changed dialogue
        rows.append(row)

    print("  → Adding EventName changes (30-32)...")
    # EventName Change (3 rows)
    for i in range(30, 33):
        row = df_prev.iloc[i].to_dict()
        row["EventName"] = f"Event{int(row['EventName'].replace('Event', '')) + 5000}"
        rows.append(row)

    print("  → Adding SequenceName change (33)...")
    # SequenceName Change (1 row)
    row = df_prev.iloc[33].to_dict()
    row["SequenceName"] = "Seq_NewScene"
    rows.append(row)

    print("  → Adding CastingKey change (34)...")
    # CastingKey Change (same S,E,O but different character) (1 row)
    row = df_prev.iloc[34].to_dict()
    row["CharacterKey"] = "DifferentChar"
    row["DialogVoice"] = "DifferentVoice"
    rows.append(row)

    # Rows 35-39 are DELETED (not added to current)
    print("  → Skipping deleted rows (35-39)...")

    print("  → Adding composite changes (40-44)...")
    # Composite changes (5 rows)
    for i in range(40, 45):
        row = df_prev.iloc[i].to_dict()
        row["StrOrigin"] = "복합 변경"
        row["EventName"] = f"Event{int(row['EventName'].replace('Event', '')) + 8000}"
        rows.append(row)

    print("  → Adding more unchanged rows (45-49)...")
    # More unchanged (5 rows)
    for i in range(45, 50):
        rows.append(df_prev.iloc[i].to_dict())

    print("  → Adding 20 NEW rows (50-69)...")
    # 20 NEW rows (brand new content)
    for i in range(20):
        new_row = {
            "SequenceName": f"Seq_New_{i//5}",
            "EventName": f"EventNew{9000 + i}",
            "StrOrigin": f"새로운 대사 {i+1}",
            "Text": f"New translation {i+1}",
            "STATUS": "POLISHED",
            "FREEMEMO": "",
            "CharacterKey": f"NewChar_{i % 3}",
            "DialogVoice": "Main" if i % 2 == 0 else "Secondary",
            "SpeakerGroupKey": "A" if i % 2 == 0 else "B",
            "DialogType": "Dialog",
            "Desc": f"New scene description {i+1}",
            "StartFrame": str((i + 100) * 100),
            "EndFrame": str(((i + 100) * 100) + 50),
            "Importance": "High" if i % 3 == 0 else "Low"
        }
        rows.append(new_row)

    df = pd.DataFrame(rows, columns=COLUMNS)

    print(f"  → Created {len(df)} rows")
    print(f"\n  Expected breakdown:")
    print(f"    - Unchanged: 30 rows (0-24, 45-49)")
    print(f"    - StrOrigin Change: 5 rows (25-29)")
    print(f"    - EventName Change: 3 rows (30-32)")
    print(f"    - SequenceName Change: 1 row (33)")
    print(f"    - CastingKey Change: 1 row (34)")
    print(f"    - Composite changes: 5 rows (40-44)")
    print(f"    - DELETED: 5 rows (35-39 from Previous)")
    print(f"    - NEW: 20 rows (50-69)")
    print(f"\n  Math check:")
    print(f"    - New rows: 20")
    print(f"    - Deleted rows: 5")
    print(f"    - new_rows - deleted_rows = 20 - 5 = 15")
    print(f"    - Actual difference: 70 - 50 = 20")
    print(f"    - ❌ WAIT - This doesn't match!")
    print(f"\n  Need to adjust: Should have 25 new rows and 5 deleted to get +20 net")

    return df

def create_current_data_corrected(df_prev):
    """Create Current file with correct math: 70 rows, +20 net = 25 new - 5 deleted."""
    print("\nCreating Current data (70 rows) - CORRECTED...")

    rows = []

    # Strategy (CORRECTED):
    # - Previous has 50 rows
    # - Current has 70 rows
    # - Physical difference: +20 rows
    # - For new_rows - deleted_rows = +20:
    #   - We need 25 NEW rows and 5 DELETED rows
    #   - 25 - 5 = 20 ✓
    #
    # Breakdown:
    # - Rows from Previous 0-24 (25 rows): UNCHANGED
    # - Rows from Previous 25-29 (5 rows): StrOrigin Change
    # - Rows from Previous 30-32 (3 rows): EventName Change
    # - Row from Previous 33 (1 row): SequenceName Change
    # - Row from Previous 34 (1 row): CastingKey Change
    # - Rows from Previous 35-39 (5 rows): DELETED (not in Current)
    # - Rows from Previous 40-44 (5 rows): Composite changes
    # - Rows from Previous 45-49 (5 rows): UNCHANGED
    # Total from Previous: 50 - 5 deleted = 45 rows carried over
    # - NEW rows 0-24 (25 rows): Brand new content
    # Total in Current: 45 + 25 = 70 ✓

    print("  → Adding unchanged rows from Previous (0-24, 45-49)...")
    # Unchanged rows (30 total)
    for i in range(25):
        rows.append(df_prev.iloc[i].to_dict())

    print("  → Adding StrOrigin changes (25-29)...")
    # StrOrigin Change (5 rows)
    for i in range(25, 30):
        row = df_prev.iloc[i].to_dict()
        row["StrOrigin"] = "변경된 대사"
        rows.append(row)

    print("  → Adding EventName changes (30-32)...")
    # EventName Change (3 rows)
    for i in range(30, 33):
        row = df_prev.iloc[i].to_dict()
        row["EventName"] = f"Event{int(row['EventName'].replace('Event', '')) + 5000}"
        rows.append(row)

    print("  → Adding SequenceName change (33)...")
    # SequenceName Change (1 row)
    row = df_prev.iloc[33].to_dict()
    row["SequenceName"] = "Seq_NewScene"
    rows.append(row)

    print("  → Adding CastingKey change (34)...")
    # CastingKey Change (1 row)
    row = df_prev.iloc[34].to_dict()
    row["CharacterKey"] = "DifferentChar"
    row["DialogVoice"] = "DifferentVoice"
    rows.append(row)

    # Rows 35-39 DELETED (skip)
    print("  → Skipping deleted rows (35-39)...")

    print("  → Adding composite changes (40-44)...")
    # Composite changes (5 rows)
    for i in range(40, 45):
        row = df_prev.iloc[i].to_dict()
        row["StrOrigin"] = "복합 변경"
        row["EventName"] = f"Event{int(row['EventName'].replace('Event', '')) + 8000}"
        rows.append(row)

    print("  → Adding more unchanged rows (45-49)...")
    # More unchanged (5 rows)
    for i in range(45, 50):
        rows.append(df_prev.iloc[i].to_dict())

    print(f"  → Rows from Previous: {len(rows)} (should be 45)")

    print("  → Adding 25 NEW rows...")
    # 25 NEW rows
    for i in range(25):
        new_row = {
            "SequenceName": f"Seq_New_{i//5}",
            "EventName": f"EventNew{9000 + i}",
            "StrOrigin": f"새로운 대사 {i+1}",
            "Text": f"New translation {i+1}",
            "STATUS": "POLISHED",
            "FREEMEMO": "",
            "CharacterKey": f"NewChar_{i % 3}",
            "DialogVoice": "Main" if i % 2 == 0 else "Secondary",
            "SpeakerGroupKey": "A" if i % 2 == 0 else "B",
            "DialogType": "Dialog",
            "Desc": f"New scene {i+1}",
            "StartFrame": str((i + 100) * 100),
            "EndFrame": str(((i + 100) * 100) + 50),
            "Importance": "High" if i % 3 == 0 else "Low"
        }
        rows.append(new_row)

    df = pd.DataFrame(rows, columns=COLUMNS)

    print(f"\n✓ Created {len(df)} rows")
    print(f"\n📊 Expected Results:")
    print(f"  ├─ Previous file: 50 rows")
    print(f"  ├─ Current file: 70 rows")
    print(f"  ├─ Physical difference: 70 - 50 = +20 rows")
    print(f"  ├─")
    print(f"  ├─ Unchanged: 30 rows")
    print(f"  ├─ StrOrigin Change: 5 rows")
    print(f"  ├─ EventName Change: 3 rows")
    print(f"  ├─ SequenceName Change: 1 row")
    print(f"  ├─ CastingKey Change: 1 row")
    print(f"  ├─ Composite changes: 5 rows")
    print(f"  ├─ NEW rows: 25 rows")
    print(f"  └─ DELETED rows: 5 rows")
    print(f"\n✅ Math Verification:")
    print(f"  new_rows - deleted_rows = 25 - 5 = +20 ✓")
    print(f"  actual_difference = 70 - 50 = +20 ✓")
    print(f"  MATCH! ✓✓✓")

    return df

def save_to_excel(df, filename):
    """Save DataFrame to Excel with proper formatting."""
    print(f"\nSaving {filename}...")
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f"  ✓ Saved: {filename}")

def main():
    """Generate test data files."""
    print("="*70)
    print("VRS Manager Test Data Generator")
    print("="*70)

    # Create Previous data
    df_prev = create_previous_data()

    # Create Current data
    df_curr = create_current_data_corrected(df_prev)

    # Save files
    save_to_excel(df_prev, "Test_Previous.xlsx")
    save_to_excel(df_curr, "Test_Current.xlsx")

    print("\n" + "="*70)
    print("✅ Test data generation complete!")
    print("="*70)
    print("\nFiles created:")
    print("  - Test_Previous.xlsx (50 rows)")
    print("  - Test_Current.xlsx (70 rows)")
    print("\nNext steps:")
    print("  1. Run VRS Manager")
    print("  2. Select 'PROCESS RAW VRS CHECK'")
    print("  3. Choose Test_Previous.xlsx as PREVIOUS")
    print("  4. Choose Test_Current.xlsx as CURRENT")
    print("  5. Verify the output matches expected results!")
    print("\n")

if __name__ == "__main__":
    main()
