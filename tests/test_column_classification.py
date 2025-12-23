"""
Test column classification system.

Tests the proper classification of columns into:
- MANDATORY: Always included, cannot disable
- VRS_CONDITIONAL: Used in change detection, always from CURRENT
- AUTO_GENERATED: Created by VRS logic, toggleable
- OPTIONAL: Extra metadata, toggleable
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import (
    MANDATORY_COLUMNS,
    VRS_CONDITIONAL_COLUMNS,
    AUTO_GENERATED_COLUMNS,
    OPTIONAL_COLUMNS,
    CHAR_GROUP_COLS
)


class TestColumnClassification(unittest.TestCase):
    """Test column classification correctness."""

    def test_mandatory_columns_exist(self):
        """MANDATORY columns should include core identification fields."""
        expected = [
            "SequenceName", "EventName", "StrOrigin", "CharacterKey",
            "CharacterName", "CastingKey", "DialogVoice", "Text",
            "STATUS", "CHANGES"
        ]
        self.assertEqual(set(MANDATORY_COLUMNS), set(expected))

    def test_vrs_conditional_includes_change_detection_columns(self):
        """VRS_CONDITIONAL should include columns used in change detection."""
        # These are checked in detect_field_changes() in change_detection.py
        expected_core = ["Desc", "DialogType", "Group", "StartFrame", "EndFrame"]
        for col in expected_core:
            self.assertIn(col, VRS_CONDITIONAL_COLUMNS,
                          f"{col} should be in VRS_CONDITIONAL_COLUMNS (used in change detection)")

    def test_vrs_conditional_includes_char_group_cols(self):
        """VRS_CONDITIONAL should include all character group columns."""
        for col in CHAR_GROUP_COLS:
            self.assertIn(col, VRS_CONDITIONAL_COLUMNS,
                          f"{col} should be in VRS_CONDITIONAL_COLUMNS (CHAR_GROUP_COLS)")

    def test_auto_generated_columns_exist(self):
        """AUTO_GENERATED columns should be comparison outputs."""
        expected = [
            "PreviousData", "PreviousText", "PreviousEventName",
            "DETAILED_CHANGES", "Previous StrOrigin", "Mainline Translation"
        ]
        self.assertEqual(set(AUTO_GENERATED_COLUMNS), set(expected))

    def test_optional_columns_not_in_vrs_logic(self):
        """OPTIONAL columns should NOT be used in VRS change detection."""
        # These columns should be truly optional metadata
        for col in OPTIONAL_COLUMNS:
            self.assertNotIn(col, VRS_CONDITIONAL_COLUMNS,
                             f"{col} is in OPTIONAL but should not be (it's in VRS_CONDITIONAL)")

    def test_no_column_overlap(self):
        """No column should appear in multiple categories."""
        all_columns = set()

        for col in MANDATORY_COLUMNS:
            self.assertNotIn(col, all_columns, f"{col} appears in multiple categories")
            all_columns.add(col)

        for col in VRS_CONDITIONAL_COLUMNS:
            self.assertNotIn(col, all_columns, f"{col} appears in multiple categories")
            all_columns.add(col)

        for col in AUTO_GENERATED_COLUMNS:
            self.assertNotIn(col, all_columns, f"{col} appears in multiple categories")
            all_columns.add(col)

        for col in OPTIONAL_COLUMNS:
            self.assertNotIn(col, all_columns, f"{col} appears in multiple categories")
            all_columns.add(col)

    def test_optional_only_extra_metadata(self):
        """OPTIONAL should only contain truly extra metadata columns."""
        expected_optional = [
            "FREEMEMO", "SubTimelineName", "UpdateTime",
            "HasAudio", "UseSubtitle", "Record", "isNew"
        ]
        self.assertEqual(set(OPTIONAL_COLUMNS), set(expected_optional),
                         "OPTIONAL_COLUMNS should only contain truly optional metadata")


class TestColumnCounts(unittest.TestCase):
    """Test expected column counts."""

    def test_mandatory_count(self):
        """MANDATORY should have 10 columns."""
        self.assertEqual(len(MANDATORY_COLUMNS), 10)

    def test_vrs_conditional_count(self):
        """VRS_CONDITIONAL should have 10 columns (5 core + 5 char group)."""
        self.assertEqual(len(VRS_CONDITIONAL_COLUMNS), 10)

    def test_auto_generated_count(self):
        """AUTO_GENERATED should have 6 columns."""
        self.assertEqual(len(AUTO_GENERATED_COLUMNS), 6)

    def test_optional_count(self):
        """OPTIONAL should have 7 columns."""
        self.assertEqual(len(OPTIONAL_COLUMNS), 7)


class TestDataProcessingInclusion(unittest.TestCase):
    """Test that data_processing.py properly includes columns."""

    def test_filter_includes_mandatory(self):
        """filter_output_columns should always include MANDATORY columns."""
        from src.utils.data_processing import filter_output_columns
        import pandas as pd

        # Create test DataFrame with all column types
        test_data = {col: ["test"] for col in MANDATORY_COLUMNS}
        df = pd.DataFrame(test_data)

        result = filter_output_columns(df, use_settings=True)

        for col in MANDATORY_COLUMNS:
            self.assertIn(col, result.columns,
                          f"MANDATORY column {col} should be in output")

    def test_filter_includes_vrs_conditional(self):
        """filter_output_columns should always include VRS_CONDITIONAL columns."""
        from src.utils.data_processing import filter_output_columns
        import pandas as pd

        # Create test DataFrame with VRS conditional columns
        test_data = {col: ["test"] for col in VRS_CONDITIONAL_COLUMNS}
        # Add mandatory columns too (required)
        for col in MANDATORY_COLUMNS:
            test_data[col] = ["test"]
        df = pd.DataFrame(test_data)

        result = filter_output_columns(df, use_settings=True)

        for col in VRS_CONDITIONAL_COLUMNS:
            self.assertIn(col, result.columns,
                          f"VRS_CONDITIONAL column {col} should be in output")


class TestSettingsIntegration(unittest.TestCase):
    """Test settings module integration."""

    def test_get_vrs_conditional_columns(self):
        """get_vrs_conditional_columns should return correct list."""
        from src.settings import get_vrs_conditional_columns

        result = get_vrs_conditional_columns()
        self.assertEqual(set(result), set(VRS_CONDITIONAL_COLUMNS))

    def test_vrs_conditional_not_in_optional_settings(self):
        """VRS_CONDITIONAL columns should not appear in optional settings."""
        from src.settings import set_selected_optional_columns, get_selected_optional_columns

        # Try to set VRS_CONDITIONAL columns as optional - they should be filtered out
        set_selected_optional_columns(VRS_CONDITIONAL_COLUMNS)
        result = get_selected_optional_columns()

        for col in VRS_CONDITIONAL_COLUMNS:
            self.assertNotIn(col, result,
                             f"VRS_CONDITIONAL column {col} should not be selectable as optional")


if __name__ == "__main__":
    print("=" * 70)
    print("COLUMN CLASSIFICATION TESTS")
    print("=" * 70)

    # Run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestColumnClassification))
    suite.addTests(loader.loadTestsFromTestCase(TestColumnCounts))
    suite.addTests(loader.loadTestsFromTestCase(TestDataProcessingInclusion))
    suite.addTests(loader.loadTestsFromTestCase(TestSettingsIntegration))

    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print(f"SUCCESS: All {result.testsRun} tests passed!")
    else:
        print(f"FAILED: {len(result.failures)} failures, {len(result.errors)} errors")
    print("=" * 70)
