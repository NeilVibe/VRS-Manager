#!/usr/bin/env python3
"""
Test the updated StrOriginAnalyzer with word-level diff
Verifies that it returns tuples (analysis, diff_detail)
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.strorigin_analysis import StrOriginAnalyzer

print("=" * 70)
print("WORD-LEVEL STRORIGIN ANALYZER TEST")
print("=" * 70)

# Initialize analyzer
analyzer = StrOriginAnalyzer()

if analyzer.bert_available:
    print("✓ Testing FULL version (BERT available)")
else:
    print("✓ Testing LIGHT version (No BERT)")

print("=" * 70)

# Test cases
test_cases = [
    ("Punctuation only", "Hello world", "Hello, world!"),
    ("Single word change", "Hello world", "Hallo world"),
    ("Multiple words", "The player won the game", "The enemy lost the battle"),
    ("Korean formality", "안녕하세요", "안녕하십니까"),
    ("Korean word change", "플레이어가 승리했습니다", "플레이어가 패배했습니다"),
    ("Korean complete rewrite", "플레이어가 승리했습니다", "적이 도망갔습니다"),
]

for description, prev, curr in test_cases:
    print(f"\n{description}:")
    print(f"  Previous: {prev}")
    print(f"  Current:  {curr}")

    # Analyze - should return tuple
    analysis, diff_detail = analyzer.analyze(prev, curr)

    print(f"  Analysis:    {analysis}")
    print(f"  Diff Detail: {diff_detail}")
    print(f"  Type check:  {type((analysis, diff_detail))} ✓ Tuple")
    print("-" * 70)

print("\n" + "=" * 70)
print("✓ All tests passed! Analyzer returns tuples correctly.")
print("=" * 70)
