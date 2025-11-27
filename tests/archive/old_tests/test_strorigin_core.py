#!/usr/bin/env python3
"""
Core test for Phase 2.3 - StrOrigin Analysis Module

Tests the core analysis functionality without GUI dependencies.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.strorigin_analysis import (
    normalize_text_for_comparison,
    is_punctuation_space_change_only,
    StrOriginAnalyzer
)


def test_normalization():
    """Test text normalization function"""
    print("=" * 80)
    print("TEST 1: Text Normalization")
    print("=" * 80)
    print()

    test_cases = [
        ("Hello, World!", "helloworld"),
        ("안녕하세요!", "안녕하세요"),
        ("Test  with   spaces", "testwithspaces"),
        ("Punctuation... Test!!!", "punctuationtest"),
        ("한글 텍스트... 테스트!", "한글텍스트테스트"),
    ]

    all_passed = True
    for input_text, expected in test_cases:
        result = normalize_text_for_comparison(input_text)
        passed = result == expected
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: '{input_text}' → '{result}'")
        if not passed:
            print(f"         Expected: '{expected}'")
            all_passed = False

    print()
    return all_passed


def test_punctuation_detection():
    """Test punctuation/space-only change detection"""
    print("=" * 80)
    print("TEST 2: Punctuation/Space Detection")
    print("=" * 80)
    print()

    test_cases = [
        # (prev, curr, should_be_punctuation_only)
        ("Hello", "Hello!", True),
        ("Hello", "Hello?", True),
        ("안녕하세요", "안녕하세요!", True),
        ("Test", "Test...", True),
        ("  Hello  ", "Hello", True),  # Space difference
        ("Hello", "Goodbye", False),  # Different text
        ("안녕하세요", "안녕", False),  # Different content
        ("Test 123", "Test 456", False),  # Different numbers
    ]

    all_passed = True
    for prev, curr, expected in test_cases:
        result = is_punctuation_space_change_only(prev, curr)
        passed = result == expected
        status = "✅ PASS" if passed else "❌ FAIL"
        result_str = "Punctuation/Space Only" if result else "Content Changed"
        expected_str = "Punctuation/Space Only" if expected else "Content Changed"
        print(f"{status}: '{prev}' → '{curr}'")
        print(f"         Result: {result_str}")
        if not passed:
            print(f"         Expected: {expected_str}")
            all_passed = False
        print()

    return all_passed


def test_bert_similarity():
    """Test BERT semantic similarity"""
    print("=" * 80)
    print("TEST 3: BERT Semantic Similarity")
    print("=" * 80)
    print()

    analyzer = StrOriginAnalyzer()

    test_cases = [
        # (text1, text2, description)
        ("안녕하세요", "안녕하세요", "Identical text"),
        ("안녕하세요", "안녕", "Similar greeting"),
        ("Hello", "Hi", "Similar English"),
        ("안녕하세요", "Goodbye", "Completely different"),
        ("반갑습니다", "안녕하세요", "Different Korean greetings"),
    ]

    print("Testing semantic similarity calculations...")
    print()

    all_passed = True
    for text1, text2, description in test_cases:
        # Calculate directly
        from src.utils.strorigin_analysis import calculate_semantic_similarity
        similarity = calculate_semantic_similarity(text1, text2, analyzer.model if analyzer.model else analyzer._load_model() or analyzer.model)

        similarity_pct = similarity * 100
        print(f"✅ {description}")
        print(f"   '{text1}' vs '{text2}'")
        print(f"   Similarity: {similarity_pct:.1f}%")
        print()

        # Basic sanity checks
        if text1 == text2 and similarity < 0.95:
            print(f"   ⚠️  WARNING: Identical texts should have >95% similarity")
            all_passed = False

    return all_passed


def test_analyzer_integration():
    """Test StrOriginAnalyzer full pipeline"""
    print("=" * 80)
    print("TEST 4: StrOriginAnalyzer Integration")
    print("=" * 80)
    print()

    analyzer = StrOriginAnalyzer()

    test_cases = [
        # (prev, curr, expected_result_type)
        ("Hello", "Hello!", "Punctuation/Space Change"),
        ("안녕하세요", "안녕하세요?", "Punctuation/Space Change"),
        ("Hello", "Hi there", "% similar"),
        ("안녕하세요", "안녕", "% similar"),
        ("Test", "Completely different text", "% similar"),
    ]

    print("Testing full analysis pipeline...")
    print()

    all_passed = True
    for prev, curr, expected_type in test_cases:
        result = analyzer.analyze(prev, curr)

        if expected_type == "Punctuation/Space Change":
            passed = result == "Punctuation/Space Change"
        else:  # "% similar"
            passed = "% similar" in result

        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: '{prev}' → '{curr}'")
        print(f"         Result: {result}")
        if not passed:
            print(f"         Expected type: {expected_type}")
            all_passed = False
        print()

    return all_passed


def test_batch_analysis():
    """Test batch processing"""
    print("=" * 80)
    print("TEST 5: Batch Analysis")
    print("=" * 80)
    print()

    analyzer = StrOriginAnalyzer()

    text_pairs = [
        ("Hello", "Hello!"),
        ("안녕하세요", "안녕"),
        ("Test", "Test..."),
        ("Different", "Text"),
    ]

    print(f"Processing {len(text_pairs)} text pairs in batch...")
    print()

    results = analyzer.analyze_batch(text_pairs)

    print("Results:")
    for i, ((prev, curr), result) in enumerate(zip(text_pairs, results)):
        print(f"  {i+1}. '{prev}' → '{curr}' : {result}")

    print()
    print(f"✅ Batch processing completed: {len(results)} results")
    print()

    return len(results) == len(text_pairs)


def main():
    """Run all tests"""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 10 + "PHASE 2.3 - StrOrigin Analysis Core Module Test" + " " * 19 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    results = {}

    try:
        results["normalization"] = test_normalization()
        results["punctuation_detection"] = test_punctuation_detection()
        results["bert_similarity"] = test_bert_similarity()
        results["analyzer_integration"] = test_analyzer_integration()
        results["batch_analysis"] = test_batch_analysis()

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
            print("✅ ALL CORE TESTS PASSED!")
            print("=" * 80)
            print()
            print("Phase 2.3 core module is working correctly!")
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
