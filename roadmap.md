# VRS Manager - Development Roadmap

## Phase 1: Master File Update - LOW Importance Logic Fix

### Problem Statement
Currently, the Master File Update process treats LOW importance rows the same as HIGH importance rows:
- It copies SOURCE data to output for both HIGH and LOW
- This overwrites TARGET data even for LOW importance rows
- NEW + LOW rows are included in output (should be deleted)

### Required Changes

#### 1.1 LOW Importance - Existing Rows (NOT "New Row")
**Requirement**: Keep TARGET data intact, only classify in sheet

**Current Behavior** (lines 1631-1687):
```python
# Copies SOURCE data to output
for col in output_structure:
    if col in source_row.index:
        output_row[col] = safe_str(source_row[col])  # ❌ WRONG
```

**New Behavior**:
```python
# For existing rows (NOT "New Row"), keep TARGET data
if change_type != "New Row":
    # Use TARGET data instead of SOURCE
    for col in output_structure:
        if col in target_row.index:
            output_row[col] = safe_str(target_row[col])  # ✓ CORRECT
        elif col in source_row.index:
            output_row[col] = safe_str(source_row[col])
        else:
            output_row[col] = ""
    # Still set CHANGES and Importance from classification
    output_row["CHANGES"] = change_type
    output_row[COL_IMPORTANCE] = "Low"
else:
    # For "New Row", use SOURCE data (will be deleted later)
    # (keep current logic for now, will be filtered in step 1.2)
```

#### 1.2 LOW Importance - New Rows (Post-Process Deletion)
**Requirement**: Delete rows where BOTH:
- Importance = "Low"
- CHANGES = "New Row"

**Implementation** (add after line 1687):
```python
# STEP 5b: Filter out LOW + New Row
log("\nFiltering LOW importance NEW rows...")
original_count = len(df_low_output)
df_low_output = df_low_output[df_low_output["CHANGES"] != "New Row"]
filtered_count = original_count - len(df_low_output)
if filtered_count > 0:
    log(f"  → Removed {filtered_count:,} LOW importance NEW rows")
    low_counter["Deleted (LOW+New)"] = filtered_count
log(f"  → Final LOW rows: {len(df_low_output):,}")
```

### Files to Modify
- `vrsmanager1114.py`
  - Function: `process_master_file_update()` (lines 1459-1827)
  - Section: LOW importance processing (lines 1631-1687)
  - Add: Post-process filter after line 1687

### Testing Plan
1. **Test Case 1**: LOW + Existing Row
   - Setup: TARGET has row with StrOrigin "A", SOURCE has same with StrOrigin "B"
   - Expected: Output shows "A" (TARGET data), classified as "StrOrigin Change"

2. **Test Case 2**: LOW + New Row
   - Setup: SOURCE has new row not in TARGET, marked LOW importance
   - Expected: Row does NOT appear in "Low Importance" sheet

3. **Test Case 3**: HIGH + New Row
   - Setup: SOURCE has new row not in TARGET, marked HIGH importance
   - Expected: Row DOES appear in "Main Sheet (High)"

4. **Test Case 4**: LOW + Deleted Row
   - Setup: TARGET has row, SOURCE doesn't (3-key validated deletion)
   - Expected: Row appears in "Deleted Rows" sheet

### Estimated Effort
- **Development**: 2 hours
- **Testing**: 1 hour
- **Total**: 3 hours
- **Status**: ✅ COMPLETED (v1114v2)

---

## Phase 1.5: Upgrade to QUADRUPLE KEY (4-Tier) Identification System

### Problem Statement
The current 3-key system has a critical edge case with duplicate StrOrigin values:

**Scenario:**
```
PREVIOUS file:
Row A: SequenceName="Scene1", EventName="12345", StrOrigin="안녕하세요", CastingKey="Hero_Male_A"

CURRENT file (100 new rows):
Row B1: SequenceName="Scene1", EventName="54321", StrOrigin="안녕하세요", CastingKey="NPC_Female_B"
Row B2: SequenceName="Scene1", EventName="99999", StrOrigin="안녕하세요", CastingKey="Villain_Male_C"
... (98 more with same StrOrigin but different characters)
```

**Current Behavior (WRONG):**
- Key 2 (CG) = `(SequenceName, StrOrigin)` = `(Scene1, 안녕하세요)` **MATCHES**
- System thinks: "EventName changed from 12345 to 54321"
- Result: Marks as **"EventName Change"** instead of **"New Row"**
- **Root Cause**: StrOrigin is a common phrase ("Hello") used by multiple characters

**Why This Happens:**
- Common dialogue phrases like "안녕하세요", "Hello", "Yes", "No" are reused across many characters
- Key 2 `(SequenceName, StrOrigin)` creates false matches
- Without character identification, we can't distinguish who's speaking
- This causes **incorrect change classification** and **missed new rows**

### Solution: Add 4th Key with CastingKey

**New 4-Tier Key System:**
```python
Key 1 (CW): (SequenceName, EventName)
Key 2 (CG): (SequenceName, StrOrigin)
Key 3 (ES): (EventName, StrOrigin)
Key 4 (CS): (CastingKey, SequenceName)  ← NEW!
```

**Why CastingKey?**
- CastingKey format: `{CharacterKey}_{DialogVoice}_{GroupKey}_{DialogType}`
- **Unique per character** within a sequence
- Differentiates speakers even with identical dialogue
- Example: `Hero_Male_Main_A` vs `NPC_Female_Secondary_B`

**New Detection Logic:**
```python
# NEW ROW: ALL 4 keys must be missing from TARGET
is_new = (key_cw not in target) AND \
         (key_cg not in target) AND \
         (key_es not in target) AND \
         (key_cs not in target)  # ← NEW!

# DELETED ROW: ALL 4 keys must be missing from SOURCE
is_deleted = (key_cw not in source) AND \
             (key_cg not in source) AND \
             (key_es not in source) AND \
             (key_cs not in source)  # ← NEW!
```

**Example with 4-Key System:**
```
PREVIOUS Row A:
- Key1 (CW): (Scene1, 12345) ✓
- Key2 (CG): (Scene1, 안녕하세요) ✓
- Key3 (ES): (12345, 안녕하세요) ✓
- Key4 (CS): (Hero_Male_A, Scene1) ✓

NEW Row B1:
- Key1 (CW): (Scene1, 54321) ✗ NOT in target
- Key2 (CG): (Scene1, 안녕하세요) ✓ MATCHES (but not alone!)
- Key3 (ES): (54321, 안녕하세요) ✗ NOT in target
- Key4 (CS): (NPC_Female_B, Scene1) ✗ NOT in target

Decision: Not ALL 4 keys match → Correctly marked as NEW ROW! ✅
```

### Required Changes

#### Impact Scope
This change affects **ALL 4 processes**:
1. ✅ Raw Process (`process_raw_vrs_check`)
2. ✅ Working Process (`process_working_vrs_check`)
3. ✅ All Language Process (`process_all_language_check`)
4. ✅ Master File Update (`process_master_file_update`)

#### 1. Update Lookup Building Functions

**File**: `vrsmanager1114v2.py`

**Function**: `build_lookups()` (lines 527-552)
```python
# Add 4th lookup - CastingKey + SequenceName
def build_lookups(df):
    lookup_cw = {}  # SequenceName + EventName
    lookup_cg = {}  # SequenceName + StrOrigin
    lookup_es = {}  # EventName + StrOrigin
    lookup_cs = {}  # NEW: CastingKey + SequenceName

    for _, row in df.iterrows():
        key_cw = (row[COL_SEQUENCE], row[COL_EVENTNAME])
        key_cg = (row[COL_SEQUENCE], row[COL_STRORIGIN])
        key_es = (row[COL_EVENTNAME], row[COL_STRORIGIN])
        key_cs = (row[COL_CASTINGKEY], row[COL_SEQUENCE])  # NEW

        lookup_cw[key_cw] = row.to_dict()
        if key_cg not in lookup_cg:
            lookup_cg[key_cg] = row[COL_EVENTNAME]
        if key_es not in lookup_es:
            lookup_es[key_es] = row.to_dict()
        if key_cs not in lookup_cs:  # NEW
            lookup_cs[key_cs] = row.to_dict()  # NEW

    return lookup_cw, lookup_cg, lookup_es, lookup_cs  # Added lookup_cs
```

**Function**: `build_working_lookups()` (lines 749-777)
- Same pattern: Add `lookup_cs = {}` and return 4 lookups

#### 2. Update Raw Process

**Function**: `compare_rows()` (lines 582-703)

**Changes needed:**
```python
def compare_rows(df_curr, prev_lookup_cw, prev_lookup_cg, prev_lookup_es, prev_lookup_cs):  # Add 4th param
    # ... existing code ...

    for idx, curr_row in df_curr.iterrows():
        key_cw = (curr_row[COL_SEQUENCE], curr_row[COL_EVENTNAME])
        key_cg = (curr_row[COL_SEQUENCE], curr_row[COL_STRORIGIN])
        key_es = (curr_row[COL_EVENTNAME], curr_row[COL_STRORIGIN])
        key_cs = (curr_row[COL_CASTINGKEY], curr_row[COL_SEQUENCE])  # NEW

        # Stage 1: Direct match
        if key_cw in prev_lookup_cw:
            # ... existing logic ...

        # Stage 2: EventName changed
        elif key_cg in prev_lookup_cg:
            # ... existing logic ...

        # Stage 3: SequenceName changed
        elif key_es in prev_lookup_es:
            # ... existing logic ...

        # Stage 4: CastingKey + SequenceName match (NEW)
        elif key_cs in prev_lookup_cs:
            change_label = "Character Change"  # Or appropriate label
            prev_row = prev_lookup_cs[key_cs]
            # ... handle the match ...

        # Stage 5: New row (was Stage 4)
        else:
            change_label = "New Row"
            changes.append(change_label)
            # ... existing logic ...
```

**Function**: `find_deleted_rows()` (lines 704-724)
```python
def find_deleted_rows(df_prev, df_curr, prev_lookup_cs):  # Add 4th param
    # Build current keys - all 4 types
    curr_keys_cw = set()
    curr_keys_cg = set()
    curr_keys_es = set()
    curr_keys_cs = set()  # NEW

    for _, curr_row in df_curr.iterrows():
        curr_keys_cw.add((curr_row[COL_SEQUENCE], curr_row[COL_EVENTNAME]))
        curr_keys_cg.add((curr_row[COL_SEQUENCE], curr_row[COL_STRORIGIN]))
        curr_keys_es.add((curr_row[COL_EVENTNAME], curr_row[COL_STRORIGIN]))
        curr_keys_cs.add((curr_row[COL_CASTINGKEY], curr_row[COL_SEQUENCE]))  # NEW

    deleted = []
    for _, prev_row in df_prev.iterrows():
        key_cw = (prev_row[COL_SEQUENCE], prev_row[COL_EVENTNAME])
        key_cg = (prev_row[COL_SEQUENCE], prev_row[COL_STRORIGIN])
        key_es = (prev_row[COL_EVENTNAME], prev_row[COL_STRORIGIN])
        key_cs = (prev_row[COL_CASTINGKEY], prev_row[COL_SEQUENCE])  # NEW

        # Only mark as deleted if ALL 4 keys are missing
        if (key_cw not in curr_keys_cw) and \
           (key_cg not in curr_keys_cg) and \
           (key_es not in curr_keys_es) and \
           (key_cs not in curr_keys_cs):  # NEW
            deleted.append(prev_row.to_dict())

    return deleted
```

**Function**: `process_raw_vrs_check()` (lines 2021-2126)
```python
# Update the function call to build and use 4 lookups
prev_lookup_cw, prev_lookup_cg, prev_lookup_es, prev_lookup_cs = build_lookups(df_prev)
changes, prev_strorigins, changed_cols, counter = compare_rows(
    df_curr, prev_lookup_cw, prev_lookup_cg, prev_lookup_es, prev_lookup_cs
)
```

#### 3. Update Working Process

**Function**: `classify_working_change()` (lines 779-803)
- Add `prev_lookup_cs` parameter
- Add Stage 4 for CastingKey+SequenceName match
- Update Stage 5 (New Row) logic

**Function**: `process_working_comparison()` (lines 911-1014)
- Add 4th key generation: `key_cs`
- Add Stage 4 matching logic
- Update deleted row detection to check all 4 keys

**Function**: `find_working_deleted_rows()` (lines 1015-1039)
- Add 4th key check to deletion logic

**Function**: `process_working_vrs_check()` (lines 2127-2224)
- Update lookup building to return 4 lookups
- Pass all 4 lookups to comparison functions

#### 4. Update All Language Process

**Function**: `merge_current_files()` (lines 1147-1230)
- Ensure CastingKey is included in merge
- Generate CastingKey if missing

**Function**: `process_alllang_comparison()` (lines 1231-1370)
- Add 4th key generation for all 3 languages
- Add Stage 4 matching logic per language
- Update deleted row detection to check all 4 keys

**Function**: `process_all_language_check()` (lines 2225-2346)
- Update lookup building for all languages (KR, EN, CN)
- Pass all 4 lookups per language to comparison

#### 5. Update Master File Update

**Function**: `process_master_file_update()` (lines 1459-1827)

**High Importance Section** (lines 1524-1629):
```python
# Build lookups with 4 keys
source_high_lookup = {}
source_high_lookup_cg = {}
source_high_lookup_es = {}
source_high_lookup_cs = {}  # NEW

for _, row in df_high.iterrows():
    key_cw = (row[COL_SEQUENCE], row[COL_EVENTNAME])
    key_cg = (row[COL_SEQUENCE], row[COL_STRORIGIN])
    key_es = (row[COL_EVENTNAME], row[COL_STRORIGIN])
    key_cs = (row[COL_CASTINGKEY], row[COL_SEQUENCE])  # NEW

    source_high_lookup[key_cw] = row.to_dict()
    if key_cg not in source_high_lookup_cg:
        source_high_lookup_cg[key_cg] = row[COL_EVENTNAME]
    if key_es not in source_high_lookup_es:
        source_high_lookup_es[key_es] = row.to_dict()
    if key_cs not in source_high_lookup_cs:  # NEW
        source_high_lookup_cs[key_cs] = row.to_dict()  # NEW

# Processing loop
for idx, source_row in df_high.iterrows():
    key_cw = (source_row[COL_SEQUENCE], source_row[COL_EVENTNAME])
    key_cg = (source_row[COL_SEQUENCE], source_row[COL_STRORIGIN])
    key_es = (source_row[COL_EVENTNAME], source_row[COL_STRORIGIN])
    key_cs = (source_row[COL_CASTINGKEY], source_row[COL_SEQUENCE])  # NEW

    # Stage 1: Direct match
    if key_cw in target_lookup:
        # ... existing logic ...

    # Stage 2: EventName changed
    elif key_cg in target_lookup_cg:
        # ... existing logic ...

    # Stage 3: SequenceName changed
    elif key_es in target_lookup_es:
        # ... existing logic ...

    # Stage 4: CastingKey + SequenceName match (NEW)
    elif key_cs in target_lookup_cs:
        change_type = "Character Change"  # Or appropriate label
        target_row = target_lookup_cs[key_cs]

    # Stage 5: New row (was Stage 4)
    else:
        change_type = "New Row"
        target_row = None
```

**Low Importance Section** (lines 1631-1702):
- Same pattern as High Importance
- Add 4th key generation and matching

**Deleted Rows Section** (lines 1704-1720):
```python
# Build all current keys (4 types)
source_all_keys_cw = set(source_high_lookup.keys()) | set(source_low_lookup.keys())
source_all_keys_cg = set(source_high_lookup_cg.keys()) | set(source_low_lookup_cg.keys())
source_all_keys_es = set(source_high_lookup_es.keys()) | set(source_low_lookup_es.keys())
source_all_keys_cs = set(source_high_lookup_cs.keys()) | set(source_low_lookup_cs.keys())  # NEW

for _, target_row in df_target.iterrows():
    key_cw = (target_row[COL_SEQUENCE], target_row[COL_EVENTNAME])
    key_cg = (target_row[COL_SEQUENCE], target_row[COL_STRORIGIN])
    key_es = (target_row[COL_EVENTNAME], target_row[COL_STRORIGIN])
    key_cs = (target_row[COL_CASTINGKEY], target_row[COL_SEQUENCE])  # NEW

    # Only mark as deleted if ALL 4 keys are missing
    if (key_cw not in source_all_keys_cw) and \
       (key_cg not in source_all_keys_cg) and \
       (key_es not in source_all_keys_es) and \
       (key_cs not in source_all_keys_cs):  # NEW
        # ... mark as deleted ...
```

### Files to Modify

**Primary file**: `vrsmanager1114v2.py` → Create `vrsmanager1114v3.py`

**Functions requiring updates** (20 functions):
1. `build_lookups()` - Add 4th lookup
2. `build_working_lookups()` - Add 4th lookup
3. `compare_rows()` - Add 4th key matching
4. `find_deleted_rows()` - Check 4 keys
5. `classify_working_change()` - Add 4th key logic
6. `process_working_comparison()` - Use 4 keys
7. `find_working_deleted_rows()` - Check 4 keys
8. `classify_alllang_change()` - Add 4th key logic
9. `apply_import_logic()` - May need adjustment
10. `apply_import_logic_alllang_lang()` - May need adjustment
11. `merge_current_files()` - Ensure CastingKey present
12. `process_alllang_comparison()` - Use 4 keys
13. `process_raw_vrs_check()` - Build/use 4 lookups
14. `process_working_vrs_check()` - Build/use 4 lookups
15. `process_all_language_check()` - Build/use 4 lookups per language
16. `process_master_file_update()` - HIGH section (4 keys)
17. `process_master_file_update()` - LOW section (4 keys)
18. `process_master_file_update()` - Deleted section (4 keys)
19. `create_raw_summary()` - Update statistics if needed
20. `create_working_summary()` - Update statistics if needed

### Testing Plan

#### Test Case 1: Duplicate StrOrigin - Different Characters
**Setup:**
```
PREVIOUS:
Row 1: Seq="S1", Event="E1", StrOrigin="Hello", CastingKey="Hero_A"

CURRENT:
Row 1: Seq="S1", Event="E1", StrOrigin="Hello", CastingKey="Hero_A" (same)
Row 2: Seq="S1", Event="E2", StrOrigin="Hello", CastingKey="NPC_B" (new character)
```

**Expected with 3-key**: Row 2 marked as "EventName Change" ❌
**Expected with 4-key**: Row 2 marked as "New Row" ✅

#### Test Case 2: Character Change Same Dialogue
**Setup:**
```
PREVIOUS:
Row 1: Seq="S1", Event="E1", StrOrigin="Hello", CastingKey="Hero_A"

CURRENT:
Row 1: Seq="S1", Event="E1", StrOrigin="Hello", CastingKey="Villain_B" (character swap)
```

**Expected**: Marked as "Character Change" (new Stage 4 detection)

#### Test Case 3: Deleted Row with 4-Key Validation
**Setup:**
```
PREVIOUS:
Row 1: Seq="S1", Event="E1", StrOrigin="Hello", CastingKey="Hero_A"

CURRENT:
(Row 1 removed)
```

**Expected**: All 4 keys missing → Correctly marked as "Deleted Row" ✅

#### Test Case 4: Working Process Import with Duplicate StrOrigin
**Setup:**
```
PREVIOUS (completed work):
Row 1: Seq="S1", Event="E1", StrOrigin="Hello", CastingKey="Hero_A", Status="FINAL"

CURRENT (new baseline):
Row 1: Seq="S1", Event="E2", StrOrigin="Hello", CastingKey="NPC_B", Status="" (new character)
```

**Expected**: No import (correctly identified as new row, not a match)

#### Test Case 5: All 4 Processes Integration
- Run all 4 processes with test data
- Verify consistent behavior across all processes
- Check statistics and change counts are accurate

### Migration Strategy

#### Option A: Direct Migration (Recommended)
1. Create `vrsmanager1114v3.py` from `vrsmanager1114v2.py`
2. Update all 20 functions with 4-key logic
3. Update version strings to "1114v3"
4. Test thoroughly with real data
5. Keep v2 as rollback option

#### Option B: Incremental Migration
1. Create feature branch for 4-key system
2. Update one process at a time:
   - Week 1: Raw Process
   - Week 2: Working Process
   - Week 3: All Language Process
   - Week 4: Master File Update
3. Test each process independently
4. Merge when all processes complete

**Recommended**: Option A (faster, ensures consistency)

### Estimated Effort
- **Analysis & Design**: 2 hours ✅ COMPLETED
- **Lookup Functions**: 2 hours (2 functions) ✅ COMPLETED
- **Raw Process**: 4 hours (3 functions) ✅ COMPLETED
- **Working Process**: 4 hours (4 functions) ✅ COMPLETED
- **All Language Process**: 4 hours (3 functions) ✅ COMPLETED
- **Master File Update**: 4 hours (3 sections) ✅ COMPLETED
- **Testing**: 6 hours (comprehensive testing) ⏳ PENDING
- **Documentation**: 2 hours ⏳ IN PROGRESS
- **Total**: **28 hours** (~3.5 days full-time)
- **Status**: 🎯 **IMPLEMENTATION COMPLETED** (awaiting testing)

### Risks & Mitigation

**Risk 1**: CastingKey might be missing in some rows
- **Mitigation**: Generate CastingKey if missing using `generate_casting_key()` function
- Add validation step before building lookups

**Risk 2**: Breaking existing behavior
- **Mitigation**: Keep v2 as rollback, extensive testing
- Test with real production data before deployment

**Risk 3**: Performance impact (4 lookups vs 3)
- **Mitigation**: Minimal impact (O(1) dictionary lookups)
- Benchmark with large files (10k+ rows)

**Risk 4**: Inconsistent behavior across 4 processes
- **Mitigation**: Share common logic via helper functions
- Use same key generation pattern everywhere

### Success Criteria
- ✅ All 20 functions updated with 4-key logic
- ⏳ All 5 test cases pass (PENDING - requires testing)
- ✅ All 4 processes handle duplicates correctly (CODE COMPLETE)
- ⏳ No regression in existing functionality (PENDING - requires testing)
- ⏳ Performance acceptable (<10% slowdown) (PENDING - requires benchmarking)
- ⏳ Statistics and reports accurate (PENDING - requires testing)

### Version Update
- **Version**: 1114v3
- **Footer**: "4-Tier Key System | Duplicate StrOrigin Fix"
- **Files**: Keep v2 and v3 both in repo

### Implementation Summary (vrsmanager1114v3.py)

**All code changes completed**. The following functions were updated with 4-Tier Key System:

1. ✅ `build_lookups()` - Returns 4 lookups (CW, CG, ES, CS)
2. ✅ `build_working_lookups()` - Returns 4 lookups
3. ✅ `compare_rows()` - Stage 2 verification with Key 4
4. ✅ `find_deleted_rows()` - Checks all 4 keys
5. ✅ `classify_working_change()` - Key 4 verification for EventName Change
6. ✅ `classify_alllang_change()` - Key 4 verification for All Language
7. ✅ `process_working_comparison()` - Stage 2 with Key 4 verification
8. ✅ `find_working_deleted_rows()` - Checks all 4 keys
9. ✅ `process_alllang_comparison()` - Stage 2 with Key 4 verification
10. ✅ `process_raw_vrs_check()` - Passes 4 lookups to compare_rows
11. ✅ `process_working_vrs_check()` - Builds and passes 4 lookups
12. ✅ `process_all_language_check()` - Builds 4 lookups per language (KR/EN/CN)
13. ✅ `process_master_file_update()` - HIGH section with 4 keys
14. ✅ `process_master_file_update()` - LOW section with 4 keys
15. ✅ `process_master_file_update()` - Deleted rows with 4 keys

**Key Changes Implemented:**

**Stage 2 Verification Logic (applied to all processes):**
```python
# Stage 2: StrOrigin+Sequence match - VERIFY with Key 4
elif key_cg in prev_lookup_cg:
    if key_cs in prev_lookup_cs:
        # Same character → EventName Change
        # ... handle as EventName Change ...
    else:
        # Different character → New Row (duplicate StrOrigin case)
        change_type = "New Row"
        prev_row = None
```

**Deleted Row Detection (applied to all processes):**
```python
# Only mark as deleted if ALL 4 keys are missing
if (key_cw not in curr_keys_cw) and \
   (key_cg not in curr_keys_cg) and \
   (key_es not in curr_keys_es) and \
   (key_cs not in curr_keys_cs):  # NEW 4th key check
    # Mark as deleted
```

**Next Steps:**
1. ⏳ Run comprehensive testing with real data
2. ⏳ Verify all 5 test cases pass
3. ⏳ Performance benchmarking (compare v2 vs v3)
4. ⏳ User acceptance testing
5. ⏳ Documentation updates (claude.md)

---

## Phase 2: Code Restructuring - From Monolith to Tree

### Current State Analysis
- **File**: Single 2,633-line file
- **Functions**: 48 functions, no classes
- **Largest Functions**:
  - `process_master_file_update()`: 369 lines
  - `create_gui()`: 197 lines
  - `show_update_history_viewer()`: 167 lines
  - `process_alllang_comparison()`: 140 lines

### Problems Identified
1. **No separation of concerns** - GUI, business logic, I/O mixed
2. **Untestable** - Cannot unit test individual components
3. **Hard to extend** - Adding features requires navigating 2,600+ lines
4. **Code duplication** - Similar logic in Raw/Working/AllLang processes
5. **Large functions** - 300+ line functions are unmaintainable

### Target Structure

```
vrs-manager/
├── src/
│   ├── __init__.py
│   ├── config.py                      # Configuration constants
│   │
│   ├── models/                        # Data structures
│   │   ├── __init__.py
│   │   └── data_structures.py         # Row, Lookup, Counter classes
│   │
│   ├── core/                          # Core business logic
│   │   ├── __init__.py
│   │   ├── comparison.py              # compare_rows, classify_change
│   │   ├── lookups.py                 # build_lookups (3-key system)
│   │   ├── casting.py                 # generate_casting_key
│   │   └── validation.py              # Triple-key validation logic
│   │
│   ├── processors/                    # Process implementations
│   │   ├── __init__.py
│   │   ├── base_processor.py          # Abstract base class
│   │   ├── raw_processor.py           # Raw Process
│   │   ├── working_processor.py       # Working Process
│   │   ├── alllang_processor.py       # All Language Process
│   │   └── master_processor.py        # Master File Update
│   │
│   ├── io/                            # File I/O operations
│   │   ├── __init__.py
│   │   ├── excel_reader.py            # safe_read_excel, normalization
│   │   ├── excel_writer.py            # Write + formatting
│   │   └── formatters.py              # Color coding, styling
│   │
│   ├── history/                       # Update history management
│   │   ├── __init__.py
│   │   └── history_manager.py         # All history functions
│   │
│   ├── ui/                            # User interface
│   │   ├── __init__.py
│   │   ├── main_window.py             # Main GUI window
│   │   ├── history_viewer.py          # History viewer dialog
│   │   └── dialogs.py                 # File selection dialogs
│   │
│   └── utils/                         # Utility functions
│       ├── __init__.py
│       ├── helpers.py                 # log, safe_str, contains_korean
│       └── progress.py                # Progress bar utilities
│
├── tests/                             # Unit tests
│   ├── __init__.py
│   ├── test_comparison.py
│   ├── test_lookups.py
│   ├── test_validation.py
│   ├── test_raw_processor.py
│   ├── test_working_processor.py
│   ├── test_alllang_processor.py
│   └── test_master_processor.py
│
├── docs/                              # Documentation
│   ├── user_guide.md
│   ├── api_reference.md
│   └── development.md
│
├── main.py                            # Entry point
├── requirements.txt                   # Dependencies
├── README.md                          # Project readme
├── claude.md                          # Project overview (this file)
└── roadmap.md                         # This roadmap
```

### Refactoring Strategy

#### Step 1: Extract Configuration (Week 1, Day 1)
- Create `src/config.py`
- Move all constants (COL_*, OUTPUT_COLUMNS*, etc.)
- Update imports in main file

#### Step 2: Extract Utilities (Week 1, Day 2)
- Create `src/utils/helpers.py`
  - Move: `log()`, `safe_str()`, `contains_korean()`, `get_script_dir()`
- Create `src/utils/progress.py`
  - Move: `print_progress()`, `finalize_progress()`
- Update imports

#### Step 3: Extract I/O Layer (Week 1, Day 3-4)
- Create `src/io/excel_reader.py`
  - Move: `safe_read_excel()`, `normalize_dataframe_status()`, `clean_numeric_columns()`, `clean_dataframe_none_values()`
- Create `src/io/excel_writer.py`
  - Move: `filter_output_columns()`, writing logic
- Create `src/io/formatters.py`
  - Move: `apply_direct_coloring()`, `generate_color_for_value()`, `widen_summary_columns()`, `format_update_history_sheet()`
- Update imports

#### Step 4: Extract Core Logic (Week 1, Day 5)
- Create `src/core/lookups.py`
  - Move: `build_lookups()`, `build_working_lookups()`
- Create `src/core/casting.py`
  - Move: `generate_casting_key()`, `generate_previous_data()`
- Create `src/core/validation.py`
  - Move: Triple-key validation logic
  - Create: `is_new_row()`, `is_deleted_row()` helper functions
- Update imports

#### Step 5: Extract Comparison Logic (Week 2, Day 1-2)
- Create `src/core/comparison.py`
  - Move: `compare_rows()`, `classify_change()`, `classify_working_change()`, `classify_alllang_change()`
  - Move: `find_deleted_rows()`, `find_working_deleted_rows()`
  - Refactor to reduce duplication
- Update imports

#### Step 6: Extract History Management (Week 2, Day 3)
- Create `src/history/history_manager.py`
  - Move: All history functions (get_history_file_path, load/save, add_*_record, clear, delete)
- Update imports

#### Step 7: Create Base Processor (Week 2, Day 4)
- Create `src/processors/base_processor.py`
  - Define abstract base class with common methods:
    - `select_files()`: File selection dialog
    - `read_files()`: Excel reading with error handling
    - `build_lookups()`: Wrapper for lookup building
    - `write_output()`: Excel writing with formatting
    - `show_summary()`: Summary dialog
  - Template method pattern for `process()`

#### Step 8: Refactor Processors (Week 2, Day 5 - Week 3, Day 3)
- Create `src/processors/raw_processor.py`
  - Extend base class
  - Move: `process_raw_vrs_check()` logic
  - Move: `create_raw_summary()`
- Create `src/processors/working_processor.py`
  - Extend base class
  - Move: `process_working_vrs_check()` logic
  - Move: `apply_import_logic()`, `create_working_summary()`, `create_working_update_history_sheet()`
- Create `src/processors/alllang_processor.py`
  - Extend base class
  - Move: `process_all_language_check()` logic
  - Move: `find_alllang_files()`, `merge_current_files()`, `apply_import_logic_alllang_lang()`, `create_alllang_summary()`, `create_alllang_update_history_sheet()`
- Create `src/processors/master_processor.py`
  - Extend base class
  - Move: `process_master_file_update()` logic (**with Phase 1 fixes applied**)
  - Move: `create_master_file_update_history_sheet()`

#### Step 9: Refactor UI (Week 3, Day 4-5)
- Create `src/ui/main_window.py`
  - Move: `create_gui()` logic
  - Split into smaller methods for better organization
- Create `src/ui/history_viewer.py`
  - Move: `show_update_history_viewer()`
- Create `src/ui/dialogs.py`
  - Common dialog utilities
- Move thread functions to processor classes

#### Step 10: Create Entry Point (Week 4, Day 1)
- Create `main.py`
  - Simple entry point that imports and runs GUI
- Create `requirements.txt`
  - List all dependencies
- Update documentation

#### Step 11: Add Unit Tests (Week 4, Day 2-4)
- Test utilities (helpers, progress)
- Test I/O layer (reading, writing, formatting)
- Test core logic (lookups, validation, comparison)
- Test processors (all 4 processes)
- Aim for >80% code coverage

#### Step 12: Final Integration & Testing (Week 4, Day 5)
- Integration testing with real data
- Performance testing
- User acceptance testing
- Documentation review

### Benefits After Restructuring

| Aspect | Before | After |
|--------|--------|-------|
| **File Size** | 1 file, 2,633 lines | ~20 files, <200 lines each |
| **Testability** | Cannot unit test | >80% coverage |
| **Maintainability** | Hard to navigate | Clear module boundaries |
| **Extensibility** | Requires editing monolith | Add new processor class |
| **Code Reuse** | Lots of duplication | Shared base class + utilities |
| **IDE Support** | Limited | Full autocomplete + navigation |
| **Team Collaboration** | Merge conflicts likely | Multiple people can work independently |

### Estimated Effort
- **Week 1**: Configuration, Utilities, I/O, Core Logic (5 days)
- **Week 2**: Comparison, History, Base Processor, Start Processors (5 days)
- **Week 3**: Finish Processors, UI (5 days)
- **Week 4**: Entry Point, Tests, Integration (5 days)
- **Total**: 20 days (1 developer, full-time)

### Risk Mitigation
1. **Keep original file**: Don't delete `vrsmanager1114.py` until fully tested
2. **Incremental migration**: Move one module at a time
3. **Continuous testing**: Run manual tests after each step
4. **Version control**: Use git branches for each major step
5. **Rollback plan**: Tag working versions for easy rollback

---

## Phase 3: Future Enhancements (Post-Restructuring)

### 3.1 Performance Optimization
- Use chunking for large Excel files
- Parallel processing for multi-language updates
- Caching for repeated lookups

### 3.2 Advanced Features
- Undo/Redo for Master File updates
- Diff viewer for side-by-side comparison
- Export to other formats (CSV, JSON, SQL)
- API for programmatic access

### 3.3 Quality of Life
- Drag-and-drop file selection
- Recent files list
- Configurable color schemes
- Keyboard shortcuts
- Dark mode

### 3.4 Validation & Safety
- Pre-flight validation checks
- Backup before overwrite
- Conflict resolution UI
- Data integrity checks

---

## Summary

### Immediate Priority (This Sprint)
**Phase 1**: Fix LOW importance logic in Master File Update (3 hours)

### Next Priority (Next Sprint)
**Phase 2**: Restructure codebase into maintainable tree (20 days)

### Future Enhancements
**Phase 3**: Performance, features, UX improvements (ongoing)

---

## Decision Points

### Should we do Phase 1 before Phase 2?
**YES** - Reasons:
1. Phase 1 is critical bug fix for current users
2. Phase 1 is small (3 hours) vs Phase 2 (20 days)
3. Phase 1 changes will be migrated during Phase 2
4. Easier to test Phase 1 fix in isolation first

### Should we do Phase 2 at all?
**YES** - Reasons:
1. Code is already hard to maintain at 2,633 lines
2. Version number (1114) suggests active development
3. Adding more features to monolith will make it worse
4. Investment now saves exponential time later
5. Team collaboration requires modular structure

### Recommended Approach
1. **Sprint 1** (1 day): Implement Phase 1 fixes, test thoroughly
2. **Sprint 2-5** (4 weeks): Execute Phase 2 restructuring
3. **Sprint 6+**: Phase 3 enhancements based on user feedback
