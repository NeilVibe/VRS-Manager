"""
Automated test runner for Master File processor.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from src.processors.master_processor import MasterProcessor

def run_automated_test():
    """Run automated test of Master File processor."""
    print("=" * 80)
    print("RUNNING AUTOMATED MASTER FILE PROCESSOR TEST")
    print("=" * 80)

    # File paths
    source_file = "/tmp/test_master_source.xlsx"
    target_file = "/tmp/test_master_target.xlsx"

    # Check files exist
    if not os.path.exists(source_file):
        print(f"ERROR: {source_file} not found. Run test_master_simple.py first.")
        return False

    if not os.path.exists(target_file):
        print(f"ERROR: {target_file} not found. Run test_master_simple.py first.")
        return False

    print(f"\nSOURCE: {source_file}")
    print(f"TARGET: {target_file}")

    # Create processor
    processor = MasterProcessor()
    processor.source_file = source_file
    processor.target_file = target_file

    # Run processing steps
    print("\n" + "-" * 80)
    print("STEP 1: Reading files...")
    print("-" * 80)
    if not processor.read_files():
        print("ERROR: Failed to read files")
        return False

    print("\n" + "-" * 80)
    print("STEP 2: Processing data...")
    print("-" * 80)
    if not processor.process_data():
        print("ERROR: Failed to process data")
        return False

    print("\n" + "-" * 80)
    print("STEP 3: Writing output...")
    print("-" * 80)
    processor.output_path = "/tmp/test_master_output.xlsx"
    if not processor.write_output():
        print("ERROR: Failed to write output")
        return False

    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)

    # Read output and verify
    df_output = pd.read_excel(processor.output_path, sheet_name="Main Sheet")

    print(f"\nOutput file: {processor.output_path}")
    print(f"Total rows: {len(df_output)}")

    print("\nOutput data:")
    print(df_output[["EventName", "CHANGES", "STATUS", "Text", "Importance"]].to_string())

    # Verify results
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)

    errors = []

    # Check row count
    expected_rows = 5  # 4 HIGH + 1 DELETED
    if len(df_output) != expected_rows:
        errors.append(f"Row count mismatch: expected {expected_rows}, got {len(df_output)}")
    else:
        print(f"✓ Row count: {len(df_output)} (correct)")

    # Check EventNames present
    expected_events = {"E001", "E002", "E003", "E004", "E999"}
    actual_events = set(df_output["EventName"].values)
    if actual_events != expected_events:
        errors.append(f"EventName mismatch: expected {expected_events}, got {actual_events}")
    else:
        print(f"✓ EventNames: {actual_events} (correct)")

    # Check E005 is NOT present (LOW importance)
    if "E005" in actual_events:
        errors.append("E005 should not be in output (LOW importance)")
    else:
        print("✓ E005 not in output (LOW importance skipped)")

    # Check E999 has CHANGES = "Deleted"
    e999_row = df_output[df_output["EventName"] == "E999"]
    if not e999_row.empty:
        changes_val = e999_row["CHANGES"].values[0]
        if changes_val != "Deleted":
            errors.append(f"E999 CHANGES should be 'Deleted', got '{changes_val}'")
        else:
            print(f"✓ E999 marked as Deleted (correct)")
    else:
        errors.append("E999 not found in output")

    # Check E001 has SOURCE data
    e001_row = df_output[df_output["EventName"] == "E001"]
    if not e001_row.empty:
        status_val = e001_row["STATUS"].values[0]
        text_val = e001_row["Text"].values[0]
        changes_val = e001_row["CHANGES"].values[0]

        if status_val != "FINAL":
            errors.append(f"E001 STATUS should be 'FINAL' (from SOURCE), got '{status_val}'")
        else:
            print(f"✓ E001 STATUS from SOURCE: {status_val} (correct)")

        if text_val != "Hi":
            errors.append(f"E001 Text should be 'Hi' (from SOURCE), got '{text_val}'")
        else:
            print(f"✓ E001 Text from SOURCE: {text_val} (correct)")

        if changes_val != "No Change":
            errors.append(f"E001 CHANGES should be 'No Change' (from SOURCE), got '{changes_val}'")
        else:
            print(f"✓ E001 CHANGES from SOURCE: {changes_val} (correct)")
    else:
        errors.append("E001 not found in output")

    print("\n" + "=" * 80)
    if errors:
        print("TEST FAILED ❌")
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("TEST PASSED ✅")
        print("\nAll checks passed successfully!")
        return True


if __name__ == "__main__":
    success = run_automated_test()
    sys.exit(0 if success else 1)
