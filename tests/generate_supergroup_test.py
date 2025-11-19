"""
Generate test files for Super Group Word Analysis with DialogType and Text columns.

Tests:
- Main Chapters (Group: Chapter1-6, Intro, Prolog)
- Faction 1-3, Faction ETC (Group: faction_01-03, faction_etc)
- Quest Dialog (DialogType: QuestDialog)
- AI Dialog (DialogType: AIDialog)
- Others (DialogType: StageCloseDialog)
- Translation tracking (Text column with "NO TRANSLATION")
"""

import pandas as pd
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import COL_STRORIGIN, COL_EVENTNAME, COL_CHARACTERKEY, COL_DIALOGVOICE, COL_SPEAKER_GROUPKEY, COL_SEQUENCE, COL_GROUP, COL_TEXT


def generate_test_files():
    """Generate test files with DialogType and Text columns."""

    script_dir = os.path.dirname(os.path.abspath(__file__))
    prev_path = os.path.join(script_dir, "test_supergroup_PREVIOUS.xlsx")
    curr_path = os.path.join(script_dir, "test_supergroup_CURRENT.xlsx")

    rows_prev = []
    rows_curr = []

    row_id = 1

    # Helper function to create row
    def create_row(strorigin, group, dialog_type, text, event_num):
        return {
            COL_STRORIGIN: strorigin,
            COL_EVENTNAME: f"Event_{event_num}",
            COL_SEQUENCE: f"scene_{event_num}",
            COL_CHARACTERKEY: f"Char_{event_num % 10}",
            COL_DIALOGVOICE: f"Voice_{event_num % 5}",
            COL_SPEAKER_GROUPKEY: f"SpeakerGroup_{event_num % 3}",
            "DialogType": dialog_type,
            COL_GROUP: group,
            COL_TEXT: text
        }

    # ===================================================================
    # SECTION 1: Main Chapters (200 rows, 80% translated)
    # ===================================================================
    for i in range(200):
        group = ["Intro", "Prolog", "Chapter1", "Chapter2", "Chapter3", "Chapter4"][i % 6]
        text = "Translated text content" if i % 5 != 0 else "NO TRANSLATION"
        strorigin = f"Main chapter dialogue {row_id}"

        row = create_row(strorigin, group, "Standard", text, row_id)
        rows_prev.append(row.copy())
        rows_curr.append(row.copy())
        row_id += 1

    # ===================================================================
    # SECTION 2: Faction 1 (50 rows, 90% translated)
    # ===================================================================
    for i in range(50):
        text = "Translated text content" if i % 10 != 0 else "NO TRANSLATION"
        strorigin = f"Faction 1 dialogue {row_id}"

        row = create_row(strorigin, "faction_01", "Standard", text, row_id)
        rows_prev.append(row.copy())
        rows_curr.append(row.copy())
        row_id += 1

    # ===================================================================
    # SECTION 3: Faction 2 (50 rows, 70% translated)
    # ===================================================================
    for i in range(50):
        text = "Translated text content" if i % 10 < 7 else "NO TRANSLATION"
        strorigin = f"Faction 2 dialogue {row_id}"

        row = create_row(strorigin, "faction_02", "Standard", text, row_id)
        rows_prev.append(row.copy())
        rows_curr.append(row.copy())
        row_id += 1

    # ===================================================================
    # SECTION 4: Faction 3 (50 rows, 100% translated)
    # ===================================================================
    for i in range(50):
        text = "Translated text content"
        strorigin = f"Faction 3 dialogue {row_id}"

        row = create_row(strorigin, "faction_03", "Standard", text, row_id)
        rows_prev.append(row.copy())
        rows_curr.append(row.copy())
        row_id += 1

    # ===================================================================
    # SECTION 5: Faction ETC (30 rows, 50% translated)
    # ===================================================================
    for i in range(30):
        text = "Translated text content" if i % 2 == 0 else "NO TRANSLATION"
        strorigin = f"Faction ETC dialogue {row_id}"

        row = create_row(strorigin, "faction_etc", "Standard", text, row_id)
        rows_prev.append(row.copy())
        rows_curr.append(row.copy())
        row_id += 1

    # ===================================================================
    # SECTION 6: Quest Dialog (100 rows, 95% translated)
    # DialogType = "QuestDialog" (case-insensitive test)
    # ===================================================================
    dialog_types_quest = ["QuestDialog", "questdialog", "QUESTDIALOG", "QuestDialog"]
    for i in range(100):
        text = "Translated text content" if i % 20 != 0 else "NO TRANSLATION"
        strorigin = f"Quest dialog text {row_id}"
        dialog_type = dialog_types_quest[i % len(dialog_types_quest)]

        row = create_row(strorigin, "Chapter1", dialog_type, text, row_id)
        rows_prev.append(row.copy())
        rows_curr.append(row.copy())
        row_id += 1

    # ===================================================================
    # SECTION 7: AI Dialog (80 rows, 60% translated)
    # DialogType = "AIDialog" (case-insensitive test)
    # ===================================================================
    dialog_types_ai = ["AIDialog", "aidialog", "AIDIALOG", "AIDialog"]
    for i in range(80):
        text = "Translated text content" if i % 5 < 3 else "NO TRANSLATION"
        strorigin = f"AI dialog text {row_id}"
        dialog_type = dialog_types_ai[i % len(dialog_types_ai)]

        row = create_row(strorigin, "Chapter2", dialog_type, text, row_id)
        rows_prev.append(row.copy())
        rows_curr.append(row.copy())
        row_id += 1

    # ===================================================================
    # SECTION 8: Others (StageCloseDialog) (40 rows, 25% translated)
    # DialogType = "StageCloseDialog" (case-insensitive test)
    # ===================================================================
    dialog_types_stage = ["StageCloseDialog", "stageclosedialog", "STAGECLOSEDIALOG"]
    for i in range(40):
        text = "Translated text content" if i % 4 == 0 else "NO TRANSLATION"
        strorigin = f"Stage close dialog {row_id}"
        dialog_type = dialog_types_stage[i % len(dialog_types_stage)]

        row = create_row(strorigin, "Chapter3", dialog_type, text, row_id)
        rows_prev.append(row.copy())
        rows_curr.append(row.copy())
        row_id += 1

    # ===================================================================
    # SECTION 9: New rows in CURRENT (50 rows, mix of super groups)
    # ===================================================================
    for i in range(10):
        text = "Translated text content"
        strorigin = f"New main chapter row {row_id}"
        row = create_row(strorigin, "Chapter5", "Standard", text, row_id)
        rows_curr.append(row)
        row_id += 1

    for i in range(10):
        text = "NO TRANSLATION"
        strorigin = f"New quest dialog row {row_id}"
        row = create_row(strorigin, "Chapter1", "QuestDialog", text, row_id)
        rows_curr.append(row)
        row_id += 1

    for i in range(10):
        text = "NO TRANSLATION"
        strorigin = f"New AI dialog row {row_id}"
        row = create_row(strorigin, "Chapter2", "AIDialog", text, row_id)
        rows_curr.append(row)
        row_id += 1

    for i in range(10):
        text = "Translated text content"
        strorigin = f"New faction row {row_id}"
        row = create_row(strorigin, "faction_01", "Standard", text, row_id)
        rows_curr.append(row)
        row_id += 1

    for i in range(10):
        text = "NO TRANSLATION"
        strorigin = f"New others row {row_id}"
        row = create_row(strorigin, "Chapter3", "StageCloseDialog", text, row_id)
        rows_curr.append(row)
        row_id += 1

    # ===================================================================
    # SECTION 10: Deleted rows in PREVIOUS (50 rows)
    # ===================================================================
    for i in range(50):
        group = ["Chapter1", "faction_01", "Chapter2"][i % 3]
        dialog_type = ["Standard", "QuestDialog", "AIDialog"][i % 3]
        text = "Translated text content"
        strorigin = f"Deleted row {row_id}"
        row = create_row(strorigin, group, dialog_type, text, row_id)
        rows_prev.append(row)
        row_id += 1

    # Create DataFrames
    df_prev = pd.DataFrame(rows_prev)
    df_curr = pd.DataFrame(rows_curr)

    print(f"Generated PREVIOUS: {len(df_prev):,} rows")
    print(f"Generated CURRENT:  {len(df_curr):,} rows")

    # Count super groups
    from src.utils.super_groups import classify_super_group

    sg_counts_prev = {}
    for _, row in df_prev.iterrows():
        sg = classify_super_group(row, row.get(COL_GROUP, "Unknown"))
        sg_counts_prev[sg] = sg_counts_prev.get(sg, 0) + 1

    sg_counts_curr = {}
    for _, row in df_curr.iterrows():
        sg = classify_super_group(row, row.get(COL_GROUP, "Unknown"))
        sg_counts_curr[sg] = sg_counts_curr.get(sg, 0) + 1

    print(f"\nSuper Group distribution (PREVIOUS):")
    for sg, count in sorted(sg_counts_prev.items()):
        print(f"  {sg:20s}: {count:3d} rows")

    print(f"\nSuper Group distribution (CURRENT):")
    for sg, count in sorted(sg_counts_curr.items()):
        print(f"  {sg:20s}: {count:3d} rows")

    # Write to Excel
    df_prev.to_excel(prev_path, index=False, engine="openpyxl")
    df_curr.to_excel(curr_path, index=False, engine="openpyxl")

    print(f"\n✓ Files saved:")
    print(f"  {prev_path}")
    print(f"  {curr_path}")


if __name__ == "__main__":
    generate_test_files()
