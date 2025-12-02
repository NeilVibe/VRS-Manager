"""
Comprehensive Change Detection Test - RAW & WORKING Processors
==============================================================
Version: v12021800
Created: 2025-11-28

PURPOSE:
    This test creates PREVIOUS/CURRENT Excel files with the TRUE VoiceRecordSheet structure,
    injects KNOWN changes at specific rows, then validates that the production code detects
    EXACTLY the expected change type at each row.

TOTAL TEST CASES: 518
    - No Change: 1
    - Standalone (9 types): 9
    - CharacterGroup variations (5 sub-fields): 5
    - Composites (2-9 fields): 502
    - New Row: 1

USES PRODUCTION CODE FROM:
    - src/core/comparison.py (RAW)
    - src/core/working_comparison.py (WORKING)
    - src/core/lookups.py
    - src/core/working_helpers.py
    - src/core/casting.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import OrderedDict, Counter
from itertools import combinations

# Production imports
from src.config import (
    COL_DIALOGTYPE, COL_GROUP, COL_SEQUENCE, COL_CHARACTERNAME,
    COL_CHARACTERKEY, COL_DIALOGVOICE, COL_CASTINGKEY, COL_STRORIGIN,
    COL_STATUS, COL_TEXT, COL_DESC, COL_FREEMEMO,
    COL_EVENTNAME, COL_STARTFRAME, COL_ENDFRAME,
    COL_PREVIOUSDATA, COL_SPEAKER_GROUPKEY, CHAR_GROUP_COLS
)
from src.io.excel_reader import safe_read_excel
from src.utils.data_processing import normalize_dataframe_status, remove_full_duplicates
from src.core.comparison import compare_rows, find_deleted_rows
from src.core.working_comparison import process_working_comparison
from src.core.lookups import build_lookups
from src.core.working_helpers import build_working_lookups, find_working_deleted_rows
from src.core.casting import generate_casting_key

# Character group column names
COL_TRIBE = "Tribe"
COL_AGE = "Age"
COL_GENDER = "Gender"
COL_JOB = "Job"
COL_REGION = "Region"

# Other columns
COL_SUBTIMELINE = "SubTimelineName"
COL_CHANGES = "CHANGES"
COL_UPDATETIME = "UpdateTime"


# =============================================================================
# TRUE STRUCTURE DEFINITION (from VoiceRecordSheet)
# =============================================================================

TRUE_COLUMNS = [
    'DialogType', 'Group', 'SequenceName', 'CharacterName', 'CharacterKey',
    'DialogVoice', 'CastingKey', 'StrOrigin', 'STATUS', 'Text', 'Desc',
    'FREEMEMO', 'SubTimelineName', 'CHANGES', 'EventName', 'StartFrame',
    'EndFrame', 'Tribe', 'Age', 'Gender', 'Job', 'Region', 'UpdateTime',
    'PreviousData', 'Mainline Translation', 'Speaker|CharacterGroupKey'
]


def create_base_row(row_index: int) -> Dict:
    """Create a base row with TRUE structure and Korean StrOrigin."""
    return {
        'DialogType': 'Sequencer',
        'Group': 'Main',
        'SequenceName': f'cd_seq_quest_main_{row_index:04d}.seqc',
        'CharacterName': '테스트캐릭터',
        'CharacterKey': f'test_char_{row_index:04d}',
        'DialogVoice': 'Test_Voice_Male',
        'CastingKey': '',  # Will be generated
        'StrOrigin': f'안녕하세요 테스트 대사입니다 번호 {row_index}',  # Korean text
        'STATUS': 'NEW',
        'Text': '',
        'Desc': f'Description for row {row_index}',
        'FREEMEMO': '',
        'SubTimelineName': 'SCENE_1',
        'CHANGES': '',
        'EventName': f'event_test_{row_index:04d}_dialogue_{row_index:05d}',
        'StartFrame': '100',
        'EndFrame': '200',
        'Tribe': '인간',
        'Age': 'Adult',
        'Gender': '남성',
        'Job': '전사',
        'Region': '파이웰 대륙',
        'UpdateTime': datetime.now().isoformat(),
        'PreviousData': '',
        'Mainline Translation': '',
        'Speaker|CharacterGroupKey': ''
    }


# =============================================================================
# CHANGE TYPE DEFINITIONS
# =============================================================================

STANDALONE_CHANGES = {
    'StrOrigin': lambda row, idx: {'StrOrigin': f'변경된 대사입니다 수정 번호 {idx}'},
    'EventName': lambda row, idx: {'EventName': f'modified_event_{idx:04d}_changed'},
    'SequenceName': lambda row, idx: {'SequenceName': f'cd_seq_modified_{idx:04d}.seqc'},
    'CastingKey': lambda row, idx: {
        'CharacterKey': f'different_char_{idx:04d}',
        'DialogVoice': 'Different_Voice_Female'
    },
    'TimeFrame': lambda row, idx: {'StartFrame': '500', 'EndFrame': '600'},
    'Desc': lambda row, idx: {'Desc': f'Modified description for row {idx}'},
    'DialogType': lambda row, idx: {'DialogType': 'Cinematic'},
    'Group': lambda row, idx: {'Group': 'Side'},
    'CharacterGroup': lambda row, idx: {'Gender': '여성'},
}

CHAR_GROUP_VARIATIONS = {
    'Gender': lambda row, idx: {'Gender': '여성'},
    'Age': lambda row, idx: {'Age': 'Child'},
    'Tribe': lambda row, idx: {'Tribe': '엘프'},
    'Job': lambda row, idx: {'Job': '마법사'},
    'Region': lambda row, idx: {'Region': '북부 설원'},
}

EXPECTED_STANDALONE_LABELS = {
    'StrOrigin': 'StrOrigin Change',
    'EventName': 'EventName Change',
    'SequenceName': 'SequenceName Change',
    'CastingKey': 'CastingKey Change',
    'TimeFrame': 'TimeFrame Change',
    'Desc': 'Desc Change',
    'DialogType': 'DialogType Change',
    'Group': 'Group Change',
    'CharacterGroup': 'CharacterGroup Change',  # Production uses "CharacterGroup" not "Character Group"
}


# =============================================================================
# COMPOSITE CHANGE COMBINATIONS
# =============================================================================

def get_all_composite_combinations(max_fields: int = 9) -> List[Tuple[str, ...]]:
    """Generate ALL 502 composite combinations (2-9 fields)."""
    fields = ['StrOrigin', 'EventName', 'SequenceName', 'CastingKey',
              'TimeFrame', 'Desc', 'DialogType', 'Group', 'CharacterGroup']

    all_combos = []
    for n in range(2, min(max_fields, len(fields)) + 1):
        for combo in combinations(fields, n):
            all_combos.append(combo)

    return all_combos


def build_expected_label(change_types: Tuple[str, ...]) -> str:
    """
    Build expected change label from change types.

    This must match EXACTLY what production code outputs.
    Production order (from src/core/change_detection.py line 60):
        CharacterGroup → EventName → StrOrigin → SequenceName → CastingKey → Desc → TimeFrame → DialogType → Group

    IMPORTANT: When too many core keys change at once, the 10-key lookup system
    cannot find a match, so production returns "New Row". This happens when:
    - StrOrigin + EventName + SequenceName all change (breaks SE, SO, EO lookups)
    - StrOrigin + EventName + CastingKey all change (breaks EC, OC, EO lookups)
    - StrOrigin + SequenceName + CastingKey all change (breaks SC, SO, OC lookups)
    - EventName + SequenceName + CastingKey all change (breaks SE, EC, SC lookups)
    - Any 4+ of the core keys change
    """
    # Check if this combination will break ALL lookups -> production returns "New Row"
    core_keys = {'StrOrigin', 'EventName', 'SequenceName', 'CastingKey'}
    changed_core = core_keys.intersection(change_types)

    # 10-key lookup combos that exist:
    # 4-key: SEOC (perfect match)
    # 3-key: SEO (StrOrigin+EventName+Seq), SEC (Seq+Event+Casting), SOC (Seq+StrOrigin+Casting), EOC (Event+StrOrigin+Casting)
    # 2-key: SE, SO, SC, EO, EC, OC

    # If 3+ core keys change, check if ANY lookup can still work
    if len(changed_core) >= 3:
        # For a lookup to work, all its keys must be UNCHANGED
        # Available lookups by unchanged keys:
        # SE: requires S and E unchanged
        # SO: requires S and O unchanged
        # SC: requires S and C unchanged
        # EO: requires E and O unchanged
        # EC: requires E and C unchanged
        # OC: requires O and C unchanged

        unchanged_core = core_keys - changed_core

        # Check if any 2-key lookup can work (needs 2 unchanged keys)
        lookup_pairs = [
            {'SequenceName', 'EventName'},      # SE
            {'SequenceName', 'StrOrigin'},      # SO
            {'SequenceName', 'CastingKey'},     # SC
            {'EventName', 'StrOrigin'},         # EO
            {'EventName', 'CastingKey'},        # EC
            {'StrOrigin', 'CastingKey'},        # OC
        ]

        can_match = any(pair.issubset(unchanged_core) for pair in lookup_pairs)

        if not can_match:
            return 'New Row'

    # EXACT production order from src/core/change_detection.py
    ORDER = ['CharacterGroup', 'EventName', 'StrOrigin', 'SequenceName', 'CastingKey',
             'Desc', 'TimeFrame', 'DialogType', 'Group']

    parts = [ct for ct in ORDER if ct in change_types]

    if not parts:
        return 'No Change'

    return '+'.join(parts) + ' Change'


# =============================================================================
# TEST DATA GENERATOR
# =============================================================================

class TestDataGenerator:
    """Generates PREVIOUS/CURRENT test files with controlled changes."""

    def __init__(self):
        self.test_cases: List[Dict] = []
        self.prev_rows: List[Dict] = []
        self.curr_rows: List[Dict] = []
        self.row_counter = 0

    def add_no_change_row(self) -> int:
        """Add a row with no changes (control case)."""
        row = create_base_row(self.row_counter)
        row['CastingKey'] = generate_casting_key(
            row['CharacterKey'], row['DialogVoice'], '', row['DialogType']
        )

        self.prev_rows.append(row.copy())
        self.curr_rows.append(row.copy())

        self.test_cases.append({
            'row_idx': self.row_counter,
            'change_types': (),
            'expected_label': 'No Change'
        })

        self.row_counter += 1
        return self.row_counter - 1

    def add_standalone_change(self, change_type: str) -> int:
        """Add a row with a single standalone change."""
        prev_row = create_base_row(self.row_counter)
        prev_row['CastingKey'] = generate_casting_key(
            prev_row['CharacterKey'], prev_row['DialogVoice'], '', prev_row['DialogType']
        )

        curr_row = prev_row.copy()
        changes = STANDALONE_CHANGES[change_type](curr_row, self.row_counter)
        curr_row.update(changes)

        if change_type == 'CastingKey':
            curr_row['CastingKey'] = generate_casting_key(
                curr_row['CharacterKey'], curr_row['DialogVoice'], '', curr_row['DialogType']
            )

        self.prev_rows.append(prev_row)
        self.curr_rows.append(curr_row)

        expected = EXPECTED_STANDALONE_LABELS[change_type]
        self.test_cases.append({
            'row_idx': self.row_counter,
            'change_types': (change_type,),
            'expected_label': expected
        })

        self.row_counter += 1
        return self.row_counter - 1

    def add_composite_change(self, change_types: Tuple[str, ...]) -> int:
        """Add a row with multiple field changes (composite)."""
        prev_row = create_base_row(self.row_counter)
        prev_row['CastingKey'] = generate_casting_key(
            prev_row['CharacterKey'], prev_row['DialogVoice'], '', prev_row['DialogType']
        )

        curr_row = prev_row.copy()

        for change_type in change_types:
            if change_type in STANDALONE_CHANGES:
                changes = STANDALONE_CHANGES[change_type](curr_row, self.row_counter)
                curr_row.update(changes)

        if 'CastingKey' in change_types:
            curr_row['CastingKey'] = generate_casting_key(
                curr_row['CharacterKey'], curr_row['DialogVoice'], '', curr_row['DialogType']
            )

        self.prev_rows.append(prev_row)
        self.curr_rows.append(curr_row)

        expected = build_expected_label(change_types)
        self.test_cases.append({
            'row_idx': self.row_counter,
            'change_types': change_types,
            'expected_label': expected
        })

        self.row_counter += 1
        return self.row_counter - 1

    def add_new_row(self) -> int:
        """Add a row that only exists in CURRENT (New Row)."""
        curr_row = create_base_row(self.row_counter)
        curr_row['CastingKey'] = generate_casting_key(
            curr_row['CharacterKey'], curr_row['DialogVoice'], '', curr_row['DialogType']
        )
        curr_row['StrOrigin'] = f'완전히 새로운 대사 {self.row_counter}'
        curr_row['EventName'] = f'brand_new_event_{self.row_counter:04d}'

        self.curr_rows.append(curr_row)

        self.test_cases.append({
            'row_idx': self.row_counter,
            'change_types': ('NewRow',),
            'expected_label': 'New Row',
            'is_new_row': True
        })

        self.row_counter += 1
        return self.row_counter - 1

    def add_character_group_variation(self, field: str) -> int:
        """Add a row with a specific character group field change."""
        prev_row = create_base_row(self.row_counter)
        prev_row['CastingKey'] = generate_casting_key(
            prev_row['CharacterKey'], prev_row['DialogVoice'], '', prev_row['DialogType']
        )

        curr_row = prev_row.copy()
        changes = CHAR_GROUP_VARIATIONS[field](curr_row, self.row_counter)
        curr_row.update(changes)

        self.prev_rows.append(prev_row)
        self.curr_rows.append(curr_row)

        self.test_cases.append({
            'row_idx': self.row_counter,
            'change_types': (f'CharacterGroup_{field}',),
            'expected_label': 'CharacterGroup Change'  # Production uses no space
        })

        self.row_counter += 1
        return self.row_counter - 1

    def generate_comprehensive_test(self, verbose: bool = False):
        """Generate comprehensive test covering ALL 518 possible test cases."""
        print("=" * 70)
        print("GENERATING COMPREHENSIVE TEST DATA - ALL 518 TEST CASES")
        print("=" * 70)

        # 1. No Change row
        print("\n[1] Adding No Change row (control)...")
        self.add_no_change_row()
        print(f"    Added 1 No Change row")

        # 2. Standalone changes - 9 types
        print("\n[2] Adding 9 Standalone changes...")
        for change_type in STANDALONE_CHANGES.keys():
            self.add_standalone_change(change_type)
        print(f"    Added 9 standalone change rows")

        # 3. Character Group variations - 5 types
        print("\n[3] Adding 5 Character Group variations...")
        for field in CHAR_GROUP_VARIATIONS.keys():
            self.add_character_group_variation(field)
        print(f"    Added 5 CharacterGroup variation rows")

        # 4. ALL Composite changes - 502 combinations
        print("\n[4] Adding ALL 502 Composite changes...")
        combos = get_all_composite_combinations()

        combo_counts = {}
        for combo in combos:
            n = len(combo)
            combo_counts[n] = combo_counts.get(n, 0) + 1
            self.add_composite_change(combo)

        print(f"    Breakdown by field count:")
        for n in sorted(combo_counts.keys()):
            print(f"      {n}-field: {combo_counts[n]} combinations")
        print(f"    Total composites: {len(combos)}")

        # 5. New Row
        print("\n[5] Adding New Row...")
        self.add_new_row()
        print(f"    Added 1 New Row")

        # Summary
        print("\n" + "=" * 70)
        print(f"TOTAL TEST CASES: {len(self.test_cases)}")
        print("=" * 70)

    def save_test_files(self, prev_path: str, curr_path: str):
        """Save PREVIOUS and CURRENT test files."""
        df_prev = pd.DataFrame(self.prev_rows)
        df_curr = pd.DataFrame(self.curr_rows)

        # Ensure all columns exist
        for col in TRUE_COLUMNS:
            if col not in df_prev.columns:
                df_prev[col] = ''
            if col not in df_curr.columns:
                df_curr[col] = ''

        df_prev = df_prev[TRUE_COLUMNS]
        df_curr = df_curr[TRUE_COLUMNS]

        df_prev.to_excel(prev_path, index=False)
        df_curr.to_excel(curr_path, index=False)

        print(f"\nSaved test files:")
        print(f"  PREVIOUS: {prev_path} ({len(df_prev)} rows)")
        print(f"  CURRENT:  {curr_path} ({len(df_curr)} rows)")

        return df_prev, df_curr


# =============================================================================
# TEST RUNNER
# =============================================================================

def run_raw_processor(df_prev: pd.DataFrame, df_curr: pd.DataFrame) -> Tuple[pd.DataFrame, Counter]:
    """Run RAW processor using production code."""
    from src.core.change_detection import get_priority_change

    df_prev = normalize_dataframe_status(df_prev.copy())
    df_curr = normalize_dataframe_status(df_curr.copy())
    df_prev = remove_full_duplicates(df_prev, "PREVIOUS")
    df_curr = remove_full_duplicates(df_curr, "CURRENT")

    # Generate CastingKeys
    for df in [df_prev, df_curr]:
        keys = []
        for idx, row in df.iterrows():
            keys.append(generate_casting_key(
                row.get(COL_CHARACTERKEY, ""), row.get(COL_DIALOGVOICE, ""),
                row.get(COL_SPEAKER_GROUPKEY, ""), row.get(COL_DIALOGTYPE, "")))
        df[COL_CASTINGKEY] = keys

    # Build lookups and run comparison
    lookups = build_lookups(df_prev)
    changes, prev_origins, cols, counter, marked, groups, pass1 = compare_rows(
        df_curr, df_prev, *lookups)

    # Add Phase 4 columns to result
    df_result = df_curr.copy()
    df_result['DETAILED_CHANGES'] = changes  # Full composite
    df_result['CHANGES'] = [get_priority_change(c) for c in changes]  # Priority label

    return df_result, counter


def run_working_processor(df_prev: pd.DataFrame, df_curr: pd.DataFrame) -> Tuple[pd.DataFrame, Counter]:
    """Run WORKING processor using production code."""
    df_prev = normalize_dataframe_status(df_prev.copy())
    df_curr = normalize_dataframe_status(df_curr.copy())
    df_prev = remove_full_duplicates(df_prev, "PREVIOUS")
    df_curr = remove_full_duplicates(df_curr, "CURRENT")

    # Generate CastingKeys
    for df in [df_prev, df_curr]:
        keys = []
        for idx, row in df.iterrows():
            keys.append(generate_casting_key(
                row.get(COL_CHARACTERKEY, ""), row.get(COL_DIALOGVOICE, ""),
                row.get(COL_SPEAKER_GROUPKEY, ""), row.get(COL_DIALOGTYPE, "")))
        df[COL_CASTINGKEY] = keys

    # Build lookups and run comparison
    lookups = build_working_lookups(df_prev, "PREVIOUS")
    result, counter, marked, pass1_results, previous_strorigins = process_working_comparison(
        df_curr, df_prev, *lookups)

    # Result already has CHANGES column
    return result, counter


# =============================================================================
# TEST VALIDATION
# =============================================================================

def validate_results(test_cases: List[Dict], df_result: pd.DataFrame, processor_name: str) -> Dict:
    """Validate results from a processor against expected values by ROW INDEX."""
    print(f"\n{'=' * 70}")
    print(f"VALIDATING {processor_name} PROCESSOR RESULTS")
    print(f"{'=' * 70}")

    # Phase 4: Use DETAILED_CHANGES for full composite validation (CHANGES now has priority label)
    changes_col = 'DETAILED_CHANGES' if 'DETAILED_CHANGES' in df_result.columns else 'CHANGES'
    changes_list = df_result[changes_col].tolist()

    results = {'passed': 0, 'failed': 0, 'errors': []}

    for test_case in test_cases:
        row_idx = test_case['row_idx']
        expected = test_case['expected_label']

        # Get actual by row index
        if row_idx < len(changes_list):
            actual = str(changes_list[row_idx]).strip()
        else:
            actual = 'INDEX OUT OF RANGE'

        if actual == expected:
            results['passed'] += 1
        else:
            results['failed'] += 1
            results['errors'].append({
                'row_idx': row_idx,
                'expected': expected,
                'actual': actual,
                'change_types': test_case['change_types']
            })

    # Summary
    passed = results['passed']
    failed = results['failed']
    total = passed + failed

    print(f"\n{processor_name} SUMMARY: {passed}/{total} passed ({100*passed/total:.1f}%)")

    if failed > 0:
        print(f"\n❌ FAILED CASES ({failed}):")
        # Group by actual result for cleaner output
        by_actual = {}
        for err in results['errors']:
            actual = err['actual']
            if actual not in by_actual:
                by_actual[actual] = []
            by_actual[actual].append(err)

        for actual, errs in sorted(by_actual.items()):
            print(f"\n  Actual: '{actual}' ({len(errs)} cases)")
            for err in errs[:5]:  # Show first 5
                print(f"    Row {err['row_idx']}: Expected '{err['expected']}' | Types: {err['change_types']}")
            if len(errs) > 5:
                print(f"    ... and {len(errs) - 5} more")

    return results


# =============================================================================
# MAIN TEST
# =============================================================================

def run_comprehensive_test():
    """Run the comprehensive change detection test."""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE CHANGE DETECTION TEST")
    print("Testing RAW and WORKING processors with TRUE VoiceRecordSheet structure")
    print("Total: 518 test cases (all possible change combinations)")
    print("=" * 70)

    # 1. Generate test data
    generator = TestDataGenerator()
    generator.generate_comprehensive_test()

    # 2. Save test files
    test_dir = os.path.dirname(os.path.abspath(__file__))
    prev_path = os.path.join(test_dir, 'UNIFIED_TEST_PREVIOUS.xlsx')
    curr_path = os.path.join(test_dir, 'UNIFIED_TEST_CURRENT.xlsx')

    df_prev, df_curr = generator.save_test_files(prev_path, curr_path)

    # 3. Run RAW processor
    print("\n" + "-" * 70)
    print("Running RAW processor...")
    print("-" * 70)

    df_raw_result, raw_counter = run_raw_processor(df_prev.copy(), df_curr.copy())
    print(f"RAW Counter: {dict(raw_counter)}")

    # 4. Run WORKING processor
    print("\n" + "-" * 70)
    print("Running WORKING processor...")
    print("-" * 70)

    df_working_result, working_counter = run_working_processor(df_prev.copy(), df_curr.copy())
    print(f"WORKING Counter: {dict(working_counter)}")

    # 5. Validate results
    raw_results = validate_results(generator.test_cases, df_raw_result, 'RAW')
    working_results = validate_results(generator.test_cases, df_working_result, 'WORKING')

    # 6. Final summary
    print("\n" + "=" * 70)
    print("FINAL TEST SUMMARY")
    print("=" * 70)

    for name, results in [('RAW', raw_results), ('WORKING', working_results)]:
        passed = results['passed']
        failed = results['failed']
        total = passed + failed
        pct = 100 * passed / total if total > 0 else 0
        status = '✅' if failed == 0 else '❌'
        print(f"{status} {name}: {passed}/{total} ({pct:.1f}%)")

    # 7. Save results
    raw_output = os.path.join(test_dir, 'UNIFIED_TEST_RAW_RESULT.xlsx')
    working_output = os.path.join(test_dir, 'UNIFIED_TEST_WORKING_RESULT.xlsx')

    df_raw_result.to_excel(raw_output, index=False)
    df_working_result.to_excel(working_output, index=False)

    print(f"\nResults saved:")
    print(f"  RAW:     {raw_output}")
    print(f"  WORKING: {working_output}")

    # Return success status
    total_failed = raw_results['failed'] + working_results['failed']
    return total_failed == 0


if __name__ == '__main__':
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
