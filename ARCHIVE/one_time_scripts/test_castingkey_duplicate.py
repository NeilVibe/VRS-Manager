#!/usr/bin/env python3
"""
Test if CastingKey can be duplicate.

Scenario: Same character speaking multiple times in different events.
Question: Will CastingKey be the same?
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.casting import generate_casting_key

print("="*80)
print("Testing CastingKey Duplication")
print("="*80)

# Scenario: Same character speaks 3 times in different events
print("\n📋 Scenario: Hero speaks 3 times with same voice/group/type:")
print()

rows = [
    {
        "CharacterKey": "Hero",
        "DialogVoice": "Main",
        "SpeakerGroupKey": "A",
        "DialogType": "Dialog",
        "EventName": "Event1000",
        "StrOrigin": "Hello"
    },
    {
        "CharacterKey": "Hero",
        "DialogVoice": "Main",
        "SpeakerGroupKey": "A",
        "DialogType": "Dialog",
        "EventName": "Event2000",
        "StrOrigin": "Goodbye"
    },
    {
        "CharacterKey": "Hero",
        "DialogVoice": "Main",
        "SpeakerGroupKey": "A",
        "DialogType": "Dialog",
        "EventName": "Event3000",
        "StrOrigin": "Thank you"
    }
]

castingkeys = []
for i, row in enumerate(rows):
    key = generate_casting_key(
        row["CharacterKey"],
        row["DialogVoice"],
        row["SpeakerGroupKey"],
        row["DialogType"]
    )
    castingkeys.append(key)
    print(f"Row {i+1}:")
    print(f"  Event:      {row['EventName']}")
    print(f"  StrOrigin:  '{row['StrOrigin']}'")
    print(f"  CastingKey: {key}")
    print()

print("="*80)
print("RESULT:")
print("="*80)

if len(set(castingkeys)) == 1:
    print("❌ CastingKey IS DUPLICATE!")
    print(f"   All 3 rows have CastingKey: '{castingkeys[0]}'")
    print()
    print("This means:")
    print("  - key_sc (Sequence + CastingKey) can match duplicates")
    print("  - key_ec (Event + CastingKey) can match duplicates")
    print("  - key_oc (StrOrigin + CastingKey) can match duplicates")
    print("  - key_sec (S + E + CastingKey) can match duplicates")
    print("  - key_soc (S + StrOrigin + C) can match duplicates")
    print("  - key_eoc (E + StrOrigin + C) can match duplicates")
    print()
    print("🚨 CRITICAL: We CANNOT use CastingKey for NEW/DELETED detection!")
    is_duplicate = True
else:
    print("✅ CastingKey is UNIQUE")
    print(f"   CastingKeys: {castingkeys}")
    is_duplicate = False

print("="*80)

# Conclusion
print("\n" + "="*80)
print("CONCLUSION:")
print("="*80)

if is_duplicate:
    print("For NEW/DELETED detection, we can ONLY use:")
    print("  ✅ key_se (Sequence + Event)")
    print()
    print("This is the ONLY combination that is GUARANTEED UNIQUE per row.")
    print()
    print("WHY:")
    print("  - Sequence: Structural position (unique)")
    print("  - Event: Unique event identifier (unique)")
    print("  - StrOrigin: Dialogue content (CAN BE DUPLICATE)")
    print("  - CastingKey: Character info (CAN BE DUPLICATE)")
    print()
    print("RECOMMENDATION:")
    print("  For NEW row: Check ONLY if key_se is missing")
    print("  For DELETED row: Check ONLY if key_se is missing")
    print("  For change detection: Use ALL 10 keys for pattern matching")
else:
    print("We can use combinations with CastingKey for NEW/DELETED detection.")

print("="*80)

sys.exit(0 if is_duplicate else 1)
