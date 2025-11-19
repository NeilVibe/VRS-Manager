"""
Test script to reproduce the dict error with REAL test files.
"""
import sys
import pandas as pd
from src.io.excel_reader import safe_read_excel
from src.utils.data_processing import normalize_dataframe_status, remove_full_duplicates
from src.core.working_helpers import build_working_lookups
from src.core.working_comparison import process_working_comparison
from src.core.casting import generate_casting_key
from src.config import COL_CASTINGKEY, COL_CHARACTERKEY, COL_DIALOGVOICE, COL_SPEAKER_GROUPKEY

def test_working_real():
    """Test Working VRS Check with REAL test files."""

    prev_file = 'tests/REAL PREVIOUS FILE TEST STRUCTURE.xlsx'
    curr_file = 'tests/REAL CURRENT FILE TEST STRUCTURE.xlsx'

    print('='*70)
    print('Testing Working VRS Check with REAL files')
    print('='*70)

    try:
        # Step 1: Read files
        print(f'\n1. Reading PREVIOUS: {prev_file}')
        df_prev = safe_read_excel(prev_file, header=0, dtype=str)
        print(f'   → {len(df_prev):,} rows, {df_prev.shape[1]} columns')

        print(f'\n2. Reading CURRENT: {curr_file}')
        df_curr = safe_read_excel(curr_file, header=0, dtype=str)
        print(f'   → {len(df_curr):,} rows, {df_curr.shape[1]} columns')

        # Step 2: Normalize STATUS
        print('\n3. Normalizing STATUS columns...')
        df_prev = normalize_dataframe_status(df_prev)
        df_curr = normalize_dataframe_status(df_curr)
        print('   → STATUS columns normalized')

        # Step 3: Remove duplicates
        print('\n4. Removing full duplicate rows...')
        df_prev = remove_full_duplicates(df_prev, "PREVIOUS")
        df_curr = remove_full_duplicates(df_curr, "CURRENT")

        # Step 4: Generate CastingKeys
        print('\n5. Generating CastingKey for PREVIOUS...')
        casting_keys_prev = []
        for idx, row in df_prev.iterrows():
            casting_key = generate_casting_key(
                row.get(COL_CHARACTERKEY, ""),
                row.get(COL_DIALOGVOICE, ""),
                row.get(COL_SPEAKER_GROUPKEY, ""),
                row.get("DialogType", "")
            )
            casting_keys_prev.append(casting_key)
        df_prev[COL_CASTINGKEY] = casting_keys_prev
        print(f'   → Generated CastingKey for {len(casting_keys_prev):,} rows')

        print('\n6. Generating CastingKey for CURRENT...')
        casting_keys_curr = []
        for idx, row in df_curr.iterrows():
            casting_key = generate_casting_key(
                row.get(COL_CHARACTERKEY, ""),
                row.get(COL_DIALOGVOICE, ""),
                row.get(COL_SPEAKER_GROUPKEY, ""),
                row.get("DialogType", "")
            )
            casting_keys_curr.append(casting_key)
        df_curr[COL_CASTINGKEY] = casting_keys_curr
        print(f'   → Generated CastingKey for {len(casting_keys_curr):,} rows')

        # Step 5: Build lookups
        print('\n7. Building 10-key lookup system for PREVIOUS...')
        (prev_lookup_se, prev_lookup_so, prev_lookup_sc,
         prev_lookup_eo, prev_lookup_ec, prev_lookup_oc,
         prev_lookup_seo, prev_lookup_sec, prev_lookup_soc, prev_lookup_eoc) = build_working_lookups(df_prev, "PREVIOUS")
        print('   → 10-key lookups built')

        # Step 6: Process comparison (THIS IS WHERE ERROR LIKELY OCCURS)
        print('\n8. Processing working comparison (TWO-PASS algorithm)...')
        df_result, counter, marked_prev_indices = process_working_comparison(
            df_curr, df_prev,
            prev_lookup_se, prev_lookup_so, prev_lookup_sc,
            prev_lookup_eo, prev_lookup_ec, prev_lookup_oc,
            prev_lookup_seo, prev_lookup_sec, prev_lookup_soc, prev_lookup_eoc
        )

        print('\n✓ Working VRS Check completed successfully!')
        print(f'   → Result: {len(df_result)} rows')
        print(f'   → Counter: {counter}')

    except Exception as e:
        print(f'\n✗ ERROR occurred!')
        print(f'   Error type: {type(e).__name__}')
        print(f'   Error message: {str(e)}')
        print('\n' + '='*70)
        print('FULL TRACEBACK:')
        print('='*70)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_working_real()
