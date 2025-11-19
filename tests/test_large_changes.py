#!/usr/bin/env python3
"""
Test diff output when large portions of sentence change
"""

from difflib import SequenceMatcher

def extract_diff_character_level(text1, text2):
    """Character-by-character"""
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
    """Word-by-word"""
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

# Test cases: Small vs Large changes
test_cases = [
    ("Small change", "Hello", "Hallo"),
    ("Half sentence changed", "The player won the game", "The enemy lost the battle"),
    ("Most of sentence changed", "Welcome back to the main menu", "Good luck in your next adventure"),
    ("Minor word swap", "Start new game", "Start game"),
    ("Complete rewrite", "Loading your profile", "Saving game data"),
    ("Korean minor", "게임을 시작합니다", "게임을 종료합니다"),
    ("Korean major", "플레이어가 승리했습니다", "적이 도망갔습니다"),
]

print("=" * 80)
print("SMALL vs LARGE CHANGES - Which diff method is clearer?")
print("=" * 80)

for category, prev, curr in test_cases:
    char_diff = extract_diff_character_level(prev, curr)
    word_diff = extract_diff_word_level(prev, curr)

    # Count number of brackets to show "noisiness"
    char_brackets = char_diff.count('[')
    word_brackets = word_diff.count('[')

    print(f"\n{category.upper()}:")
    print(f"  Previous: {prev}")
    print(f"  Current:  {curr}")
    print(f"  Char-level ({char_brackets} changes): {char_diff}")
    print(f"  Word-level ({word_brackets} changes): {word_diff}")
    print(f"  → Clearer: {'WORD' if word_brackets <= char_brackets else 'CHAR'}")
    print("-" * 80)
