"""
Test standalone metadata changes (single field changes).

This test verifies that STANDALONE changes are detected correctly
when ONLY one metadata field changes (no core key changes).
"""

import pandas as pd
from src.core.comparison import process_raw_comparison
from src.core.working_comparison import process_working_comparison
from src.core.lookups import build_lookup_dictionaries
from src.core.working_helpers import build_working_lookup_dictionaries

def test_standalone_changes():
    """Test that standalone metadata changes are detected."""
    print("="*70)
    print("TESTING STANDALONE METADATA CHANGES")
    print("="*70)

    # Create test data with ONLY metadata changes (all 4 core keys identical)
    base_data = {
        "SequenceName": "Seq1",
        "EventName": "Event1",
        "StrOrigin": "Hello World",
        "CharacterKey": "Char1",
        "DialogVoice": "Voice1",
        "Speaker|CharacterGroupKey": "Group1",
        "DialogType": "Dialogue",
        "CastingKey": "Char1_Voice1_Group1_Dialogue",
        "Text": "Translation",
        "STATUS": "POLISHED",
        "FREEMEMO": "Memo",
        "Desc": "Original Desc",
        "StartFrame": "100",
        "EndFrame": "200",
        "Group": "Chapter1",
        "Tribe": "Human",
        "Age": "Adult",
        "Gender": "Male"
    }

    # PREVIOUS data
    prev_data = []

    # Row 1: Will have ONLY TimeFrame change
    row1_prev = base_data.copy()
    prev_data.append(row1_prev)

    # Row 2: Will have ONLY Desc change
    row2_prev = base_data.copy()
    row2_prev["SequenceName"] = "Seq2"
    row2_prev["EventName"] = "Event2"
    prev_data.append(row2_prev)

    # Row 3: Will have ONLY DialogType change
    row3_prev = base_data.copy()
    row3_prev["SequenceName"] = "Seq3"
    row3_prev["EventName"] = "Event3"
    prev_data.append(row3_prev)

    # Row 4: Will have ONLY Group change
    row4_prev = base_data.copy()
    row4_prev["SequenceName"] = "Seq4"
    row4_prev["EventName"] = "Event4"
    prev_data.append(row4_prev)

    # Row 5: Will have ONLY Character Group change
    row5_prev = base_data.copy()
    row5_prev["SequenceName"] = "Seq5"
    row5_prev["EventName"] = "Event5"
    prev_data.append(row5_prev)

    # Row 6: Will have composite TimeFrame+Desc change
    row6_prev = base_data.copy()
    row6_prev["SequenceName"] = "Seq6"
    row6_prev["EventName"] = "Event6"
    prev_data.append(row6_prev)

    # Row 7: Will have No Change (perfect match)
    row7_prev = base_data.copy()
    row7_prev["SequenceName"] = "Seq7"
    row7_prev["EventName"] = "Event7"
    prev_data.append(row7_prev)

    # CURRENT data with changes
    curr_data = []

    # Row 1: ONLY TimeFrame changed
    row1_curr = row1_prev.copy()
    row1_curr["StartFrame"] = "150"  # Changed from 100
    row1_curr["EndFrame"] = "250"    # Changed from 200
    curr_data.append(row1_curr)

    # Row 2: ONLY Desc changed
    row2_curr = row2_prev.copy()
    row2_curr["Desc"] = "Modified Desc"  # Changed
    curr_data.append(row2_curr)

    # Row 3: ONLY DialogType changed
    row3_curr = row3_prev.copy()
    row3_curr["DialogType"] = "Narration"  # Changed from Dialogue
    curr_data.append(row3_curr)

    # Row 4: ONLY Group changed
    row4_curr = row4_prev.copy()
    row4_curr["Group"] = "Chapter2"  # Changed from Chapter1
    curr_data.append(row4_curr)

    # Row 5: ONLY Character Group changed
    row5_curr = row5_prev.copy()
    row5_curr["Gender"] = "Female"  # Changed from Male
    curr_data.append(row5_curr)

    # Row 6: Composite TimeFrame+Desc change
    row6_curr = row6_prev.copy()
    row6_curr["StartFrame"] = "150"
    row6_curr["Desc"] = "Modified Desc"
    curr_data.append(row6_curr)

    # Row 7: No Change
    row7_curr = row7_prev.copy()
    curr_data.append(row7_curr)

    df_prev = pd.DataFrame(prev_data)
    df_curr = pd.DataFrame(curr_data)

    # Test RAW processor
    print("\n" + "="*70)
    print("TEST 1: RAW PROCESSOR")
    print("="*70)
    lookups = build_lookup_dictionaries(df_prev)
    df_result, counter, _, _ = process_raw_comparison(df_curr, df_prev, *lookups)

    print("\nDetected changes:")
    for change_type, count in sorted(counter.items()):
        print(f"  {change_type}: {count}")

    # Verify results
    results = {}
    for idx, row in df_result.iterrows():
        seq = row["SequenceName"]
        changes = row["CHANGES"]
        results[seq] = changes
        print(f"  {seq}: {changes}")

    # Assertions for RAW
    errors = []
    if results.get("Seq1") != "TimeFrame Change":
        errors.append(f"RAW: Row 1 expected 'TimeFrame Change', got '{results.get('Seq1')}'")
    if results.get("Seq2") != "Desc Change":
        errors.append(f"RAW: Row 2 expected 'Desc Change', got '{results.get('Seq2')}'")
    if results.get("Seq3") != "DialogType Change":
        errors.append(f"RAW: Row 3 expected 'DialogType Change', got '{results.get('Seq3')}'")
    if results.get("Seq4") != "Group Change":
        errors.append(f"RAW: Row 4 expected 'Group Change', got '{results.get('Seq4')}'")
    if results.get("Seq5") != "Character Group Change":
        errors.append(f"RAW: Row 5 expected 'Character Group Change', got '{results.get('Seq5')}'")
    if "TimeFrame" not in results.get("Seq6", "") or "Desc" not in results.get("Seq6", ""):
        errors.append(f"RAW: Row 6 expected 'TimeFrame+Desc Change', got '{results.get('Seq6')}'")
    if results.get("Seq7") != "No Change":
        errors.append(f"RAW: Row 7 expected 'No Change', got '{results.get('Seq7')}'")

    if errors:
        print("\n❌ RAW PROCESSOR FAILURES:")
        for error in errors:
            print(f"  {error}")
    else:
        print("\n✓ RAW PROCESSOR: ALL STANDALONE CHANGES DETECTED")

    # Test WORKING processor
    print("\n" + "="*70)
    print("TEST 2: WORKING PROCESSOR")
    print("="*70)
    lookups_working = build_working_lookup_dictionaries(df_prev)
    df_result_w, counter_w, _, _, _ = process_working_comparison(df_curr, df_prev, *lookups_working)

    print("\nDetected changes:")
    for change_type, count in sorted(counter_w.items()):
        print(f"  {change_type}: {count}")

    # Verify results
    results_w = {}
    for idx, row in df_result_w.iterrows():
        seq = row["SequenceName"]
        changes = row["CHANGES"]
        results_w[seq] = changes
        print(f"  {seq}: {changes}")

    # Assertions for WORKING
    errors_w = []
    if results_w.get("Seq1") != "TimeFrame Change":
        errors_w.append(f"WORKING: Row 1 expected 'TimeFrame Change', got '{results_w.get('Seq1')}'")
    if results_w.get("Seq2") != "Desc Change":
        errors_w.append(f"WORKING: Row 2 expected 'Desc Change', got '{results_w.get('Seq2')}'")
    if results_w.get("Seq3") != "DialogType Change":
        errors_w.append(f"WORKING: Row 3 expected 'DialogType Change', got '{results_w.get('Seq3')}'")
    if results_w.get("Seq4") != "Group Change":
        errors_w.append(f"WORKING: Row 4 expected 'Group Change', got '{results_w.get('Seq4')}'")
    if results_w.get("Seq5") != "Character Group Change":
        errors_w.append(f"WORKING: Row 5 expected 'Character Group Change', got '{results_w.get('Seq5')}'")
    if "TimeFrame" not in results_w.get("Seq6", "") or "Desc" not in results_w.get("Seq6", ""):
        errors_w.append(f"WORKING: Row 6 expected 'TimeFrame+Desc Change', got '{results_w.get('Seq6')}'")
    if results_w.get("Seq7") != "No Change":
        errors_w.append(f"WORKING: Row 7 expected 'No Change', got '{results_w.get('Seq7')}'")

    if errors_w:
        print("\n❌ WORKING PROCESSOR FAILURES:")
        for error in errors_w:
            print(f"  {error}")
    else:
        print("\n✓ WORKING PROCESSOR: ALL STANDALONE CHANGES DETECTED")

    # Final report
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)

    total_errors = len(errors) + len(errors_w)
    if total_errors == 0:
        print("✓ ALL TESTS PASSED")
        print("✓ Standalone changes: DETECTED")
        print("✓ Composite changes: DETECTED")
        return True
    else:
        print(f"❌ {total_errors} TESTS FAILED")
        print("\nAll errors:")
        for error in errors + errors_w:
            print(f"  {error}")
        return False


if __name__ == "__main__":
    success = test_standalone_changes()
    exit(0 if success else 1)
