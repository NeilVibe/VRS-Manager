"""
Create comprehensive 5000-row test with REAL file structure and all edge cases.

Test cases:
1. Full duplicates (should be cleaned before processing)
2. Duplicate StrOrigin (different rows, same StrOrigin)
3. Duplicate CastingKey (different rows, same CastingKey)
4. No changes (perfect 4-key match)
5. Unique changes (one field changes)
6. Composite changes (multiple fields change)
7. New rows (all 10 keys missing)
8. Deleted rows (in PREVIOUS but not in CURRENT)
9. Empty StrOrigin cases
10. Special characters in text
11. Very long text fields
12. DialogType variations
13. Group variations
"""

import pandas as pd
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.casting import generate_casting_key

# Real file structure columns
CURR_COLUMNS = [
    'DialogType', 'Group', 'SequenceName', 'CharacterName', 'CharacterKey',
    'DialogVoice', 'StrOrigin', 'Text', 'Desc', 'Speaker|CharacterGroupKey',
    'StartFrame', 'EndFrame', 'SubTimelineName', 'CutScene', 'UseBodyAnim',
    'Random', 'Tribe', 'Age', 'Gender', 'Job', 'Region', 'EditorUsable',
    'EventName', 'UseSubtitle', 'HasAudio', 'Record', 'isNew', 'UpdateTime'
]

PREV_COLUMNS = [
    'DialogType', 'Group', 'SequenceName', 'CharacterName', 'CharacterKey',
    'DialogVoice', 'CastingKey', 'StrOrigin', 'STATUS', 'Text', 'Desc',
    'FREEMEMO', 'SubTimelineName', 'CHANGES', 'EventName', 'StartFrame',
    'EndFrame', 'Tribe', 'Age', 'Gender', 'Job', 'Region', 'UpdateTime',
    'PreviousData', 'Mainline Translation'
]

# Sample values from REAL files
DIALOG_TYPES = ['Sequencer', 'questdialog', 'aidialog', 'normaldialog', 'cutscenedialog']
GROUPS = ['Intro', 'Chapter1', 'Chapter2', 'Chapter3', 'Faction_01', 'Police', 'Shop', 'Tutorial']
CHARACTER_NAMES = ['Kliff', 'Aurelia', 'Marcus', 'Elena', 'Thorne', 'Iris', 'Zara', 'Viktor']
TRIBES = ['인간', '엘프', '드워프', '오크']
AGES = ['Adult', 'Young', 'Old', 'Child']
GENDERS = ['Male', 'Female', 'Other']
JOBS = ['용병단', 'Mage', 'Warrior', 'Rogue', 'Cleric']
REGIONS = ['Continent of Pywel', 'Northern Wastes', 'Southern Islands', 'Eastern Empire']
STATUSES = ['NEW', 'RECORDING', 'REVIEW', 'APPROVED', 'DONE']


def create_base_timestamp(row_id):
    """Create a timestamp for a given row ID."""
    base = datetime(2025, 8, 1, 10, 0, 0)
    delta = timedelta(minutes=row_id)
    return (base + delta).strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-4] + 'Z'


def create_curr_row(row_id, seq_num=None, event_num=None, origin_text=None,
                    char_key=None, dialog_voice=None, speaker_group=None,
                    text=None, dialog_type=None, group=None):
    """Create a CURRENT file row with REAL structure."""

    # Default values
    if seq_num is None:
        seq_num = row_id
    if event_num is None:
        event_num = row_id
    if char_key is None:
        char_key = f"char_{row_id}"
    if dialog_voice is None:
        dialog_voice = f"voice_{row_id}"
    if speaker_group is None:
        speaker_group = "Player"
    if origin_text is None:
        origin_text = f"origin_{row_id}"
    if text is None:
        text = f"Text content {row_id}"
    if dialog_type is None:
        dialog_type = DIALOG_TYPES[row_id % len(DIALOG_TYPES)]
    if group is None:
        group = GROUPS[row_id % len(GROUPS)]

    char_name = CHARACTER_NAMES[row_id % len(CHARACTER_NAMES)]
    tribe = TRIBES[row_id % len(TRIBES)]
    age = AGES[row_id % len(AGES)]
    gender = GENDERS[row_id % len(GENDERS)]
    job = JOBS[row_id % len(JOBS)]
    region = REGIONS[row_id % len(REGIONS)]

    return {
        'DialogType': dialog_type,
        'Group': group,
        'SequenceName': f"seq_{seq_num:05d}.seqc",
        'CharacterName': char_name,
        'CharacterKey': char_key,
        'DialogVoice': dialog_voice,
        'StrOrigin': origin_text,
        'Text': text,
        'Desc': f"Description {row_id}",
        'Speaker|CharacterGroupKey': speaker_group,
        'StartFrame': str(row_id * 100),
        'EndFrame': str(row_id * 100 + 50),
        'SubTimelineName': f"SCENE_{(row_id % 10) + 1}",
        'CutScene': 'False' if row_id % 2 == 0 else 'True',
        'UseBodyAnim': 'True' if row_id % 3 == 0 else 'False',
        'Random': 'False',
        'Tribe': tribe,
        'Age': age,
        'Gender': gender,
        'Job': job,
        'Region': region,
        'EditorUsable': 'True',
        'EventName': f"event_{event_num:05d}",
        'UseSubtitle': 'True',
        'HasAudio': 'True' if row_id % 4 != 0 else 'False',
        'Record': 'True',
        'isNew': 'False',
        'UpdateTime': create_base_timestamp(row_id)
    }


def create_prev_row(row_id, seq_num=None, event_num=None, origin_text=None,
                   char_key=None, dialog_voice=None, speaker_group=None,
                   text=None, status=None, dialog_type=None, group=None):
    """Create a PREVIOUS file row with REAL structure."""

    # Default values
    if seq_num is None:
        seq_num = row_id
    if event_num is None:
        event_num = row_id
    if char_key is None:
        char_key = f"char_{row_id}"
    if dialog_voice is None:
        dialog_voice = f"voice_{row_id}"
    if speaker_group is None:
        speaker_group = "Player"
    if origin_text is None:
        origin_text = f"origin_{row_id}"
    if text is None:
        text = f"Text content {row_id}"
    if status is None:
        status = STATUSES[row_id % len(STATUSES)]
    if dialog_type is None:
        dialog_type = DIALOG_TYPES[row_id % len(DIALOG_TYPES)]
    if group is None:
        group = GROUPS[row_id % len(GROUPS)]

    # Generate CastingKey
    casting_key = generate_casting_key(char_key, dialog_voice, speaker_group, dialog_type)

    char_name = CHARACTER_NAMES[row_id % len(CHARACTER_NAMES)]
    tribe = TRIBES[row_id % len(TRIBES)]
    age = AGES[row_id % len(AGES)]
    gender = GENDERS[row_id % len(GENDERS)]
    job = JOBS[row_id % len(JOBS)]
    region = REGIONS[row_id % len(REGIONS)]

    return {
        'DialogType': dialog_type,
        'Group': group,
        'SequenceName': f"seq_{seq_num:05d}.seqc",
        'CharacterName': char_name,
        'CharacterKey': char_key,
        'DialogVoice': dialog_voice,
        'CastingKey': casting_key,
        'StrOrigin': origin_text,
        'STATUS': status,
        'Text': text,
        'Desc': f"Description {row_id}",
        'FREEMEMO': '',
        'SubTimelineName': f"SCENE_{(row_id % 10) + 1}",
        'CHANGES': '',
        'EventName': f"event_{event_num:05d}",
        'StartFrame': str(row_id * 100),
        'EndFrame': str(row_id * 100 + 50),
        'Tribe': tribe,
        'Age': age,
        'Gender': gender,
        'Job': job,
        'Region': region,
        'UpdateTime': create_base_timestamp(row_id),
        'PreviousData': '',
        'Mainline Translation': ''
    }


def create_comprehensive_5000_test():
    """Create comprehensive test files with 5000+ rows."""

    print("Creating comprehensive 5000-row test with REAL structure...")
    print("="*70)

    prev_rows = []
    curr_rows = []

    row_id = 1

    # ===================================================================
    # CASE 1: FULL DUPLICATES (200 rows → 100 unique after cleanup)
    # ===================================================================
    print(f"\n1. Creating FULL DUPLICATES: 200 rows (100 unique)")
    for i in range(100):
        curr_row = create_curr_row(row_id)
        prev_row = create_prev_row(row_id)

        # Add same row TWICE to both PREVIOUS and CURRENT
        prev_rows.append(prev_row.copy())
        prev_rows.append(prev_row.copy())
        curr_rows.append(curr_row.copy())
        curr_rows.append(curr_row.copy())
        row_id += 1

    # ===================================================================
    # CASE 2: DUPLICATE STRORIGIN (500 rows with 50 repeated StrOrigins)
    # ===================================================================
    print(f"2. Creating DUPLICATE STRORIGIN: 500 rows (50 StrOrigins, each used 10 times)")
    for strorigin_idx in range(50):
        strorigin_text = f"RepeatedOrigin_{strorigin_idx}"
        for instance in range(10):
            prev_rows.append(create_prev_row(
                row_id, origin_text=strorigin_text,
                char_key=f"char_{row_id}", dialog_voice=f"voice_{row_id}",
                text=f"Previous text {row_id}", status="NEW"
            ))
            curr_rows.append(create_curr_row(
                row_id, origin_text=strorigin_text,
                char_key=f"char_{row_id}", dialog_voice=f"voice_{row_id}",
                text=f"Current text {row_id}"
            ))
            row_id += 1

    # ===================================================================
    # CASE 3: DUPLICATE CASTINGKEY (500 rows with 50 repeated CastingKeys)
    # ===================================================================
    print(f"3. Creating DUPLICATE CASTINGKEY: 500 rows (50 CastingKeys, each used 10 times)")
    for casting_idx in range(50):
        char_key = f"DUPECASTING_CHAR_{casting_idx}"
        dialog_voice = f"DUPECASTING_VOICE_{casting_idx}"
        speaker_group = f"DUPECASTING_GROUP_{casting_idx}"

        for instance in range(10):
            prev_rows.append(create_prev_row(
                row_id, origin_text=f"origin_{row_id}",
                char_key=char_key, dialog_voice=dialog_voice,
                speaker_group=speaker_group,
                text=f"Previous text {row_id}", status="NEW"
            ))
            curr_rows.append(create_curr_row(
                row_id, origin_text=f"origin_{row_id}",
                char_key=char_key, dialog_voice=dialog_voice,
                speaker_group=speaker_group,
                text=f"Current text {row_id}"
            ))
            row_id += 1

    # ===================================================================
    # CASE 4: NO CHANGES (perfect 4-key match) - 1000 rows
    # ===================================================================
    print(f"4. Creating NO CHANGES: 1000 rows (perfect 4-key match)")
    for i in range(1000):
        curr_row = create_curr_row(row_id)
        prev_row = create_prev_row(row_id)
        prev_rows.append(prev_row)
        curr_rows.append(curr_row)
        row_id += 1

    # ===================================================================
    # CASE 5: UNIQUE CHANGES (one field changes) - 800 rows
    # ===================================================================
    print(f"5. Creating UNIQUE CHANGES: 800 rows")

    # 5a. StrOrigin Change (200 rows)
    for i in range(200):
        prev_rows.append(create_prev_row(
            row_id, origin_text=f"OldOrigin_{row_id}", text=f"Text {row_id}", status="NEW"
        ))
        curr_rows.append(create_curr_row(
            row_id, origin_text=f"NewOrigin_{row_id}", text=f"Text {row_id}"
        ))
        row_id += 1

    # 5b. CastingKey Change (200 rows)
    for i in range(200):
        prev_rows.append(create_prev_row(
            row_id, char_key=f"OLDCHAR_{row_id}", dialog_voice=f"OLDVOICE_{row_id}",
            text=f"Text {row_id}", status="NEW"
        ))
        curr_rows.append(create_curr_row(
            row_id, char_key=f"NEWCHAR_{row_id}", dialog_voice=f"NEWVOICE_{row_id}",
            text=f"Text {row_id}"
        ))
        row_id += 1

    # 5c. EventName Change (200 rows)
    for i in range(200):
        prev_rows.append(create_prev_row(
            row_id, event_num=9000 + i, text=f"Text {row_id}", status="NEW"
        ))
        curr_rows.append(create_curr_row(
            row_id, event_num=row_id, text=f"Text {row_id}"
        ))
        row_id += 1

    # 5d. SequenceName Change (200 rows)
    for i in range(200):
        prev_rows.append(create_prev_row(
            row_id, seq_num=8000 + i, text=f"Text {row_id}", status="NEW"
        ))
        curr_rows.append(create_curr_row(
            row_id, seq_num=row_id, text=f"Text {row_id}"
        ))
        row_id += 1

    # ===================================================================
    # CASE 6: COMPOSITE CHANGES (multiple fields) - 400 rows
    # ===================================================================
    print(f"6. Creating COMPOSITE CHANGES: 400 rows")

    # 6a. StrOrigin + CastingKey Change (200 rows)
    for i in range(200):
        prev_rows.append(create_prev_row(
            row_id, origin_text=f"OldOrigin_{row_id}",
            char_key=f"OLDCHAR_{row_id}", dialog_voice=f"OLDVOICE_{row_id}",
            text=f"Text {row_id}", status="NEW"
        ))
        curr_rows.append(create_curr_row(
            row_id, origin_text=f"NewOrigin_{row_id}",
            char_key=f"NEWCHAR_{row_id}", dialog_voice=f"NEWVOICE_{row_id}",
            text=f"Text {row_id}"
        ))
        row_id += 1

    # 6b. EventName + StrOrigin Change (200 rows)
    for i in range(200):
        prev_rows.append(create_prev_row(
            row_id, event_num=7000 + i, origin_text=f"OldOrigin_{row_id}",
            text=f"Text {row_id}", status="NEW"
        ))
        curr_rows.append(create_curr_row(
            row_id, event_num=row_id, origin_text=f"NewOrigin_{row_id}",
            text=f"Text {row_id}"
        ))
        row_id += 1

    # ===================================================================
    # CASE 7: NEW ROWS (all 10 keys missing) - 500 rows
    # ===================================================================
    print(f"7. Creating NEW ROWS: 500 rows (only in CURRENT)")
    for i in range(500):
        curr_rows.append(create_curr_row(
            row_id, origin_text=f"BrandNewOrigin_{row_id}",
            char_key=f"NEWCHAR_{row_id}", dialog_voice=f"NEWVOICE_{row_id}",
            text=f"New text {row_id}"
        ))
        row_id += 1

    # ===================================================================
    # CASE 8: DELETED ROWS (only in PREVIOUS) - 500 rows
    # ===================================================================
    print(f"8. Creating DELETED ROWS: 500 rows (only in PREVIOUS)")
    for i in range(500):
        prev_rows.append(create_prev_row(
            row_id, origin_text=f"DeletedOrigin_{row_id}",
            char_key=f"DELETEDCHAR_{row_id}", dialog_voice=f"DELETEDVOICE_{row_id}",
            text=f"Deleted text {row_id}", status="NEW"
        ))
        row_id += 1

    # ===================================================================
    # CASE 9: EMPTY STRORIGIN CASES - 200 rows
    # ===================================================================
    print(f"9. Creating EMPTY STRORIGIN: 200 rows")
    for i in range(200):
        prev_rows.append(create_prev_row(
            row_id, origin_text="", text=f"Text {row_id}", status="NEW"
        ))
        curr_rows.append(create_curr_row(
            row_id, origin_text="", text=f"Text {row_id}"
        ))
        row_id += 1

    # ===================================================================
    # CASE 10: SPECIAL CHARACTERS - 200 rows
    # ===================================================================
    print(f"10. Creating SPECIAL CHARACTERS: 200 rows")
    special_texts = [
        "Text with 'quotes' and \"double quotes\"",
        "Text with newlines\nand\ttabs",
        "한글 텍스트 Korean text",
        "中文文本 Chinese text",
        "Text with symbols: @#$%^&*()",
        "Text with emoji: 🎮🎯🎨",
        "Text with special chars: é ñ ü ö",
        "Very long text " + "x" * 500
    ]
    for i in range(200):
        text = special_texts[i % len(special_texts)]
        prev_rows.append(create_prev_row(
            row_id, text=text, status="NEW"
        ))
        curr_rows.append(create_curr_row(
            row_id, text=text
        ))
        row_id += 1

    # ===================================================================
    # Create DataFrames
    # ===================================================================
    df_prev = pd.DataFrame(prev_rows, columns=PREV_COLUMNS)
    df_curr = pd.DataFrame(curr_rows, columns=CURR_COLUMNS)

    print("\n" + "="*70)
    print(f"SUMMARY:")
    print(f"  PREVIOUS: {len(df_prev):,} rows (before duplicate cleanup)")
    print(f"  CURRENT:  {len(df_curr):,} rows (before duplicate cleanup)")
    print("="*70)

    # Save files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    prev_path = os.path.join(script_dir, "test_5000_PREVIOUS.xlsx")
    curr_path = os.path.join(script_dir, "test_5000_CURRENT.xlsx")

    df_prev.to_excel(prev_path, index=False, engine='openpyxl')
    df_curr.to_excel(curr_path, index=False, engine='openpyxl')

    print(f"\n✓ Created: {prev_path}")
    print(f"✓ Created: {curr_path}")

    print("\nTest cases breakdown:")
    print(f"  1. Full duplicates: 200 rows (100 unique)")
    print(f"  2. Duplicate StrOrigin: 500 rows")
    print(f"  3. Duplicate CastingKey: 500 rows")
    print(f"  4. No changes: 1000 rows")
    print(f"  5. Unique changes: 800 rows")
    print(f"  6. Composite changes: 400 rows")
    print(f"  7. New rows: 500 rows")
    print(f"  8. Deleted rows: 500 rows")
    print(f"  9. Empty StrOrigin: 200 rows")
    print(f"  10. Special characters: 200 rows")
    print(f"  TOTAL: {len(df_prev):,} PREVIOUS, {len(df_curr):,} CURRENT")


if __name__ == "__main__":
    create_comprehensive_5000_test()
