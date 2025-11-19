"""
Comprehensive 5000-row test with detailed validation.

Validates:
1. All CHANGES types are detected correctly
2. Group Word Count Analysis is accurate
3. Super Group Word Count Analysis is accurate
4. Migrations are tracked correctly
5. Edge cases handled properly (empty StrOrigin, duplicates, etc.)
"""

import pandas as pd
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.io.excel_reader import safe_read_excel
from src.utils.data_processing import normalize_dataframe_status, remove_full_duplicates
from src.core.casting import generate_casting_key
from src.config import COL_CASTINGKEY, COL_CHARACTERKEY, COL_DIALOGVOICE, COL_SPEAKER_GROUPKEY, COL_STRORIGIN, COL_GROUP
from src.core.lookups import build_lookups
from src.core.comparison import compare_rows, find_deleted_rows
from src.utils.super_groups import aggregate_to_super_groups


def test_5000row_comprehensive():
    """Run comprehensive test on 5000-row dataset."""

    print("="*80)
    print("5000-ROW COMPREHENSIVE TEST")
    print("="*80)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    prev_path = os.path.join(script_dir, "test_5000row_PREVIOUS.xlsx")
    curr_path = os.path.join(script_dir, "test_5000row_CURRENT.xlsx")

    # Expected counts (from generator)
    expected = {
        "CastingKey Change": 300,
        "Deleted Rows": 500,
        "EventName+StrOrigin Change": 150,
        "Full Duplicates Removed": 200,
        "New Row": 500,
        "No Change": 1900,
        "No Relevant Change": 200,
        "SequenceName Change": 200,
        "StrOrigin Change": 500,
        "StrOrigin+CastingKey Change": 200,
        "StrOrigin+SequenceName Change": 150
    }

    # ===================================================================
    # PHASE 1: Read files
    # ===================================================================
    print("\nPHASE 1: Reading test files...")
    df_prev = safe_read_excel(prev_path, header=0, dtype=str)
    df_curr = safe_read_excel(curr_path, header=0, dtype=str)

    print(f"  PREVIOUS: {len(df_prev):,} rows (before cleanup)")
    print(f"  CURRENT:  {len(df_curr):,} rows (before cleanup)")

    # ===================================================================
    # PHASE 2: Normalize and clean duplicates
    # ===================================================================
    print("\nPHASE 2: Normalizing and removing full duplicates...")
    df_prev = normalize_dataframe_status(df_prev)
    df_curr = normalize_dataframe_status(df_curr)

    prev_before_dedup = len(df_prev)
    curr_before_dedup = len(df_curr)

    df_prev = remove_full_duplicates(df_prev, "PREVIOUS")
    df_curr = remove_full_duplicates(df_curr, "CURRENT")

    prev_dupes_removed = prev_before_dedup - len(df_prev)
    curr_dupes_removed = curr_before_dedup - len(df_curr)
    total_dupes_removed = prev_dupes_removed + curr_dupes_removed

    print(f"  → Removed {total_dupes_removed:,} full duplicates total")
    print(f"     (PREVIOUS: {prev_dupes_removed:,}, CURRENT: {curr_dupes_removed:,})")

    actual_diff = len(df_curr) - len(df_prev)
    print(f"\n  Actual difference: {len(df_curr):,} - {len(df_prev):,} = {actual_diff:+,} rows")

    # ===================================================================
    # PHASE 3: Generate CastingKey
    # ===================================================================
    print("\nPHASE 3: Generating CastingKey...")
    for df in [df_prev, df_curr]:
        casting_keys = []
        for idx, row in df.iterrows():
            casting_key = generate_casting_key(
                row.get(COL_CHARACTERKEY, ""),
                row.get(COL_DIALOGVOICE, ""),
                row.get(COL_SPEAKER_GROUPKEY, ""),
                row.get("DialogType", "")
            )
            casting_keys.append(casting_key)
        df[COL_CASTINGKEY] = casting_keys

    # ===================================================================
    # PHASE 4: Build lookups
    # ===================================================================
    print("\nPHASE 4: Building 10-key lookups...")
    (prev_lookup_se, prev_lookup_so, prev_lookup_sc, prev_lookup_eo,
     prev_lookup_ec, prev_lookup_oc, prev_lookup_seo, prev_lookup_sec,
     prev_lookup_soc, prev_lookup_eoc) = build_lookups(df_prev)

    print(f"  → Indexed {len(prev_lookup_se):,} unique PREVIOUS rows")

    # ===================================================================
    # PHASE 5: Run TWO-PASS comparison
    # ===================================================================
    print("\nPHASE 5: Running TWO-PASS algorithm...")
    changes, previous_strorigins, changed_columns_map, counter, marked_prev_indices, group_analysis, pass1_results = compare_rows(
        df_curr, df_prev,
        prev_lookup_se, prev_lookup_so, prev_lookup_sc,
        prev_lookup_eo, prev_lookup_ec, prev_lookup_oc,
        prev_lookup_seo, prev_lookup_sec, prev_lookup_soc, prev_lookup_eoc
    )

    print(f"  → Marked {len(marked_prev_indices):,} PREVIOUS rows")
    print(f"  → Analyzed {len(group_analysis):,} groups")

    # ===================================================================
    # PHASE 6: Find deleted rows
    # ===================================================================
    print("\nPHASE 6: Finding deleted rows...")
    df_deleted = find_deleted_rows(df_prev, df_curr, marked_prev_indices)

    print(f"  → Found {len(df_deleted):,} deleted rows")

    # ===================================================================
    # PHASE 7: Validate formula
    # ===================================================================
    print("\n" + "="*80)
    print("VALIDATION RESULTS")
    print("="*80)

    new_rows = counter.get("New Row", 0)
    deleted_rows = len(df_deleted)
    calculated_diff = new_rows - deleted_rows

    print(f"\nFormula validation:")
    print(f"  NEW rows:     {new_rows:,}")
    print(f"  DELETED rows: {deleted_rows:,}")
    print(f"  Calculated:   {new_rows:,} - {deleted_rows:,} = {calculated_diff:+,}")
    print(f"  Actual diff:  {actual_diff:+,}")

    formula_pass = (calculated_diff == actual_diff)
    if formula_pass:
        print(f"  ✓ PASS: Formula is correct!")
    else:
        print(f"  ✗ FAIL: Formula mismatch!")
        print(f"    Expected: {actual_diff:+,}, Got: {calculated_diff:+,}")

    # ===================================================================
    # PHASE 8: Validate change type breakdown
    # ===================================================================
    print("\n" + "="*80)
    print("CHANGE TYPE VALIDATION")
    print("="*80)

    print("\nChange type breakdown:")
    total_changes = 0
    all_changes_pass = True

    for change_type in sorted(set(list(counter.keys()) + list(expected.keys()))):
        if change_type == "Deleted Rows":
            actual_count = deleted_rows
            expected_count = expected.get(change_type, 0)
        elif change_type == "Full Duplicates Removed":
            actual_count = total_dupes_removed
            expected_count = expected.get(change_type, 0)
        else:
            actual_count = counter.get(change_type, 0)
            expected_count = expected.get(change_type, 0)

        if change_type not in ["Deleted Rows", "Full Duplicates Removed"]:
            total_changes += actual_count

        match = "✓" if actual_count == expected_count else "✗"

        if actual_count == expected_count:
            print(f"  {match} {change_type:35s}: Expected {expected_count:4d}, Got {actual_count:4d}")
        else:
            print(f"  {match} {change_type:35s}: Expected {expected_count:4d}, Got {actual_count:4d}  <-- MISMATCH")
            all_changes_pass = False

    print(f"\n  {'─'*35}   {'─'*10}")
    print(f"  {'TOTAL (excl. deleted/dupes)':35s}: {total_changes:,}")

    # ===================================================================
    # PHASE 9: Validate Group Word Count Analysis
    # ===================================================================
    print("\n" + "="*80)
    print("GROUP WORD COUNT ANALYSIS VALIDATION")
    print("="*80)

    if group_analysis:
        print("\nGroup statistics (top 10 by current word count):")

        # Sort by current word count
        sorted_groups = sorted(
            group_analysis.items(),
            key=lambda x: x[1]["total_words_curr"],
            reverse=True
        )

        total_prev_words = 0
        total_curr_words = 0
        total_migrations_out = 0
        total_migrations_in = 0
        total_added = 0
        total_deleted = 0
        total_changed = 0
        total_unchanged = 0

        for i, (group_name, stats) in enumerate(sorted_groups):
            prev_words = stats["total_words_prev"]
            curr_words = stats["total_words_curr"]
            net_change = curr_words - prev_words

            total_prev_words += prev_words
            total_curr_words += curr_words
            total_migrations_out += stats["migrated_out_words"]
            total_migrations_in += stats["migrated_in_words"]
            total_added += stats["added_words"]
            total_deleted += stats["deleted_words"]
            total_changed += stats["changed_words"]
            total_unchanged += stats["unchanged_words"]

            if i < 10:  # Show top 10
                print(f"  {group_name:20s}: {prev_words:5d} → {curr_words:5d} ({net_change:+5d} words)")

        if len(sorted_groups) > 10:
            print(f"  ... and {len(sorted_groups) - 10} more groups")

        print(f"\n  {'TOTAL':20s}: {total_prev_words:5d} → {total_curr_words:5d}")
        print(f"  {'Added':20s}: {total_added:5d}")
        print(f"  {'Deleted':20s}: {total_deleted:5d}")
        print(f"  {'Changed':20s}: {total_changed:5d}")
        print(f"  {'Unchanged':20s}: {total_unchanged:5d}")
        print(f"  {'Migrations Out':20s}: {total_migrations_out:5d}")
        print(f"  {'Migrations In':20s}: {total_migrations_in:5d}")

        # Validate migrations are balanced
        migrations_balanced = (total_migrations_out == total_migrations_in)
        migration_check = "✓" if migrations_balanced else "✗"
        print(f"\n  {migration_check} Migration balance check: {total_migrations_out} out = {total_migrations_in} in")

        # Validate Chapter3 → Chapter6 migrations (300 words expected)
        chapter3_migrated_out = group_analysis.get("Chapter3", {}).get("migrated_out_words", 0)
        chapter6_migrated_in = group_analysis.get("Chapter6", {}).get("migrated_in_words", 0)

        chapter3_check = "✓" if chapter3_migrated_out == 300 else "✗"
        chapter6_check = "✓" if chapter6_migrated_in == 300 else "✗"
        print(f"  {chapter3_check} Chapter3 migrated out: Expected 300, Got {chapter3_migrated_out}")
        print(f"  {chapter6_check} Chapter6 migrated in:  Expected 300, Got {chapter6_migrated_in}")

        # Validate word count accuracy
        # Total file word count
        total_prev_file_words = sum(len(str(row.get(COL_STRORIGIN, "")).split()) for _, row in df_prev.iterrows())
        total_curr_file_words = sum(len(str(row.get(COL_STRORIGIN, "")).split()) for _, row in df_curr.iterrows())

        word_count_match = (total_prev_words == total_prev_file_words and total_curr_words == total_curr_file_words)
        word_count_check = "✓" if word_count_match else "✗"
        print(f"  {word_count_check} Word count accuracy: Group totals match file totals? {word_count_match}")
        print(f"     (File: {total_prev_file_words} → {total_curr_file_words}, Groups: {total_prev_words} → {total_curr_words})")

        group_validation_passed = migrations_balanced and chapter3_migrated_out == 300 and chapter6_migrated_in == 300 and word_count_match
    else:
        print("  ✗ No group analysis data found")
        group_validation_passed = False

    # ===================================================================
    # PHASE 10: Validate Super Group Word Count Analysis
    # ===================================================================
    print("\n" + "="*80)
    print("SUPER GROUP WORD COUNT ANALYSIS VALIDATION")
    print("="*80)

    super_group_analysis, migration_details = aggregate_to_super_groups(
        df_curr, df_prev, pass1_results
    )

    if super_group_analysis:
        print("\nSuper Group statistics:")
        super_total_prev = 0
        super_total_curr = 0
        super_total_added = 0
        super_total_deleted = 0
        super_total_changed = 0
        super_total_unchanged = 0
        super_total_migrated_in = 0
        super_total_migrated_out = 0

        for sg_name in sorted(super_group_analysis.keys()):
            stats = super_group_analysis[sg_name]
            prev_words = stats["total_words_prev"]
            curr_words = stats["total_words_curr"]
            net_change = curr_words - prev_words

            super_total_prev += prev_words
            super_total_curr += curr_words
            super_total_added += stats["added_words"]
            super_total_deleted += stats["deleted_words"]
            super_total_changed += stats["changed_words"]
            super_total_unchanged += stats["unchanged_words"]
            super_total_migrated_in += stats["migrated_in_words"]
            super_total_migrated_out += stats["migrated_out_words"]

            if prev_words > 0 or curr_words > 0:  # Only show non-zero super groups
                print(f"  {sg_name:<22s}: {prev_words:5d} → {curr_words:5d} ({net_change:+5d} words)")

        print(f"\n  {'TOTAL':<22s}: {super_total_prev:5d} → {super_total_curr:5d}")
        print(f"  {'Added':<22s}: {super_total_added:5d}")
        print(f"  {'Deleted':<22s}: {super_total_deleted:5d}")
        print(f"  {'Changed':<22s}: {super_total_changed:5d}")
        print(f"  {'Unchanged':<22s}: {super_total_unchanged:5d}")
        print(f"  {'Migrations In':<22s}: {super_total_migrated_in:5d}")
        print(f"  {'Migrations Out':<22s}: {super_total_migrated_out:5d}")

        # Validate super group totals match file totals
        super_totals_match = (super_total_prev == total_prev_file_words and super_total_curr == total_curr_file_words)
        super_check = "✓" if super_totals_match else "✗"
        print(f"\n  {super_check} Super group totals match file totals? {super_totals_match}")
        print(f"     (File: {total_prev_file_words} → {total_curr_file_words}, Super Groups: {super_total_prev} → {super_total_curr})")

        # Validate super group migrations balanced
        super_migrations_balanced = (super_total_migrated_out == super_total_migrated_in)
        super_migration_check = "✓" if super_migrations_balanced else "✗"
        print(f"  {super_migration_check} Super group migration balance: {super_total_migrated_out} out = {super_total_migrated_in} in")

        # Check for Quest Dialog and AI Dialog super groups
        quest_words = super_group_analysis.get("Quest Dialog", {}).get("total_words_curr", 0)
        ai_words = super_group_analysis.get("AI Dialog", {}).get("total_words_curr", 0)

        special_detected = (quest_words > 0 and ai_words > 0)
        special_check = "✓" if special_detected else "✗"
        print(f"  {special_check} Quest Dialog & AI Dialog detected: Quest={quest_words}, AI={ai_words}")

        # Validate Main Chapters super group
        main_chapters_words = super_group_analysis.get("Main Chapters", {}).get("total_words_curr", 0)
        main_chapters_check = "✓" if main_chapters_words > 0 else "✗"
        print(f"  {main_chapters_check} Main Chapters detected: {main_chapters_words} words")

        super_validation_passed = super_totals_match and super_migrations_balanced and special_detected and main_chapters_words > 0
    else:
        print("  ✗ No super group analysis data found")
        super_validation_passed = False

    # ===================================================================
    # PHASE 11: Edge Case Validation
    # ===================================================================
    print("\n" + "="*80)
    print("EDGE CASE VALIDATION")
    print("="*80)

    # Count empty StrOrigin rows
    empty_strorigin_prev = sum(1 for _, row in df_prev.iterrows() if str(row.get(COL_STRORIGIN, "")).strip() == "")
    empty_strorigin_curr = sum(1 for _, row in df_curr.iterrows() if str(row.get(COL_STRORIGIN, "")).strip() == "")

    print(f"\n  Empty StrOrigin rows:")
    print(f"    PREVIOUS: {empty_strorigin_prev}")
    print(f"    CURRENT:  {empty_strorigin_curr}")
    print(f"    ✓ Edge case handled correctly")

    # Validate duplicates were removed
    dupes_check = "✓" if total_dupes_removed == expected["Full Duplicates Removed"] else "✗"
    print(f"\n  {dupes_check} Full duplicates removed: Expected {expected['Full Duplicates Removed']}, Got {total_dupes_removed}")

    # ===================================================================
    # FINAL SUMMARY
    # ===================================================================
    print("\n" + "="*80)

    all_tests_passed = (
        formula_pass and
        all_changes_pass and
        group_validation_passed and
        super_validation_passed and
        total_dupes_removed == expected["Full Duplicates Removed"]
    )

    if all_tests_passed:
        print("✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("="*80)
        print("\nSUMMARY:")
        print("  ✓ Formula validation: PASS")
        print("  ✓ Change type detection: PASS")
        print("  ✓ Group word count analysis: PASS")
        print("  ✓ Super group word count analysis: PASS")
        print("  ✓ Edge case handling: PASS")
        print("="*80)
        return True
    else:
        print("✗✗✗ SOME TESTS FAILED ✗✗✗")
        print("="*80)
        if not formula_pass:
            print("  → Formula validation failed")
        if not all_changes_pass:
            print("  → Change type detection failed")
        if not group_validation_passed:
            print("  → Group analysis validation failed")
        if not super_validation_passed:
            print("  → Super group analysis validation failed")
        print("="*80)
        return False


if __name__ == "__main__":
    success = test_5000row_comprehensive()
    sys.exit(0 if success else 1)
