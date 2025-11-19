"""
Test CHANGES column preservation in Master File processor.

Tests two scenarios:
1. TARGET without CHANGES column
2. TARGET with CHANGES column
"""

import pandas as pd

# Scenario 1: TARGET WITHOUT CHANGES column
def test_without_changes_column():
    print("=" * 80)
    print("SCENARIO 1: TARGET WITHOUT CHANGES COLUMN")
    print("=" * 80)

    # SOURCE data (has CHANGES column)
    source_data = {
        "EventName": ["E001", "E002", "E003"],
        "StrOrigin": ["Hello", "Goodbye", "Yes"],
        "STATUS": ["FINAL", "RECORDED", "POLISHED"],
        "Text": ["Hi", "Bye", "Yep"],
        "Importance": ["High", "High", "High"],
        "CHANGES": ["No Change", "StrOrigin Change", "New Row"],  # CHANGES from Working Process
    }

    # TARGET data (NO CHANGES column)
    target_data = {
        "EventName": ["E001", "E002"],
        "StrOrigin": ["Hello OLD", "Goodbye OLD"],
        "STATUS": ["OLD_STATUS", "OLD_STATUS"],
        "Text": ["Old Text 1", "Old Text 2"],
        "Importance": ["High", "High"],
        # NO CHANGES column!
    }

    df_source = pd.DataFrame(source_data)
    df_target = pd.DataFrame(target_data)

    print("\nSOURCE (has CHANGES):")
    print(df_source[["EventName", "CHANGES", "STATUS"]].to_string())

    print("\nTARGET (NO CHANGES column):")
    print(df_target.columns.tolist())
    print(df_target[["EventName", "STATUS"]].to_string())

    df_source.to_excel("/tmp/test_master_source_no_changes.xlsx", index=False)
    df_target.to_excel("/tmp/test_master_target_no_changes.xlsx", index=False)

    print("\nFiles created:")
    print("  SOURCE: /tmp/test_master_source_no_changes.xlsx")
    print("  TARGET: /tmp/test_master_target_no_changes.xlsx")
    print("\nExpected: CHANGES column should be added and values from SOURCE preserved")
    print("  E001: 'No Change'")
    print("  E002: 'StrOrigin Change'")
    print("  E003: 'New Row'")


# Scenario 2: TARGET WITH CHANGES column
def test_with_changes_column():
    print("\n" + "=" * 80)
    print("SCENARIO 2: TARGET WITH CHANGES COLUMN")
    print("=" * 80)

    # SOURCE data (has CHANGES column)
    source_data = {
        "EventName": ["E001", "E002", "E003"],
        "StrOrigin": ["Hello", "Goodbye", "Yes"],
        "STATUS": ["FINAL", "RECORDED", "POLISHED"],
        "Text": ["Hi", "Bye", "Yep"],
        "Importance": ["High", "High", "High"],
        "CHANGES": ["No Change", "StrOrigin Change", "New Row"],  # From Working Process
    }

    # TARGET data (HAS CHANGES column with old values)
    target_data = {
        "EventName": ["E001", "E002"],
        "StrOrigin": ["Hello OLD", "Goodbye OLD"],
        "STATUS": ["OLD_STATUS", "OLD_STATUS"],
        "Text": ["Old Text 1", "Old Text 2"],
        "Importance": ["High", "High"],
        "CHANGES": ["OLD_CHANGES_1", "OLD_CHANGES_2"],  # Should be REPLACED with SOURCE
    }

    df_source = pd.DataFrame(source_data)
    df_target = pd.DataFrame(target_data)

    print("\nSOURCE (has CHANGES):")
    print(df_source[["EventName", "CHANGES", "STATUS"]].to_string())

    print("\nTARGET (has CHANGES - will be overwritten):")
    print(df_target[["EventName", "CHANGES", "STATUS"]].to_string())

    df_source.to_excel("/tmp/test_master_source_with_changes.xlsx", index=False)
    df_target.to_excel("/tmp/test_master_target_with_changes.xlsx", index=False)

    print("\nFiles created:")
    print("  SOURCE: /tmp/test_master_source_with_changes.xlsx")
    print("  TARGET: /tmp/test_master_target_with_changes.xlsx")
    print("\nExpected: TARGET CHANGES should be REPLACED with SOURCE values")
    print("  E001: 'No Change' (not 'OLD_CHANGES_1')")
    print("  E002: 'StrOrigin Change' (not 'OLD_CHANGES_2')")
    print("  E003: 'New Row'")


if __name__ == "__main__":
    test_without_changes_column()
    test_with_changes_column()

    print("\n" + "=" * 80)
    print("Both test files created. Run Master File processor with each pair.")
    print("=" * 80)
