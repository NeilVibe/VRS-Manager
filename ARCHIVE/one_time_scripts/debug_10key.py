#!/usr/bin/env python3
"""
Debug script to check what's happening with the "No Change" vs "CastingKey Change" bug.
"""

import sys
import os
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.io.excel_reader import safe_read_excel
from src.utils.data_processing import normalize_dataframe_status
from src.core.casting import generate_casting_key
from src.config import COL_CASTINGKEY, COL_SEQUENCE, COL_EVENTNAME, COL_STRORIGIN

# Load test files
prev_file = "Test_Previous.xlsx"
curr_file = "Test_Current.xlsx"

print("Loading files...")
df_prev = safe_read_excel(prev_file, header=0, dtype=str)
df_curr = safe_read_excel(curr_file, header=0, dtype=str)

print(f"Previous: {len(df_prev)} rows")
print(f"Current:  {len(df_curr)} rows")

# Normalize
df_prev = normalize_dataframe_status(df_prev)
df_curr = normalize_dataframe_status(df_curr)

# Generate CastingKey
for df in [df_prev, df_curr]:
    casting_keys = []
    for idx, row in df.iterrows():
        key = generate_casting_key(
            row.get("CharacterKey", ""),
            row.get("DialogVoice", ""),
            row.get("SpeakerGroupKey", ""),
            row.get("DialogType", "")
        )
        casting_keys.append(key)
    df[COL_CASTINGKEY] = casting_keys

print("\n" + "="*80)
print("DEBUGGING: Checking rows that should be 'No Change'")
print("="*80)

# Expected unchanged rows: 0-24 and 45-49 from Previous
# These should also be in Current at positions 0-24 and 40-44

unchanged_indices_prev = list(range(0, 25)) + list(range(45, 50))
print(f"\nExpected {len(unchanged_indices_prev)} unchanged rows from Previous")

# Check a few sample rows
samples = [0, 5, 10, 24, 45, 49]
for idx in samples:
    if idx >= len(df_prev):
        continue

    prev_row = df_prev.iloc[idx]

    # Find matching row in current
    matches = df_curr[
        (df_curr[COL_SEQUENCE] == prev_row[COL_SEQUENCE]) &
        (df_curr[COL_EVENTNAME] == prev_row[COL_EVENTNAME]) &
        (df_curr[COL_STRORIGIN] == prev_row[COL_STRORIGIN])
    ]

    if len(matches) > 0:
        curr_row = matches.iloc[0]

        prev_casting = prev_row[COL_CASTINGKEY]
        curr_casting = curr_row[COL_CASTINGKEY]

        print(f"\n--- Row {idx} from Previous ---")
        print(f"  Sequence:  {prev_row[COL_SEQUENCE]}")
        print(f"  Event:     {prev_row[COL_EVENTNAME]}")
        print(f"  StrOrigin: {prev_row[COL_STRORIGIN]}")
        print(f"  CastingKey Prev: {prev_casting}")
        print(f"  CastingKey Curr: {curr_casting}")
        print(f"  Match: {prev_casting == curr_casting}")

        if prev_casting == curr_casting:
            print(f"  → Should be: 'No Change'")
        else:
            print(f"  → Should be: 'CastingKey Change'")
    else:
        print(f"\n--- Row {idx} from Previous ---")
        print(f"  NOT FOUND in Current (might be deleted)")

print("\n" + "="*80)
print("CONCLUSION:")
print("="*80)
print("The bug is in comparison.py line 90-96:")
print("When key_seo matches, we ASSUME CastingKey changed.")
print("But we need to CHECK if CastingKey actually changed!")
print()
print("Fix: Compare CastingKey values when key_seo matches:")
print("  - If same → 'No Change'")
print("  - If different → 'CastingKey Change'")
print("="*80)
