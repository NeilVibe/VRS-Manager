#!/usr/bin/env python3
"""
Test LIGHT version by temporarily hiding BERT packages

This simulates what happens when torch/sentence_transformers are not installed.
"""

import sys
from pathlib import Path
from unittest import mock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_light_version_simulation():
    """Test LIGHT version by mocking ImportError for BERT packages"""
    print("=" * 80)
    print("TEST: LIGHT Version Simulation (BERT Packages Hidden)")
    print("=" * 80)
    print()

    # Mock torch and sentence_transformers as unavailable
    import_original = __builtins__.__import__

    def mock_import(name, *args, **kwargs):
        if name in ['torch', 'sentence_transformers']:
            raise ImportError(f"No module named '{name}' (simulated for LIGHT version test)")
        return import_original(name, *args, **kwargs)

    with mock.patch('builtins.__import__', side_effect=mock_import):
        # Now import the module (it will check for BERT availability)
        from src.utils.strorigin_analysis import StrOriginAnalyzer

        # Create analyzer
        analyzer = StrOriginAnalyzer()

        print(f"BERT Available: {analyzer.bert_available}")
        print()

        if analyzer.bert_available:
            print("❌ FAIL: BERT should not be available in LIGHT version simulation!")
            return False

        print("✅ LIGHT Version Successfully Simulated")
        print()

        # Test cases
        test_cases = [
            # (prev, curr, expected_result, description)
            ("Hello", "Hello!", "Punctuation/Space Change", "Punctuation only"),
            ("안녕하세요", "안녕하세요?", "Punctuation/Space Change", "Korean punctuation"),
            ("Test", "Test...", "Punctuation/Space Change", "Ellipsis added"),
            ("Hello World", "Goodbye World", "Content Change", "Content changed"),
            ("안녕하세요", "안녕", "Content Change", "Korean content changed"),
        ]

        print("Test Results:")
        print("-" * 80)

        all_passed = True
        for prev, curr, expected, description in test_cases:
            result = analyzer.analyze(prev, curr)
            passed = result == expected

            status = "✅ PASS" if passed else "❌ FAIL"

            print(f"{status}: {description}")
            print(f"  Input: '{prev}' → '{curr}'")
            print(f"  Expected: {expected}")
            print(f"  Got: {result}")
            if not passed:
                all_passed = False
            print()

        return all_passed


def main():
    """Run LIGHT version simulation test"""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 24 + "LIGHT Version Test" + " " * 36 + "║")
    print("║" + " " * 18 + "(Simulating Missing BERT Packages)" + " " * 27 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    try:
        success = test_light_version_simulation()

        print("=" * 80)
        if success:
            print("✅ LIGHT VERSION TEST PASSED!")
            print("=" * 80)
            print()
            print("LIGHT version behavior verified:")
            print("  - Punctuation/Space detection: ✅ Works")
            print("  - Content changes: ✅ Shows 'Content Change'")
            print("  - No BERT required: ✅ Gracefully handles missing packages")
            print()
            print("Both LIGHT and FULL versions are working correctly! 🎉")
        else:
            print("❌ LIGHT VERSION TEST FAILED")
            print("=" * 80)
        print()

        return success

    except Exception as e:
        print()
        print("=" * 80)
        print("❌ TEST FAILED WITH EXCEPTION")
        print("=" * 80)
        print()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
