#!/usr/bin/env python3
"""
Quick test of the new diff highlighting feature
"""

from src.utils.strorigin_analysis import StrOriginAnalyzer, extract_differences

# Test the diff extraction function directly
print("=" * 60)
print("DIFF EXTRACTION TESTS (Character-level precision)")
print("=" * 60)

test_cases = [
    ("Hello", "Hallo", "Single character replacement"),
    ("Hello, world!", "Hello world", "Punctuation removal"),
    ("Press any button", "Press button", "Word deletion"),
    ("Loading", "Loading complete", "Word addition"),
    ("Welcome back", "Welcome home", "Word replacement"),
    ("안녕하세요", "안녕하십니까", "Korean formality change"),
    ("플레이어 승리", "플레이어 패배", "Korean word change"),
    ("The player won the game", "The player lost the match", "Multiple changes"),
]

for prev, curr, description in test_cases:
    diff = extract_differences(prev, curr)
    print(f"\n{description}:")
    print(f"  Previous: {prev}")
    print(f"  Current:  {curr}")
    print(f"  Diff:     {diff}")

# Test the full analyzer (LIGHT mode - no BERT)
print("\n" + "=" * 60)
print("FULL ANALYZER TESTS (LIGHT mode - no BERT)")
print("=" * 60)

analyzer = StrOriginAnalyzer()

test_cases_full = [
    ("Hello, world!", "Hello world"),
    ("Hello", "Hallo"),
    ("Press any button", "Press button"),
    ("안녕하세요", "안녕하십니까"),
]

for prev, curr in test_cases_full:
    result = analyzer.analyze(prev, curr)
    print(f"\nPrevious: {prev}")
    print(f"Current:  {curr}")
    print(f"Result:   {result}")

print("\n" + "=" * 60)
print("✓ Test complete!")
print("=" * 60)
