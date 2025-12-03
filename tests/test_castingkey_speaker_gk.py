"""
Test CastingKey generation with Speaker|CharacterGroupKey from CURRENT only.

Phase 4.5.3: Speaker|CharacterGroupKey is read ONLY from CURRENT file
and used to generate CastingKey for BOTH PREVIOUS and CURRENT rows.

This test verifies:
1. PREVIOUS file can be missing Speaker|CharacterGroupKey
2. CURRENT file must have Speaker|CharacterGroupKey
3. CastingKey generation uses CURRENT's Speaker|CharacterGroupKey for BOTH files
4. Validation passes when PREVIOUS lacks Speaker|CharacterGroupKey
"""

import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.casting import generate_casting_key, validate_castingkey_columns
from src.utils.helpers import safe_str


def test_validation_previous_without_speaker_gk():
    """PREVIOUS should pass validation even without Speaker|CharacterGroupKey."""
    df_prev = pd.DataFrame({
        'CharacterKey': ['CharA'],
        'DialogVoice': ['Voice1'],
        'DialogType': ['normal'],
        # NO Speaker|CharacterGroupKey!
    })

    valid, missing = validate_castingkey_columns(df_prev, "PREVIOUS", is_current=False)
    assert valid == True, f"PREVIOUS should be valid without Speaker|CharacterGroupKey, but missing: {missing}"
    assert missing == [], f"Should have no missing columns, got: {missing}"
    print("✓ test_validation_previous_without_speaker_gk")


def test_validation_current_requires_speaker_gk():
    """CURRENT should fail validation without Speaker|CharacterGroupKey."""
    df_curr = pd.DataFrame({
        'CharacterKey': ['CharA'],
        'DialogVoice': ['Voice1'],
        'DialogType': ['normal'],
        # NO Speaker|CharacterGroupKey!
    })

    valid, missing = validate_castingkey_columns(df_curr, "CURRENT", is_current=True)
    assert valid == False, "CURRENT should fail without Speaker|CharacterGroupKey"
    assert "Speaker|CharacterGroupKey" in missing, f"Should be missing Speaker|CharacterGroupKey, got: {missing}"
    print("✓ test_validation_current_requires_speaker_gk")


def test_validation_current_with_speaker_gk():
    """CURRENT should pass validation with Speaker|CharacterGroupKey."""
    df_curr = pd.DataFrame({
        'CharacterKey': ['CharA'],
        'DialogVoice': ['Voice1'],
        'DialogType': ['normal'],
        'Speaker|CharacterGroupKey': ['GroupX'],
    })

    valid, missing = validate_castingkey_columns(df_curr, "CURRENT", is_current=True)
    assert valid == True, f"CURRENT should be valid with all columns, but missing: {missing}"
    assert missing == [], f"Should have no missing columns, got: {missing}"
    print("✓ test_validation_current_with_speaker_gk")


def test_castingkey_same_for_both_files():
    """CastingKey should be identical for PREV and CURR when using CURR's Speaker|CharacterGroupKey."""

    # CURRENT has Speaker|CharacterGroupKey
    df_curr = pd.DataFrame({
        'SequenceName': ['Seq1', 'Seq2', 'Seq3'],
        'EventName': ['Event1', 'Event2', 'Event3'],
        'CharacterKey': ['CharA', 'CharB', 'CharC'],
        'DialogVoice': ['', '', ''],
        'Speaker|CharacterGroupKey': ['CharA_Group', 'CharB_Group', 'CharC_Group'],
        'DialogType': ['normal', 'normal', 'normal'],
    })

    # PREVIOUS does NOT have Speaker|CharacterGroupKey
    df_prev = pd.DataFrame({
        'SequenceName': ['Seq1', 'Seq2', 'Seq3'],
        'EventName': ['Event1', 'Event2', 'Event3'],
        'CharacterKey': ['CharA', 'CharB', 'CharC'],
        'DialogVoice': ['', '', ''],
        'DialogType': ['normal', 'normal', 'normal'],
    })

    # Build lookup from CURRENT
    speaker_gk_lookup = {}
    for idx, row in df_curr.iterrows():
        key = (safe_str(row.get('SequenceName', '')), safe_str(row.get('EventName', '')))
        speaker_gk_lookup[key] = safe_str(row.get('Speaker|CharacterGroupKey', ''))

    # Generate CastingKey for PREVIOUS using CURRENT's Speaker|CharacterGroupKey
    ck_prev = []
    for idx, row in df_prev.iterrows():
        key = (safe_str(row.get('SequenceName', '')), safe_str(row.get('EventName', '')))
        speaker_gk = speaker_gk_lookup.get(key, '')
        ck = generate_casting_key(
            row.get('CharacterKey', ''),
            row.get('DialogVoice', ''),
            speaker_gk,
            row.get('DialogType', '')
        )
        ck_prev.append(ck)

    # Generate CastingKey for CURRENT using its own Speaker|CharacterGroupKey
    ck_curr = []
    for idx, row in df_curr.iterrows():
        ck = generate_casting_key(
            row.get('CharacterKey', ''),
            row.get('DialogVoice', ''),
            row.get('Speaker|CharacterGroupKey', ''),
            row.get('DialogType', '')
        )
        ck_curr.append(ck)

    # They should match!
    for i in range(len(ck_prev)):
        assert ck_prev[i] == ck_curr[i], f"Row {i}: PREV={ck_prev[i]} != CURR={ck_curr[i]}"

    print("✓ test_castingkey_same_for_both_files")


def test_castingkey_lowercase():
    """All CastingKey values should be lowercase."""
    test_cases = [
        ('CHARA', '', '', 'normal', 'chara'),
        ('CharB', 'Unique_Voice', '', 'normal', 'unique_voice'),
        ('', 'MYVOICE', '', 'aidialog', 'myvoice'),
        ('ABC', '', 'ABC_Group', 'normal', 'abc_group'),
    ]

    for char_key, dialog_v, speaker_gk, dialog_type, expected in test_cases:
        result = generate_casting_key(char_key, dialog_v, speaker_gk, dialog_type)
        assert result == expected, f"Expected {expected}, got {result}"
        assert result == result.lower(), f"CastingKey should be lowercase: {result}"

    print("✓ test_castingkey_lowercase")


def test_previous_row_not_in_current():
    """PREVIOUS row without match in CURRENT should use empty Speaker|CharacterGroupKey."""

    # CURRENT has only Seq1
    df_curr = pd.DataFrame({
        'SequenceName': ['Seq1'],
        'EventName': ['Event1'],
        'CharacterKey': ['CharA'],
        'DialogVoice': [''],
        'Speaker|CharacterGroupKey': ['GroupX'],
        'DialogType': ['normal'],
    })

    # PREVIOUS has Seq1 and Seq2 (Seq2 not in CURRENT)
    df_prev = pd.DataFrame({
        'SequenceName': ['Seq1', 'Seq2'],
        'EventName': ['Event1', 'Event2'],
        'CharacterKey': ['CharA', 'CharB'],
        'DialogVoice': ['', ''],
        'DialogType': ['normal', 'normal'],
    })

    # Build lookup from CURRENT
    speaker_gk_lookup = {}
    for idx, row in df_curr.iterrows():
        key = (safe_str(row.get('SequenceName', '')), safe_str(row.get('EventName', '')))
        speaker_gk_lookup[key] = safe_str(row.get('Speaker|CharacterGroupKey', ''))

    # Generate CastingKey for PREVIOUS
    for idx, row in df_prev.iterrows():
        key = (safe_str(row.get('SequenceName', '')), safe_str(row.get('EventName', '')))
        speaker_gk = speaker_gk_lookup.get(key, '')  # Empty if not found
        ck = generate_casting_key(
            row.get('CharacterKey', ''),
            row.get('DialogVoice', ''),
            speaker_gk,
            row.get('DialogType', '')
        )

        if idx == 0:  # Seq1 - found in CURRENT
            assert speaker_gk == 'GroupX', f"Seq1 should have GroupX, got: {speaker_gk}"
        else:  # Seq2 - NOT found in CURRENT
            assert speaker_gk == '', f"Seq2 should have empty speaker_gk, got: {speaker_gk}"
            # Should still generate CastingKey using CharacterKey
            assert ck == 'charb', f"Should fallback to CharacterKey, got: {ck}"

    print("✓ test_previous_row_not_in_current")


if __name__ == "__main__":
    print("="*70)
    print("CastingKey Speaker|CharacterGroupKey Tests (Phase 4.5.3)")
    print("="*70)
    print()

    test_validation_previous_without_speaker_gk()
    test_validation_current_requires_speaker_gk()
    test_validation_current_with_speaker_gk()
    test_castingkey_same_for_both_files()
    test_castingkey_lowercase()
    test_previous_row_not_in_current()

    print()
    print("="*70)
    print("ALL TESTS PASSED!")
    print("="*70)
