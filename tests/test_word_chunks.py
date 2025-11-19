#!/usr/bin/env python3
"""
Demonstrate word-level chunking (like WinMerge)
Shows how consecutive changed words are automatically grouped
"""

from difflib import SequenceMatcher

def extract_diff_word_level(text1, text2):
    """Word-level diff with automatic chunking"""
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

# Test cases showing chunking behavior
test_cases = [
    ("Single word changed",
     "플레이어가 적을 물리쳤습니다",
     "플레이어가 보스를 물리쳤습니다"),

    ("Two consecutive words changed",
     "새로운 게임을 시작하세요",
     "저장된 파일을 시작하세요"),

    ("Three consecutive words changed",
     "플레이어가 적을 빠르게 물리쳤습니다",
     "플레이어가 보스를 천천히 공격했습니다"),

    ("Beginning chunk changed",
     "새로운 게임을 시작하시겠습니까?",
     "저장된 데이터를 시작하시겠습니까?"),

    ("End chunk changed",
     "게임을 시작하시겠습니까?",
     "게임을 불러오시겠어요?"),

    ("Multiple separate chunks",
     "플레이어가 적을 물리치고 승리했습니다",
     "적이 플레이어를 공격하고 패배했습니다"),

    ("Almost entire sentence (keeps only middle)",
     "The player won the game",
     "The enemy lost the battle"),

    ("Korean - half sentence chunk",
     "플레이어가 최종 보스를 물리쳤습니다",
     "플레이어가 일반 적을 물리쳤습니다"),
]

print("=" * 90)
print("WORD-LEVEL CHUNKING DEMONSTRATION (Like WinMerge)")
print("=" * 90)
print("\nConsecutive changed words are automatically grouped into chunks!\n")

for description, prev, curr in test_cases:
    diff = extract_diff_word_level(prev, curr)
    chunk_count = diff.count('[')

    print(f"{description}:")
    print(f"  Previous: {prev}")
    print(f"  Current:  {curr}")
    print(f"  Diff:     {diff}")
    print(f"  Chunks:   {chunk_count}")
    print("-" * 90)

print("\n" + "=" * 90)
print("KEY INSIGHT:")
print("=" * 90)
print("When consecutive words change, they're shown as ONE chunk: [old words→new words]")
print("This is exactly how WinMerge groups changes together!")
print("No separate 'chunk level' needed - word-level already does it! ✓")
print("=" * 90)
