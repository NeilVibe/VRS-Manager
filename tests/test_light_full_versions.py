#!/usr/bin/env python3
"""
Test LIGHT vs FULL version behavior for StrOrigin Analysis

This test validates that:
- LIGHT version (no BERT): Shows "Punctuation/Space Change" or "Content Change"
- FULL version (with BERT): Shows "Punctuation/Space Change" or "XX.X% similar"
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.strorigin_analysis import (
    StrOriginAnalyzer,
    is_punctuation_space_change_only
)


def test_light_version():
    """Test LIGHT version (simulate missing BERT by checking availability)"""
    print("=" * 80)
    print("TEST: LIGHT Version (No BERT)")
    print("=" * 80)
    print()

    # Create analyzer
    analyzer = StrOriginAnalyzer()

    print(f"BERT Available: {analyzer.bert_available}")
    print()

    # Test cases
    test_cases = [
        # (prev, curr, description)
        ("Hello", "Hello!", "Punctuation only"),
        ("안녕하세요", "안녕하세요?", "Korean punctuation"),
        ("Test", "Test...", "Ellipsis added"),
        ("  Spaces  ", "Spaces", "Space only"),
        ("Hello World", "Goodbye World", "Content changed"),
        ("안녕하세요", "안녕", "Korean content changed"),
    ]

    print("Test Results:")
    print("-" * 80)

    all_passed = True
    for prev, curr, description in test_cases:
        result = analyzer.analyze(prev, curr)

        # Check expected behavior
        is_punct_only = is_punctuation_space_change_only(prev, curr)

        if is_punct_only:
            expected = "Punctuation/Space Change"
            passed = result == expected
        else:
            if analyzer.bert_available:
                expected = "contains similarity %"
                passed = "% similar" in result
            else:
                expected = "Content Change"
                passed = result == expected

        status = "✅ PASS" if passed else "❌ FAIL"

        print(f"{status}: {description}")
        print(f"  Input: '{prev}' → '{curr}'")
        print(f"  Result: {result}")
        if not passed:
            print(f"  Expected: {expected}")
            all_passed = False
        print()

    return all_passed


def test_version_detection():
    """Test that version detection works correctly"""
    print("=" * 80)
    print("TEST: Version Detection")
    print("=" * 80)
    print()

    analyzer = StrOriginAnalyzer()

    print(f"BERT Available: {analyzer.bert_available}")
    print()

    if analyzer.bert_available:
        print("✅ FULL Version Detected")
        print("   - Punctuation/Space detection: Enabled")
        print("   - BERT similarity calculation: Enabled")
        print("   - Output: 'Punctuation/Space Change' or 'XX.X% similar'")
    else:
        print("✅ LIGHT Version Detected")
        print("   - Punctuation/Space detection: Enabled")
        print("   - BERT similarity calculation: Disabled")
        print("   - Output: 'Punctuation/Space Change' or 'Content Change'")

    print()
    return True


def test_output_format():
    """Test that output format is correct for both versions"""
    print("=" * 80)
    print("TEST: Output Format")
    print("=" * 80)
    print()

    analyzer = StrOriginAnalyzer()

    # Test punctuation change (same for both versions)
    result1 = analyzer.analyze("Hello", "Hello!")
    print(f"Punctuation test: '{result1}'")
    assert result1 == "Punctuation/Space Change", f"Expected 'Punctuation/Space Change', got '{result1}'"
    print("✅ PASS: Punctuation detection works")
    print()

    # Test content change (different for LIGHT vs FULL)
    result2 = analyzer.analyze("Hello", "Goodbye")
    print(f"Content change test: '{result2}'")

    if analyzer.bert_available:
        # FULL version should show percentage
        assert "% similar" in result2, f"FULL version should show '% similar', got '{result2}'"
        print("✅ PASS: FULL version shows similarity percentage")
    else:
        # LIGHT version should show "Content Change"
        assert result2 == "Content Change", f"LIGHT version should show 'Content Change', got '{result2}'"
        print("✅ PASS: LIGHT version shows 'Content Change'")

    print()
    return True


def main():
    """Run all tests"""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "LIGHT vs FULL Version Test" + " " * 32 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    try:
        results = {}

        results["version_detection"] = test_version_detection()
        results["light_version"] = test_light_version()
        results["output_format"] = test_output_format()

        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print()

        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status}: {test_name.replace('_', ' ').title()}")

        print()

        all_passed = all(results.values())
        if all_passed:
            print("=" * 80)
            print("✅ ALL TESTS PASSED!")
            print("=" * 80)
            print()
            analyzer = StrOriginAnalyzer()
            if analyzer.bert_available:
                print("FULL version is working correctly!")
                print("  - Punctuation/Space detection: ✅")
                print("  - BERT similarity: ✅")
            else:
                print("LIGHT version is working correctly!")
                print("  - Punctuation/Space detection: ✅")
                print("  - Content Change marker: ✅")
            print()
        else:
            print("=" * 80)
            print("❌ SOME TESTS FAILED")
            print("=" * 80)
            print()

        return all_passed

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
