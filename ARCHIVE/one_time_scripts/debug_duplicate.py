#!/usr/bin/env python3
"""Debug duplicate StrOrigin issue."""

import sys
import os
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.io.excel_reader import safe_read_excel
from src.utils.data_processing import normalize_dataframe_status
from src.core.casting import generate_casting_key
from src.config import COL_CASTINGKEY, COL_SEQUENCE, COL_EVENTNAME, COL_STRORIGIN

# Load test files
prev_file = "Test_DuplicateStrOrigin_Previous.xlsx"
curr_file = "Test_DuplicateStrOrigin_Current.xlsx"

df_prev = safe_read_excel(prev_file, header=0, dtype=str)
df_curr = safe_read_excel(curr_file, header=0, dtype=str)

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

print("="*80)
print("DEBUGGING: NEW ROWS with duplicate 'Hello'")
print("="*80)

# Find rows in CURRENT that should be NEW (Event 9000-9004)
new_hello_rows = df_curr[(df_curr["EventName"] >= "Event9000") & (df_curr["EventName"] < "Event9005")]

print(f"\nFound {len(new_hello_rows)} rows with EventName 9000-9004 (should be NEW):")
for idx, row in new_hello_rows.iterrows():
    S = row[COL_SEQUENCE]
    E = row[COL_EVENTNAME]
    O = row[COL_STRORIGIN]
    C = row[COL_CASTINGKEY]

    print(f"\n  Row {idx}:")
    print(f"    Sequence:   {S}")
    print(f"    Event:      {E}")
    print(f"    StrOrigin:  '{O}'")
    print(f"    CastingKey: {C}")

    # Check which keys match in PREVIOUS
    print(f"\n    Checking PREVIOUS for matching keys:")

    # key_se
    matches_se = df_prev[(df_prev[COL_SEQUENCE] == S) & (df_prev[COL_EVENTNAME] == E)]
    print(f"      key_se (S+E): {len(matches_se)} matches")

    # key_so
    matches_so = df_prev[(df_prev[COL_SEQUENCE] == S) & (df_prev[COL_STRORIGIN] == O)]
    print(f"      key_so (S+O): {len(matches_so)} matches ⚠️  DUPLICATE!")
    if len(matches_so) > 0:
        print(f"        → Matched with Events: {list(matches_so[COL_EVENTNAME].values)}")

    # key_sc
    matches_sc = df_prev[(df_prev[COL_SEQUENCE] == S) & (df_prev[COL_CASTINGKEY] == C)]
    print(f"      key_sc (S+C): {len(matches_sc)} matches")

    # key_eo
    matches_eo = df_prev[(df_prev[COL_EVENTNAME] == E) & (df_prev[COL_STRORIGIN] == O)]
    print(f"      key_eo (E+O): {len(matches_eo)} matches")

    # key_ec
    matches_ec = df_prev[(df_prev[COL_EVENTNAME] == E) & (df_prev[COL_CASTINGKEY] == C)]
    print(f"      key_ec (E+C): {len(matches_ec)} matches")

    # key_oc
    matches_oc = df_prev[(df_prev[COL_STRORIGIN] == O) & (df_prev[COL_CASTINGKEY] == C)]
    print(f"      key_oc (O+C): {len(matches_oc)} matches")

    # 3-key
    matches_seo = df_prev[(df_prev[COL_SEQUENCE] == S) & (df_prev[COL_EVENTNAME] == E) & (df_prev[COL_STRORIGIN] == O)]
    print(f"      key_seo (S+E+O): {len(matches_seo)} matches")

    matches_sec = df_prev[(df_prev[COL_SEQUENCE] == S) & (df_prev[COL_EVENTNAME] == E) & (df_prev[COL_CASTINGKEY] == C)]
    print(f"      key_sec (S+E+C): {len(matches_sec)} matches")

    matches_soc = df_prev[(df_prev[COL_SEQUENCE] == S) & (df_prev[COL_STRORIGIN] == O) & (df_prev[COL_CASTINGKEY] == C)]
    print(f"      key_soc (S+O+C): {len(matches_soc)} matches")

    matches_eoc = df_prev[(df_prev[COL_EVENTNAME] == E) & (df_prev[COL_STRORIGIN] == O) & (df_prev[COL_CASTINGKEY] == C)]
    print(f"      key_eoc (E+O+C): {len(matches_eoc)} matches")

print("\n" + "="*80)
print("CONCLUSION:")
print("="*80)
print("The problem: key_so (Sequence + StrOrigin) MATCHES because:")
print("  - Same Sequence: 'Scene1'")
print("  - Same StrOrigin: 'Hello' (DUPLICATE)")
print("  - But different Event and CastingKey")
print()
print("This causes the 10-key system to think it's a CHANGE, not a NEW row!")
print("Because at least ONE of the 10 keys matches, it's not 'all keys missing'.")
print()
print("STEP 1 check fails: NOT all 10 keys missing → NOT 'New Row'")
print("STEP 2: Falls through to pattern matching → finds key_so match")
print("  → Classifies as 'No Relevant Change' (EventName+CastingKey changed)")
print()
print("This is the BUG!")
print("="*80)
