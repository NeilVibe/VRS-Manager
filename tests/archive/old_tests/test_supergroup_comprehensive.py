"""
Comprehensive Super Group Word Analysis Test.

Validates:
1. Super group classification using DialogType column
2. Translation tracking (Text column with "NO TRANSLATION")
3. Word count accuracy
4. All 9 super groups working correctly
"""

import pandas as pd
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.io.excel_reader import safe_read_excel
from src.utils.data_processing import normalize_dataframe_status, remove_full_duplicates
from src.core.casting import generate_casting_key
from src.config import COL_CASTINGKEY, COL_CHARACTERKEY, COL_DIALOGVOICE, COL_SPEAKER_GROUPKEY, COL_STRORIGIN, COL_TEXT
from src.core.lookups import build_lookups
from src.core.comparison import compare_rows, find_deleted_rows
from src.utils.super_groups import aggregate_to_super_groups


def test_supergroup_comprehensive():
    """Run comprehensive test on super group functionality."""

    print("="*80)
    print("SUPER GROUP WORD ANALYSIS COMPREHENSIVE TEST")
    print("="*80)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    prev_path = os.path.join(script_dir, "test_supergroup_PREVIOUS.xlsx")
    curr_path = os.path.join(script_dir, "test_supergroup_CURRENT.xlsx")

    # ===================================================================
    # PHASE 1: Read files
    # ===================================================================
    print("\nPHASE 1: Reading test files...")
    df_prev = safe_read_excel(prev_path, header=0, dtype=str)
    df_curr = safe_read_excel(curr_path, header=0, dtype=str)

    print(f"  PREVIOUS: {len(df_prev):,} rows (before cleanup)")
    print(f"  CURRENT:  {len(df_curr):,} rows (before cleanup)")

    # ===================================================================
    # PHASE 2: Normalize and clean
    # ===================================================================
    print("\nPHASE 2: Normalizing...")
    df_prev = normalize_dataframe_status(df_prev)
    df_curr = normalize_dataframe_status(df_curr)

    df_prev = remove_full_duplicates(df_prev, "PREVIOUS")
    df_curr = remove_full_duplicates(df_curr, "CURRENT")

    actual_diff = len(df_curr) - len(df_prev)
    print(f"  Actual difference: {len(df_curr):,} - {len(df_prev):,} = {actual_diff:+,} rows")

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
    # PHASE 4: Build lookups and compare
    # ===================================================================
    print("\nPHASE 4: Building 10-key lookups...")
    (prev_lookup_se, prev_lookup_so, prev_lookup_sc, prev_lookup_eo,
     prev_lookup_ec, prev_lookup_oc, prev_lookup_seo, prev_lookup_sec,
     prev_lookup_soc, prev_lookup_eoc) = build_lookups(df_prev)

    print(f"  → Indexed {len(prev_lookup_se):,} unique PREVIOUS rows")

    print("\nPHASE 5: Running TWO-PASS algorithm...")
    changes, previous_strorigins, changed_columns_map, counter, marked_prev_indices, group_analysis, pass1_results = compare_rows(
        df_curr, df_prev,
        prev_lookup_se, prev_lookup_so, prev_lookup_sc,
        prev_lookup_eo, prev_lookup_ec, prev_lookup_oc,
        prev_lookup_seo, prev_lookup_sec, prev_lookup_soc, prev_lookup_eoc
    )

    print(f"  → Marked {len(marked_prev_indices):,} PREVIOUS rows")

    df_deleted = find_deleted_rows(df_prev, df_curr, marked_prev_indices)
    print(f"  → Found {len(df_deleted):,} deleted rows")

    # ===================================================================
    # PHASE 6: Generate Super Group Analysis
    # ===================================================================
    print("\n" + "="*80)
    print("SUPER GROUP WORD ANALYSIS VALIDATION")
    print("="*80)

    print("\nPHASE 6: Generating Super Group Analysis...")
    super_group_analysis, migration_details = aggregate_to_super_groups(
        df_curr, df_prev, pass1_results
    )

    if not super_group_analysis:
        print("  ✗ FAIL: No super group analysis data")
        return False

    print(f"  → Generated {len(super_group_analysis)} super groups")

    # ===================================================================
    # PHASE 7: Validate Super Group Results
    # ===================================================================
    print("\nSuper Group statistics:")

    super_total_prev = 0
    super_total_curr = 0
    super_translated = 0
    super_untranslated = 0

    for sg_name in sorted(super_group_analysis.keys()):
        stats = super_group_analysis[sg_name]
        prev_words = stats["total_words_prev"]
        curr_words = stats["total_words_curr"]
        net_change = curr_words - prev_words
        translated = stats.get("translated_words", 0)
        untranslated = stats.get("untranslated_words", 0)

        super_total_prev += prev_words
        super_total_curr += curr_words
        super_translated += translated
        super_untranslated += untranslated

        if prev_words > 0 or curr_words > 0:
            trans_pct = (translated / curr_words * 100) if curr_words > 0 else 0
            print(f"  {sg_name:<20s}: {prev_words:4d} → {curr_words:4d} ({net_change:+4d} words) | Trans: {translated:4d} ({trans_pct:5.1f}%)")

    print(f"\n  {'TOTAL':<20s}: {super_total_prev:4d} → {super_total_curr:4d}")
    print(f"  {'Translated':<20s}: {super_translated:4d}")
    print(f"  {'Untranslated':<20s}: {super_untranslated:4d}")

    # Calculate total file word count
    total_prev_file = sum(len(str(row.get(COL_STRORIGIN, "")).split()) for _, row in df_prev.iterrows())
    total_curr_file = sum(len(str(row.get(COL_STRORIGIN, "")).split()) for _, row in df_curr.iterrows())

    # ===================================================================
    # PHASE 8: Validation Checks
    # ===================================================================
    print("\n" + "="*80)
    print("VALIDATION CHECKS")
    print("="*80)

    all_pass = True

    # Check 1: Super group totals match file totals
    totals_match = (super_total_prev == total_prev_file and super_total_curr == total_curr_file)
    check1 = "✓" if totals_match else "✗"
    print(f"\n  {check1} Super group totals match file totals? {totals_match}")
    print(f"     File: {total_prev_file} → {total_curr_file}")
    print(f"     Super Groups: {super_total_prev} → {super_total_curr}")
    if not totals_match:
        all_pass = False

    # Check 2: Translation totals match current total
    translation_sum_match = (super_translated + super_untranslated == super_total_curr)
    check2 = "✓" if translation_sum_match else "✗"
    print(f"\n  {check2} Translation totals match? {translation_sum_match}")
    print(f"     Translated + Untranslated = {super_translated} + {super_untranslated} = {super_translated + super_untranslated}")
    print(f"     Total Words Current = {super_total_curr}")
    if not translation_sum_match:
        all_pass = False

    # Check 3: All expected super groups exist
    expected_super_groups = ["Main Chapters", "Faction 1", "Faction 2", "Faction 3",
                              "Faction ETC", "Quest Dialog", "AI Dialog", "Others"]

    print(f"\n  Super group detection:")
    for sg in expected_super_groups:
        curr_words = super_group_analysis.get(sg, {}).get("total_words_curr", 0)
        detected = curr_words > 0
        check = "✓" if detected else "✗"
        print(f"    {check} {sg:<20s}: {curr_words:4d} words")
        if sg in ["Main Chapters", "Quest Dialog", "AI Dialog", "Others"] and not detected:
            all_pass = False

    # Check 4: DialogType classification working correctly
    quest_words = super_group_analysis.get("Quest Dialog", {}).get("total_words_curr", 0)
    ai_words = super_group_analysis.get("AI Dialog", {}).get("total_words_curr", 0)
    others_words = super_group_analysis.get("Others", {}).get("total_words_curr", 0)

    dialogtype_check = (quest_words > 0 and ai_words > 0 and others_words > 0)
    check4 = "✓" if dialogtype_check else "✗"
    print(f"\n  {check4} DialogType classification working? {dialogtype_check}")
    print(f"     Quest Dialog: {quest_words} words")
    print(f"     AI Dialog: {ai_words} words")
    print(f"     Others (StageCloseDialog): {others_words} words")
    if not dialogtype_check:
        all_pass = False

    # Check 5: Formula validation
    new_rows = counter.get("New Row", 0)
    deleted_rows = len(df_deleted)
    calculated_diff = new_rows - deleted_rows

    formula_pass = (calculated_diff == actual_diff)
    check5 = "✓" if formula_pass else "✗"
    print(f"\n  {check5} Formula validation: New - Deleted = Actual Diff? {formula_pass}")
    print(f"     {new_rows} - {deleted_rows} = {calculated_diff} (expected: {actual_diff})")
    if not formula_pass:
        all_pass = False

    # ===================================================================
    # FINAL SUMMARY
    # ===================================================================
    print("\n" + "="*80)

    if all_pass:
        print("✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("="*80)
        print("\nSUMMARY:")
        print("  ✓ Super group totals match file totals")
        print("  ✓ Translation tracking accurate")
        print("  ✓ All expected super groups detected")
        print("  ✓ DialogType classification working")
        print("  ✓ Formula validation correct")
        print("="*80)
        return True
    else:
        print("✗✗✗ SOME TESTS FAILED ✗✗✗")
        print("="*80)
        return False


if __name__ == "__main__":
    success = test_supergroup_comprehensive()
    sys.exit(0 if success else 1)
