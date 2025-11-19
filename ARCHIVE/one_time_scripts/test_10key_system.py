#!/usr/bin/env python3
"""
Test the 10-key system with generated mock data.
Runs Raw VRS Check programmatically and validates results.
"""

import sys
import os
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.processors.raw_processor import RawProcessor
from src.utils.helpers import log

def test_raw_process():
    """Test Raw VRS Check with mock data."""
    print("="*70)
    print("Testing 10-Key System with Mock Data")
    print("="*70)

    # Paths to test files
    prev_file = "Test_Previous.xlsx"
    curr_file = "Test_Current.xlsx"

    if not os.path.exists(prev_file) or not os.path.exists(curr_file):
        print("❌ Error: Test files not found!")
        print("Please run generate_test_data.py first")
        return False

    # Create processor
    processor = RawProcessor()

    # Set files manually (bypass GUI)
    processor.prev_file = os.path.abspath(prev_file)
    processor.curr_file = os.path.abspath(curr_file)

    print(f"\nPREVIOUS: {os.path.basename(processor.prev_file)}")
    print(f"CURRENT:  {os.path.basename(processor.curr_file)}")

    # Read files
    print("\n" + "-"*70)
    print("STEP 1: Reading Files")
    print("-"*70)
    if not processor.read_files():
        print("❌ Failed to read files")
        return False

    # Process data
    print("\n" + "-"*70)
    print("STEP 2: Processing Data (10-Key System)")
    print("-"*70)
    if not processor.process_data():
        print("❌ Failed to process data")
        return False

    # Analyze results
    print("\n" + "="*70)
    print("RESULTS ANALYSIS")
    print("="*70)

    print("\n📊 Change Type Breakdown:")
    for change_type, count in sorted(processor.counter.items(), key=lambda x: -x[1]):
        print(f"  {change_type:.<40} {count:>5} rows")

    # Calculate totals
    new_rows = processor.counter.get("New Row", 0)
    deleted_rows = processor.counter.get("Deleted Rows", 0)
    net_change = new_rows - deleted_rows

    prev_count = len(processor.df_prev)
    curr_count = len(processor.df_curr)
    actual_diff = curr_count - prev_count

    print(f"\n📈 Row Count Analysis:")
    print(f"  Previous file rows.................... {prev_count:>5}")
    print(f"  Current file rows..................... {curr_count:>5}")
    print(f"  Actual difference (Current - Previous). {actual_diff:>+5}")
    print(f"\n  New rows detected..................... {new_rows:>5}")
    print(f"  Deleted rows detected................. {deleted_rows:>5}")
    print(f"  Net change (New - Deleted)............ {net_change:>+5}")

    print(f"\n✅ Validation:")
    if net_change == actual_diff:
        print(f"  ✓ PASS: net_change ({net_change:+d}) == actual_diff ({actual_diff:+d})")
        print(f"  ✓ The 10-key system is working correctly!")
        validation_passed = True
    else:
        print(f"  ✗ FAIL: net_change ({net_change:+d}) != actual_diff ({actual_diff:+d})")
        print(f"  ✗ Bug still exists!")
        validation_passed = False

    # Expected values
    print(f"\n📋 Expected vs Actual:")
    expected = {
        "New Row": 25,
        "Deleted Rows": 5,
        "No Change": 30,
        "StrOrigin Change": 5,
        "EventName Change": 3,
        "SequenceName Change": 1,
        "CastingKey Change": 1,
    }

    all_match = True
    for change_type, expected_count in expected.items():
        actual_count = processor.counter.get(change_type, 0)
        match = "✓" if actual_count == expected_count else "✗"
        if actual_count != expected_count:
            all_match = False
        print(f"  {match} {change_type:.<35} Exp:{expected_count:>3}  Act:{actual_count:>3}")

    # Check for composite changes
    composite_count = sum(count for change_type, count in processor.counter.items()
                         if "+" in change_type or "Composite" in change_type)
    print(f"  {'~'} Composite changes (various)............. Exp:  5  Act:{composite_count:>3}")

    print("\n" + "="*70)
    if validation_passed and all_match:
        print("🎉 ALL TESTS PASSED! 10-Key System Works Perfectly!")
    elif validation_passed:
        print("⚠️  Math is correct but some change classifications differ")
    else:
        print("❌ TESTS FAILED! Bug detected!")
    print("="*70)

    # Write output for inspection
    print("\n📝 Writing output file for manual inspection...")
    if processor.write_output():
        print(f"  ✓ Output saved: {os.path.basename(processor.output_path)}")
        print(f"  → Open this file to verify change classifications")

    return validation_passed

if __name__ == "__main__":
    success = test_raw_process()
    sys.exit(0 if success else 1)
