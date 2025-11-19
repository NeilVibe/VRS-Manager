#!/usr/bin/env python3
"""
Test different diff granularities: character-level vs word-level
"""

from difflib import SequenceMatcher

def extract_diff_character_level(text1, text2):
    """Character-by-character (current implementation)"""
    matcher = SequenceMatcher(None, text1, text2)
    changes = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            changes.append(f"[{text1[i1:i2]}→{text2[j1:j2]}]")
        elif tag == 'delete':
            changes.append(f"[-{text1[i1:i2]}]")
        elif tag == 'insert':
            changes.append(f"[+{text2[j1:j2]}]")

    return ' '.join(changes) if changes else ""

def extract_diff_word_level(text1, text2):
    """Word-by-word (alternative)"""
    words1 = text1.split()
    words2 = text2.split()

    matcher = SequenceMatcher(None, words1, words2)
    changes = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            old_words = ' '.join(words1[i1:i2])
            new_words = ' '.join(words2[j1:j2])
            changes.append(f"[{old_words}→{new_words}]")
        elif tag == 'delete':
            deleted = ' '.join(words1[i1:i2])
            changes.append(f"[-{deleted}]")
        elif tag == 'insert':
            added = ' '.join(words2[j1:j2])
            changes.append(f"[+{added}]")

    return ' '.join(changes) if changes else ""

# Test cases
test_cases = [
    ("Hello", "Hallo"),
    ("Press any button", "Press button"),
    ("The player won the game", "The player lost the match"),
    ("Welcome back home", "Welcome home"),
    ("안녕하세요", "안녕하십니까"),
]

print("=" * 70)
print("CHARACTER-LEVEL vs WORD-LEVEL DIFF COMPARISON")
print("=" * 70)

for prev, curr in test_cases:
    char_diff = extract_diff_character_level(prev, curr)
    word_diff = extract_diff_word_level(prev, curr)

    print(f"\nPrevious: {prev}")
    print(f"Current:  {curr}")
    print(f"Char-level: {char_diff}")
    print(f"Word-level: {word_diff}")
    print("-" * 70)
