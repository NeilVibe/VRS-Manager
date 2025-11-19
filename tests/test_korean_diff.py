#!/usr/bin/env python3
"""
Korean-specific diff testing
Testing word-level vs character-level for Korean game strings
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
    """Word-by-word (space-separated)"""
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

# Korean test cases - realistic game strings
korean_test_cases = [
    ("Formality change", "안녕하세요", "안녕하십니까"),
    ("Verb tense", "게임을 시작합니다", "게임을 시작했습니다"),
    ("Word replacement", "플레이어가 승리했습니다", "플레이어가 패배했습니다"),
    ("Particle change", "게임을 시작하세요", "게임으로 시작하세요"),
    ("Complete rewrite", "플레이어가 승리했습니다", "적이 도망갔습니다"),
    ("Addition", "로딩 중", "로딩 중입니다"),
    ("Deletion", "게임을 시작합니다", "게임 시작합니다"),
    ("Half sentence", "플레이어가 적을 물리쳤습니다", "플레이어가 보스를 물리쳤습니다"),
    ("Multiple words", "새로운 게임을 시작하시겠습니까?", "저장된 게임을 불러오시겠습니까?"),
    ("Honorific change", "게임을 시작하세요", "게임을 시작하십시오"),
    ("Single char no space", "승리", "패배"),
    ("With spaces", "게임 시작", "게임 종료"),
    ("Long sentence small change", "플레이어가 최종 보스를 물리치고 게임을 클리어했습니다", "플레이어가 최종 보스를 물리치고 게임을 완료했습니다"),
    ("Menu item", "새 게임", "게임 불러오기"),
    ("Button text", "확인", "취소"),
]

print("=" * 90)
print("KOREAN DIFF TESTING - Character vs Word Level")
print("=" * 90)

for category, prev, curr in korean_test_cases:
    char_diff = extract_diff_character_level(prev, curr)
    word_diff = extract_diff_word_level(prev, curr)

    # Count brackets
    char_brackets = char_diff.count('[')
    word_brackets = word_diff.count('[')

    print(f"\n{category.upper()}:")
    print(f"  Previous:  {prev}")
    print(f"  Current:   {curr}")
    print(f"  Char-level ({char_brackets} changes): {char_diff}")
    print(f"  Word-level ({word_brackets} changes): {word_diff}")

    # Determine which is clearer
    if char_brackets == word_brackets:
        winner = "TIE"
    elif word_brackets < char_brackets:
        winner = "WORD ✓"
    else:
        winner = "CHAR ✓"

    print(f"  → Clearer: {winner}")
    print("-" * 90)

print("\n" + "=" * 90)
print("SUMMARY: Which method works better for Korean?")
print("=" * 90)
