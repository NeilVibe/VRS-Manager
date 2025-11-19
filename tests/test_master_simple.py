"""
Simple test for Master File processor with simplified logic.

Tests:
1. HIGH importance rows - update existing (match by EventName)
2. HIGH importance rows - add new (EventName not in TARGET)
3. Deleted rows - mark with CHANGES = "Deleted"
4. LOW importance rows - skip entirely
"""

import pandas as pd
import os
from datetime import datetime

# Test data
def create_test_data():
    """Create simple test data for Master File processor."""

    # SOURCE data (Working Process output)
    source_data = {
        "SequenceName": ["Scene1", "Scene1", "Scene2", "Scene3", "Scene4"],
        "EventName": ["E001", "E002", "E003", "E004", "E005"],
        "StrOrigin": ["Hello", "Goodbye", "Yes", "No", "Maybe"],
        "CastingKey": ["Hero_A", "Hero_A", "NPC_B", "NPC_B", "Villain_C"],
        "STATUS": ["FINAL", "RECORDED", "POLISHED", "CHECK", "SPEC-OUT"],
        "Text": ["Hi", "Bye", "Yep", "Nope", "Dunno"],
        "FREEMEMO": ["Note1", "Note2", "Note3", "Note4", "Note5"],
        "Importance": ["High", "High", "High", "High", "Low"],  # E005 is LOW - should be skipped
        "CHANGES": ["No Change", "StrOrigin Change", "New Row", "EventName Change", "No Change"],
    }

    # TARGET data (Master File)
    target_data = {
        "SequenceName": ["Scene1", "Scene1", "Scene99"],
        "EventName": ["E001", "E002", "E999"],  # E999 will be marked as Deleted
        "StrOrigin": ["Hello OLD", "Goodbye OLD", "Deleted content"],
        "CastingKey": ["Hero_A", "Hero_A", "Deleted_X"],
        "STATUS": ["OLD_STATUS", "OLD_STATUS", "OLD_STATUS"],
        "Text": ["Old Text 1", "Old Text 2", "Old Text 3"],
        "FREEMEMO": ["Old Note 1", "Old Note 2", "Old Note 3"],
        "Importance": ["High", "High", "High"],
        "CHANGES": ["OLD_CHANGES_1", "OLD_CHANGES_2", "OLD_CHANGES_3"],
    }

    df_source = pd.DataFrame(source_data)
    df_target = pd.DataFrame(target_data)

    return df_source, df_target


def run_test():
    """Run the test."""
    print("=" * 80)
    print("MASTER FILE PROCESSOR - SIMPLIFIED LOGIC TEST")
    print("=" * 80)

    # Create test data
    df_source, df_target = create_test_data()

    print("\nSOURCE Data (Working Process output):")
    print(df_source[["EventName", "Importance", "CHANGES", "STATUS", "Text"]].to_string())

    print("\nTARGET Data (Master File):")
    print(df_target[["EventName", "CHANGES", "STATUS", "Text"]].to_string())

    # Save to temp files
    source_file = "/tmp/test_master_source.xlsx"
    target_file = "/tmp/test_master_target.xlsx"

    df_source.to_excel(source_file, index=False)
    df_target.to_excel(target_file, index=False)

    print(f"\nTest files created:")
    print(f"  SOURCE: {source_file}")
    print(f"  TARGET: {target_file}")

    print("\n" + "=" * 80)
    print("EXPECTED RESULTS:")
    print("=" * 80)
    print("\n1. HIGH importance rows:")
    print("   - E001: UPDATE existing (match in TARGET) → Use SOURCE data, preserve CHANGES from SOURCE")
    print("   - E002: UPDATE existing (match in TARGET) → Use SOURCE data, preserve CHANGES from SOURCE")
    print("   - E003: ADD new row (not in TARGET) → New row with SOURCE data")
    print("   - E004: ADD new row (not in TARGET) → New row with SOURCE data")

    print("\n2. LOW importance rows:")
    print("   - E005: SKIP entirely (LOW importance) → NOT in output")

    print("\n3. Deleted rows:")
    print("   - E999: MARK as Deleted (in TARGET but not in SOURCE HIGH) → Set CHANGES = 'Deleted'")

    print("\n4. Output structure:")
    print("   - Single 'Main Sheet' with 5 rows total (4 HIGH + 1 DELETED)")
    print("   - No 'Low Importance' sheet")
    print("   - No 'Deleted Rows' sheet")

    print("\n" + "=" * 80)
    print("Now run the Master File processor manually:")
    print("  python3 main.py")
    print("  Select '4. Process Master File Update'")
    print(f"  SOURCE: {source_file}")
    print(f"  TARGET: {target_file}")
    print("=" * 80)


if __name__ == "__main__":
    run_test()
