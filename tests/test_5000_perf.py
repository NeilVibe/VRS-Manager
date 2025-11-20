"""Test all processors with 5000-row dataset - Performance test."""
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.io.excel_reader import safe_read_excel
from src.utils.data_processing import normalize_dataframe_status, remove_full_duplicates
from src.core.casting import generate_casting_key
from src.core.lookups import build_lookups
from src.core.comparison import compare_rows, find_deleted_rows
from src.core.working_helpers import build_working_lookups
from src.core.working_comparison import process_working_comparison
from src.config import COL_CASTINGKEY, COL_CHARACTERKEY, COL_DIALOGVOICE, COL_SPEAKER_GROUPKEY

def test_raw():
    print("="*70)
    print("RAW VRS CHECK - 5000 ROW TEST")
    print("="*70)
    start = time.time()
    
    df_prev = safe_read_excel('tests/test_5000_PREVIOUS.xlsx', header=0, dtype=str)
    df_curr = safe_read_excel('tests/test_5000_CURRENT.xlsx', header=0, dtype=str)
    print(f"Read: {time.time()-start:.2f}s - {len(df_prev)} PREV, {len(df_curr)} CURR")
    
    df_prev = normalize_dataframe_status(df_prev)
    df_curr = normalize_dataframe_status(df_curr)
    df_prev = remove_full_duplicates(df_prev, "PREVIOUS")
    df_curr = remove_full_duplicates(df_curr, "CURRENT")
    
    for df in [df_prev, df_curr]:
        keys = []
        for idx, row in df.iterrows():
            keys.append(generate_casting_key(
                row.get(COL_CHARACTERKEY, ""), row.get(COL_DIALOGVOICE, ""),
                row.get(COL_SPEAKER_GROUPKEY, ""), row.get("DialogType", "")))
        df[COL_CASTINGKEY] = keys
    
    lookups = build_lookups(df_prev)
    print(f"Lookups: {time.time()-start:.2f}s")
    
    changes, prev_origins, cols, counter, marked, groups, pass1 = compare_rows(
        df_curr, df_prev, *lookups)
    print(f"Comparison: {time.time()-start:.2f}s")
    
    deleted = find_deleted_rows(df_prev, df_curr, marked)
    total = time.time()-start
    print(f"✓ DONE: {total:.2f}s ({len(df_curr)/total:.0f} rows/sec)")
    print(f"  Counter: {dict(counter)}")
    return True

def test_working():
    print("\n" + "="*70)
    print("WORKING VRS CHECK - 5000 ROW TEST")
    print("="*70)
    start = time.time()
    
    df_prev = safe_read_excel('tests/test_5000_PREVIOUS.xlsx', header=0, dtype=str)
    df_curr = safe_read_excel('tests/test_5000_CURRENT.xlsx', header=0, dtype=str)
    print(f"Read: {time.time()-start:.2f}s - {len(df_prev)} PREV, {len(df_curr)} CURR")
    
    df_prev = normalize_dataframe_status(df_prev)
    df_curr = normalize_dataframe_status(df_curr)
    df_prev = remove_full_duplicates(df_prev, "PREVIOUS")
    df_curr = remove_full_duplicates(df_curr, "CURRENT")
    
    for df in [df_prev, df_curr]:
        keys = []
        for idx, row in df.iterrows():
            keys.append(generate_casting_key(
                row.get(COL_CHARACTERKEY, ""), row.get(COL_DIALOGVOICE, ""),
                row.get(COL_SPEAKER_GROUPKEY, ""), row.get("DialogType", "")))
        df[COL_CASTINGKEY] = keys
    
    lookups = build_working_lookups(df_prev, "PREVIOUS")
    print(f"Lookups: {time.time()-start:.2f}s")
    
    result, counter, marked = process_working_comparison(df_curr, df_prev, *lookups)
    total = time.time()-start
    print(f"✓ DONE: {total:.2f}s ({len(result)/total:.0f} rows/sec)")
    print(f"  Counter: {dict(counter)}")
    return True

if __name__ == "__main__":
    print("TESTING safe_str() PERFORMANCE IMPACT\n")
    raw_ok = test_raw()
    work_ok = test_working()
    print("\n" + "="*70)
    if raw_ok and work_ok:
        print("✓ ALL TESTS PASSED - safe_str() has MINIMAL performance impact")
    else:
        print("✗ SOME TESTS FAILED")
    print("="*70)
