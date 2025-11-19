"""
Test all processors to ensure no dict errors exist.
"""
import sys
import pandas as pd
from src.io.excel_reader import safe_read_excel
from src.utils.data_processing import normalize_dataframe_status, remove_full_duplicates
from src.core.casting import generate_casting_key
from src.config import COL_CASTINGKEY, COL_CHARACTERKEY, COL_DIALOGVOICE, COL_SPEAKER_GROUPKEY

def test_raw_processor():
    """Test Raw VRS Check processor."""
    print("\n" + "="*70)
    print("TESTING RAW VRS CHECK PROCESSOR")
    print("="*70)

    from src.core.lookups import build_lookups
    from src.core.comparison import process_comparison

    prev_file = 'tests/REAL PREVIOUS FILE TEST STRUCTURE.xlsx'
    curr_file = 'tests/REAL CURRENT FILE TEST STRUCTURE.xlsx'

    try:
        # Read files
        df_prev = safe_read_excel(prev_file, header=0, dtype=str)
        df_curr = safe_read_excel(curr_file, header=0, dtype=str)
        print(f"✓ Read PREVIOUS: {len(df_prev)} rows")
        print(f"✓ Read CURRENT: {len(df_curr)} rows")

        # Normalize
        df_prev = normalize_dataframe_status(df_prev)
        df_curr = normalize_dataframe_status(df_curr)
        df_prev = remove_full_duplicates(df_prev, "PREVIOUS")
        df_curr = remove_full_duplicates(df_curr, "CURRENT")

        # Generate CastingKeys
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

        # Build lookups
        prev_lookup_se, prev_lookup_so, prev_lookup_sc = build_lookups(df_prev, "PREVIOUS")
        print("✓ Built lookups")

        # Process comparison
        df_result, counter, marked_prev_indices = process_comparison(
            df_curr, df_prev, prev_lookup_se, prev_lookup_so, prev_lookup_sc
        )
        print(f"✓ RAW VRS CHECK PASSED - Result: {len(df_result)} rows")
        print(f"  Counter: {counter}")
        return True

    except Exception as e:
        print(f"✗ RAW VRS CHECK FAILED")
        print(f"  Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_working_processor():
    """Test Working VRS Check processor."""
    print("\n" + "="*70)
    print("TESTING WORKING VRS CHECK PROCESSOR")
    print("="*70)

    from src.core.working_helpers import build_working_lookups
    from src.core.working_comparison import process_working_comparison

    prev_file = 'tests/REAL PREVIOUS FILE TEST STRUCTURE.xlsx'
    curr_file = 'tests/REAL CURRENT FILE TEST STRUCTURE.xlsx'

    try:
        # Read files
        df_prev = safe_read_excel(prev_file, header=0, dtype=str)
        df_curr = safe_read_excel(curr_file, header=0, dtype=str)
        print(f"✓ Read PREVIOUS: {len(df_prev)} rows")
        print(f"✓ Read CURRENT: {len(df_curr)} rows")

        # Normalize
        df_prev = normalize_dataframe_status(df_prev)
        df_curr = normalize_dataframe_status(df_curr)
        df_prev = remove_full_duplicates(df_prev, "PREVIOUS")
        df_curr = remove_full_duplicates(df_curr, "CURRENT")

        # Generate CastingKeys
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

        # Build lookups
        (prev_lookup_se, prev_lookup_so, prev_lookup_sc,
         prev_lookup_eo, prev_lookup_ec, prev_lookup_oc,
         prev_lookup_seo, prev_lookup_sec, prev_lookup_soc, prev_lookup_eoc) = build_working_lookups(df_prev, "PREVIOUS")
        print("✓ Built lookups")

        # Process comparison
        df_result, counter, marked_prev_indices = process_working_comparison(
            df_curr, df_prev,
            prev_lookup_se, prev_lookup_so, prev_lookup_sc,
            prev_lookup_eo, prev_lookup_ec, prev_lookup_oc,
            prev_lookup_seo, prev_lookup_sec, prev_lookup_soc, prev_lookup_eoc
        )
        print(f"✓ WORKING VRS CHECK PASSED - Result: {len(df_result)} rows")
        print(f"  Counter: {counter}")
        return True

    except Exception as e:
        print(f"✗ WORKING VRS CHECK FAILED")
        print(f"  Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_alllang_processor():
    """Test All Language Check processor."""
    print("\n" + "="*70)
    print("TESTING ALL LANGUAGE CHECK PROCESSOR")
    print("="*70)

    from src.core.alllang_helpers import process_alllang_comparison

    prev_file = 'tests/REAL PREVIOUS FILE TEST STRUCTURE.xlsx'
    curr_file = 'tests/REAL CURRENT FILE TEST STRUCTURE.xlsx'

    try:
        # Read files
        df_prev = safe_read_excel(prev_file, header=0, dtype=str)
        df_curr = safe_read_excel(curr_file, header=0, dtype=str)
        print(f"✓ Read PREVIOUS: {len(df_prev)} rows")
        print(f"✓ Read CURRENT: {len(df_curr)} rows")

        # Normalize
        df_prev = normalize_dataframe_status(df_prev)
        df_curr = normalize_dataframe_status(df_curr)
        df_prev = remove_full_duplicates(df_prev, "PREVIOUS")
        df_curr = remove_full_duplicates(df_curr, "CURRENT")

        # Generate CastingKeys
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

        # Process comparison (All Language uses 4-key system like Raw)
        df_result, counter, marked_prev_indices = process_alllang_comparison(
            df_curr, df_prev
        )
        print(f"✓ ALL LANGUAGE CHECK PASSED - Result: {len(df_result)} rows")
        print(f"  Counter: {counter}")
        return True

    except Exception as e:
        print(f"✗ ALL LANGUAGE CHECK FAILED")
        print(f"  Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all processor tests."""
    print("\n" + "="*70)
    print("COMPREHENSIVE PROCESSOR TESTING")
    print("="*70)

    results = {
        "Raw VRS Check": test_raw_processor(),
        "Working VRS Check": test_working_processor(),
        "All Language Check": test_alllang_processor()
    }

    print("\n" + "="*70)
    print("FINAL TEST RESULTS")
    print("="*70)
    for processor, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{processor}: {status}")

    all_passed = all(results.values())
    print("\n" + "="*70)
    if all_passed:
        print("ALL PROCESSORS PASSED ✓")
    else:
        print("SOME PROCESSORS FAILED ✗")
    print("="*70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
