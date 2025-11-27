"""
Test comprehensive 1000-row test with TWO-PASS algorithm.

Validates:
1. Full duplicates are cleaned
2. Duplicate StrOrigin handled correctly (no 1-to-many matching)
3. Duplicate CastingKey handled correctly (no 1-to-many matching)
4. Formula: new_rows - deleted_rows = actual_difference
5. All change types detected correctly
"""

import pandas as pd
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.io.excel_reader import safe_read_excel
from src.utils.data_processing import normalize_dataframe_status, remove_full_duplicates
from src.core.casting import generate_casting_key
from src.config import COL_CASTINGKEY, COL_CHARACTERKEY, COL_DIALOGVOICE, COL_SPEAKER_GROUPKEY
from src.core.lookups import build_lookups
from src.core.comparison import compare_rows, find_deleted_rows


def test_comprehensive():
    """Run comprehensive test on TWO-PASS algorithm."""

    print("="*70)
    print("COMPREHENSIVE TWO-PASS ALGORITHM TEST")
    print("="*70)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    prev_path = os.path.join(script_dir, "test_comprehensive_PREVIOUS.xlsx")
    curr_path = os.path.join(script_dir, "test_comprehensive_CURRENT.xlsx")

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

    df_prev = remove_full_duplicates(df_prev, "PREVIOUS")
    df_curr = remove_full_duplicates(df_curr, "CURRENT")

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
    print("\n" + "="*70)
    print("VALIDATION RESULTS")
    print("="*70)

    new_rows = counter.get("New Row", 0)
    deleted_rows = len(df_deleted)
    calculated_diff = new_rows - deleted_rows

    print(f"\nFormula validation:")
    print(f"  NEW rows:     {new_rows:,}")
    print(f"  DELETED rows: {deleted_rows:,}")
    print(f"  Calculated:   {new_rows:,} - {deleted_rows:,} = {calculated_diff:+,}")
    print(f"  Actual diff:  {actual_diff:+,}")

    if calculated_diff == actual_diff:
        print(f"  ✓ PASS: Formula is correct!")
    else:
        print(f"  ✗ FAIL: Formula mismatch!")
        print(f"    Expected: {actual_diff:+,}, Got: {calculated_diff:+,}")
        return False

    # ===================================================================
    # PHASE 8: Print change type breakdown
    # ===================================================================
    print("\nChange type breakdown:")
    total_changes = 0
    for change_type, count in sorted(counter.items()):
        print(f"  {change_type:30s}: {count:,}")
        total_changes += count

    print(f"  {'─'*30}   {'─'*10}")
    print(f"  {'TOTAL':30s}: {total_changes:,}")

    # ===================================================================
    # PHASE 9: Validate expected counts
    # ===================================================================
    print("\n" + "="*70)
    print("EXPECTED vs ACTUAL")
    print("="*70)

    expected = {
        "New Row": 100,
        "No Change": 425,  # 25 cleaned dupes + 100 dup StrOrigin + 100 dup CastingKey + 200 explicit
        "Deleted Rows": 100
    }

    all_passed = True

    for change_type, expected_count in expected.items():
        if change_type == "Deleted Rows":
            actual_count = deleted_rows
        else:
            actual_count = counter.get(change_type, 0)

        match = "✓" if actual_count == expected_count else "✗"
        print(f"  {match} {change_type:30s}: Expected {expected_count:4d}, Got {actual_count:4d}")

        if actual_count != expected_count:
            all_passed = False

    # ===================================================================
    # PHASE 10: Validate Group Word Count Analysis
    # ===================================================================
    print("\n" + "="*70)
    print("GROUP WORD COUNT ANALYSIS VALIDATION")
    print("="*70)

    if group_analysis:
        print("\nGroup statistics:")
        total_prev_words = 0
        total_curr_words = 0
        total_migrations_out = 0
        total_migrations_in = 0

        for group_name, stats in sorted(group_analysis.items()):
            prev_words = stats["total_words_prev"]
            curr_words = stats["total_words_curr"]
            net_change = curr_words - prev_words

            total_prev_words += prev_words
            total_curr_words += curr_words
            total_migrations_out += stats["migrated_out_words"]
            total_migrations_in += stats["migrated_in_words"]

            print(f"  {group_name:15s}: {prev_words:5d} → {curr_words:5d} ({net_change:+5d} words)")

        print(f"\n  {'TOTAL':15s}: {total_prev_words:5d} → {total_curr_words:5d}")
        print(f"  {'Migrations Out':15s}: {total_migrations_out:5d}")
        print(f"  {'Migrations In':15s}: {total_migrations_in:5d}")

        # Validate migrations are balanced
        migrations_balanced = (total_migrations_out == total_migrations_in)
        migration_check = "✓" if migrations_balanced else "✗"
        print(f"\n  {migration_check} Migration balance check: {total_migrations_out} out = {total_migrations_in} in")

        # Check for Chapter3 → Chapter6 migrations
        chapter3_migrated_out = group_analysis.get("Chapter3", {}).get("migrated_out_words", 0)
        chapter6_migrated_in = group_analysis.get("Chapter6", {}).get("migrated_in_words", 0)

        migration_detected = (chapter3_migrated_out > 0 and chapter6_migrated_in > 0)
        migration_check2 = "✓" if migration_detected else "✗"
        print(f"  {migration_check2} Chapter3 → Chapter6 migration detected: {chapter3_migrated_out} words")

        group_validation_passed = migrations_balanced and migration_detected
    else:
        print("  ✗ No group analysis data found")
        group_validation_passed = False

    # ===================================================================
    # PHASE 11: Validate Super Group Word Count Analysis
    # ===================================================================
    print("\n" + "="*70)
    print("SUPER GROUP WORD COUNT ANALYSIS VALIDATION")
    print("="*70)

    from src.utils.super_groups import aggregate_to_super_groups

    super_group_analysis, migration_details = aggregate_to_super_groups(
        df_curr, df_prev, pass1_results
    )

    if super_group_analysis:
        print("\nSuper Group statistics:")
        super_total_prev = 0
        super_total_curr = 0

        for sg_name in sorted(super_group_analysis.keys()):
            stats = super_group_analysis[sg_name]
            prev_words = stats["total_words_prev"]
            curr_words = stats["total_words_curr"]
            net_change = curr_words - prev_words

            super_total_prev += prev_words
            super_total_curr += curr_words

            print(f"  {sg_name:<20s}: {prev_words:5d} → {curr_words:5d} ({net_change:+5d} words)")

        print(f"\n  {'TOTAL':<20s}: {super_total_prev:5d} → {super_total_curr:5d}")

        # Validate super group totals match file totals
        super_totals_match = (super_total_prev == total_prev_words and super_total_curr == total_curr_words)
        super_check = "✓" if super_totals_match else "✗"
        print(f"\n  {super_check} Super group totals match file totals? {super_totals_match}")

        # Check for Quest Dialog and AI Dialog super groups
        quest_words = super_group_analysis.get("Quest Dialog", {}).get("total_words_curr", 0)
        ai_words = super_group_analysis.get("AI Dialog", {}).get("total_words_curr", 0)

        special_detected = (quest_words > 0 and ai_words > 0)
        special_check = "✓" if special_detected else "✗"
        print(f"  {special_check} Quest Dialog & AI Dialog detected: Quest={quest_words}, AI={ai_words}")

        super_validation_passed = super_totals_match and special_detected
    else:
        print("  ✗ No super group analysis data found")
        super_validation_passed = False

    print("\n" + "="*70)

    if all_passed and calculated_diff == actual_diff and group_validation_passed and super_validation_passed:
        print("✓✓✓ ALL TESTS PASSED (INCLUDING GROUP & SUPER GROUP ANALYSIS) ✓✓✓")
        print("="*70)
        return True
    else:
        print("✗✗✗ SOME TESTS FAILED ✗✗✗")
        if not group_validation_passed:
            print("  → Group analysis validation failed")
        if not super_validation_passed:
            print("  → Super group analysis validation failed")
        print("="*70)
        return False


if __name__ == "__main__":
    success = test_comprehensive()
    sys.exit(0 if success else 1)
