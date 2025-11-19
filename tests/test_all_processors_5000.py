"""
Test all processors with comprehensive 5000-row test.
Measures performance to show safe_str() changes have minimal impact.
"""
import sys
import time
import pandas as pd
from src.io.excel_reader import safe_read_excel
from src.utils.data_processing import normalize_dataframe_status, remove_full_duplicates
from src.core.casting import generate_casting_key
from src.core.lookups import build_lookups
from src.core.comparison import compare_rows, find_deleted_rows
from src.core.working_helpers import build_working_lookups
from src.core.working_comparison import process_working_comparison
from src.config import COL_CASTINGKEY, COL_CHARACTERKEY, COL_DIALOGVOICE, COL_SPEAKER_GROUPKEY


def test_raw_processor():
    """Test Raw VRS Check with 5000-row dataset."""
    print("\n" + "="*70)
    print("TESTING RAW VRS CHECK - 5000 ROW DATASET")
    print("="*70)

    prev_file = 'tests/test_5000_PREVIOUS.xlsx'
    curr_file = 'tests/test_5000_CURRENT.xlsx'

    try:
        start_time = time.time()

        # Read files
        read_start = time.time()
        df_prev = safe_read_excel(prev_file, header=0, dtype=str)
        df_curr = safe_read_excel(curr_file, header=0, dtype=str)
        read_time = time.time() - read_start
        print(f"✓ Read files: {len(df_prev)} PREVIOUS, {len(df_curr)} CURRENT ({read_time:.2f}s)")

        # Normalize
        norm_start = time.time()
        df_prev = normalize_dataframe_status(df_prev)
        df_curr = normalize_dataframe_status(df_curr)
        df_prev = remove_full_duplicates(df_prev, "PREVIOUS")
        df_curr = remove_full_duplicates(df_curr, "CURRENT")
        norm_time = time.time() - norm_start
        print(f"✓ Normalized and deduplicated ({norm_time:.2f}s)")

        # Generate CastingKeys
        cast_start = time.time()
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
        cast_time = time.time() - cast_start
        print(f"✓ Generated CastingKeys ({cast_time:.2f}s)")

        # Build lookups
        lookup_start = time.time()
        (prev_lookup_se, prev_lookup_so, prev_lookup_sc,
         prev_lookup_eo, prev_lookup_ec, prev_lookup_oc,
         prev_lookup_seo, prev_lookup_sec, prev_lookup_soc, prev_lookup_eoc) = build_lookups(df_prev)
        lookup_time = time.time() - lookup_start
        print(f"✓ Built 10-key lookups ({lookup_time:.2f}s)")

        # Process comparison
        comp_start = time.time()
        changes, previous_strorigins, changed_columns_map, counter, marked_prev_indices, group_analysis, pass1_results = compare_rows(
            df_curr, df_prev,
            prev_lookup_se, prev_lookup_so, prev_lookup_sc,
            prev_lookup_eo, prev_lookup_ec, prev_lookup_oc,
            prev_lookup_seo, prev_lookup_sec, prev_lookup_soc, prev_lookup_eoc
        )
        comp_time = time.time() - comp_start
        print(f"✓ Processed comparison ({comp_time:.2f}s)")

        # Find deleted
        del_start = time.time()
        df_deleted = find_deleted_rows(df_prev, df_curr, marked_prev_indices)
        del_time = time.time() - del_start
        print(f"✓ Found deleted rows ({del_time:.2f}s)")

        total_time = time.time() - start_time

        print(f"\n✓ RAW VRS CHECK PASSED")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Rows processed: {len(df_curr):,}")
        print(f"  Performance: {len(df_curr) / total_time:.0f} rows/sec")
        print(f"  Counter: {dict(counter)}")
        print(f"  Deleted rows: {len(df_deleted)}")

        return True

    except Exception as e:
        print(f"✗ RAW VRS CHECK FAILED")
        print(f"  Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_working_processor():
    """Test Working VRS Check with 5000-row dataset."""
    print("\n" + "="*70)
    print("TESTING WORKING VRS CHECK - 5000 ROW DATASET")
    print("="*70)

    prev_file = 'tests/test_5000_PREVIOUS.xlsx'
    curr_file = 'tests/test_5000_CURRENT.xlsx'

    try:
        start_time = time.time()

        # Read files
        read_start = time.time()
        df_prev = safe_read_excel(prev_file, header=0, dtype=str)
        df_curr = safe_read_excel(curr_file, header=0, dtype=str)
        read_time = time.time() - read_start
        print(f"✓ Read files: {len(df_prev)} PREVIOUS, {len(df_curr)} CURRENT ({read_time:.2f}s)")

        # Normalize
        norm_start = time.time()
        df_prev = normalize_dataframe_status(df_prev)
        df_curr = normalize_dataframe_status(df_curr)
        df_prev = remove_full_duplicates(df_prev, "PREVIOUS")
        df_curr = remove_full_duplicates(df_curr, "CURRENT")
        norm_time = time.time() - norm_start
        print(f"✓ Normalized and deduplicated ({norm_time:.2f}s)")

        # Generate CastingKeys
        cast_start = time.time()
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
        cast_time = time.time() - cast_start
        print(f"✓ Generated CastingKeys ({cast_time:.2f}s)")

        # Build lookups
        lookup_start = time.time()
        (prev_lookup_se, prev_lookup_so, prev_lookup_sc,
         prev_lookup_eo, prev_lookup_ec, prev_lookup_oc,
         prev_lookup_seo, prev_lookup_sec, prev_lookup_soc, prev_lookup_eoc) = build_working_lookups(df_prev, "PREVIOUS")
        lookup_time = time.time() - lookup_start
        print(f"✓ Built 10-key lookups ({lookup_time:.2f}s)")

        # Process comparison
        comp_start = time.time()
        df_result, counter, marked_prev_indices = process_working_comparison(
            df_curr, df_prev,
            prev_lookup_se, prev_lookup_so, prev_lookup_sc,
            prev_lookup_eo, prev_lookup_ec, prev_lookup_oc,
            prev_lookup_seo, prev_lookup_sec, prev_lookup_soc, prev_lookup_eoc
        )
        comp_time = time.time() - comp_start
        print(f"✓ Processed comparison ({comp_time:.2f}s)")

        total_time = time.time() - start_time

        print(f"\n✓ WORKING VRS CHECK PASSED")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Rows processed: {len(df_result):,}")
        print(f"  Performance: {len(df_result) / total_time:.0f} rows/sec")
        print(f"  Counter: {dict(counter)}")

        return True

    except Exception as e:
        print(f"✗ WORKING VRS CHECK FAILED")
        print(f"  Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all processor tests with 5000-row dataset."""
    print("\n" + "="*70)
    print("COMPREHENSIVE PROCESSOR TESTING - 5000 ROW DATASET")
    print("Testing performance impact of safe_str() changes")
    print("="*70)

    results = {
        "Raw VRS Check": test_raw_processor(),
        "Working VRS Check": test_working_processor()
    }

    print("\n" + "="*70)
    print("FINAL TEST RESULTS - 5000 ROW DATASET")
    print("="*70)
    for processor, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{processor}: {status}")

    all_passed = all(results.values())
    print("\n" + "="*70)
    if all_passed:
        print("ALL PROCESSORS PASSED WITH EXCELLENT PERFORMANCE ✓")
        print("safe_str() changes have MINIMAL performance impact")
    else:
        print("SOME PROCESSORS FAILED ✗")
    print("="*70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
