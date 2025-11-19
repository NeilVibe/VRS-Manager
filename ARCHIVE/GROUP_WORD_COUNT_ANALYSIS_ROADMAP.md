# Group Word Count Analysis - Implementation Roadmap

## 🎯 Executive Summary

### Problem Statement
Currently, the VRS Manager provides **100% accurate total word count differences** at the file level. However, when content moves between Groups (e.g., 1000 words moving from "Chapter3" to "Chapter6"), the system cannot track:
- Which groups lost words (deletions within group)
- Which groups gained words (additions within group)
- Which groups had word changes (modifications within group)

This makes it difficult for stakeholders to understand word count changes at the **group level**.

### Goal
Add a **new analysis sheet** called "Group Word Analysis" that tracks word count changes (additions, deletions, modifications) at the Group level, providing granular visibility into how content shifts between groups.

**Key Constraint**: Keep existing 10-key system intact (it's working perfectly). Only ADD group tracking layer on top.

---

## 📊 Current State Analysis

### What We Have ✅
1. **10-Key Matching System**: 100% accurate row-level change detection
   - Keys: Sequence, EventName, StrOrigin, CastingKey
   - 10 combination patterns for matching
   - TWO-PASS algorithm prevents 1-to-many matching

2. **Word Count Metric**: Based on `StrOrigin` field
   - Word count = number of words in StrOrigin value (space-separated)
   - Already 100% accurate at file level

3. **Change Classifications**: All working correctly
   - No Change, New Row, Deleted Row
   - StrOrigin Change, CastingKey Change, EventName Change, etc.
   - Composite changes (StrOrigin+Desc Change, etc.)

### What We're Adding 🎯
1. **Group Column**: Already exists in production files
   - Column name: "Group"
   - Values: "Intro", "Prolog", "Chapter1", "Chapter2", ..., "Final Chapter"
   - Voice actors use this to filter and organize their work

2. **Group-Level Tracking**: NEW feature to add
   - Track word counts per group
   - Detect group migrations (words moving between chapters)
   - Show additions/deletions/changes per group

### Production File Structure (Confirmed)
```
Production Files:
- Group column: ✅ EXISTS (column name: "Group")
- Values: Chapter names and categories (e.g., "Intro", "Chapter1", "Chapter3", "Chapter6", "Final Chapter")
- Lines can move between groups (e.g., Chapter3 → Chapter6)
```

---

## 🧮 Mathematical Analysis

### Word Count Calculation
```
word_count(row) = len(StrOrigin.split())
```

### Group-Level Metrics Needed
For each Group G in (Previous ∪ Current):
1. **Total Words (Previous)**: Sum of word counts for all rows in Group G in previous file
2. **Total Words (Current)**: Sum of word counts for all rows in Group G in current file
3. **Words Deleted**: Word count from rows that existed in Previous[G] but not in Current[G]
4. **Words Added**: Word count from rows that exist in Current[G] but not in Previous[G]
5. **Words Changed**: Word count from rows in Current[G] that match Previous[G] but StrOrigin changed
6. **Net Change**: (Current - Previous) = Added - Deleted ± Changed

### Matching Logic with Group

**Current 10-Key System:**
- Matches rows using: (S, E, O, C) combinations
- Does NOT consider Group

**Proposed 11-Key System:**
- Add Group (G) to the identification process
- New keys include: (G, S), (G, O), (G, E), (G, C), (G, S, E), (G, S, O), etc.

**Problem with 11-Key Approach:**
- If Group changes (Chapter3 → Faction3), the row won't match
- This is actually CORRECT for group-level analysis!
- We WANT to treat group migrations as "Delete from old group" + "Add to new group"

---

## 🎨 Proposed Solution Architecture

### Option A: Extend 10-Key System with Group Context (RECOMMENDED)
**Strategy**: Keep 10-key matching for row identity, but track group membership separately

**Algorithm:**
```
For each row in Current:
    1. Match using existing 10-key system → get matched Previous row (if any)
    2. Extract Group_current from current row
    3. Extract Group_previous from matched row (if match found)
    4. Classify:
        a. If NO match found → "New Row in Group_current"
        b. If match found AND Group_current == Group_previous:
            - If StrOrigin unchanged → "No Change in Group_current"
            - If StrOrigin changed → "Modified in Group_current"
        c. If match found AND Group_current != Group_previous:
            - Treat as "Deleted from Group_previous"
            - Treat as "Added to Group_current"
            - This is a GROUP MIGRATION

For each row in Previous not matched:
    Extract Group_previous → "Deleted from Group_previous"
```

**Advantages:**
- Leverages existing 10-key system (proven accurate)
- Cleanly separates row identity from group membership
- Correctly handles group migrations
- No changes to core comparison logic

**Data Structure:**
```python
group_analysis = {
    "Chapter3": {
        "total_words_prev": 15000,
        "total_words_curr": 14000,
        "deleted_words": 1500,  # Includes migrations out
        "added_words": 500,     # Includes migrations in
        "changed_words": 200,   # StrOrigin modifications
        "net_change": -1000
    },
    "Faction3": {
        "total_words_prev": 5000,
        "total_words_curr": 6000,
        "deleted_words": 100,
        "added_words": 1100,    # Includes migrations in
        "changed_words": 50,
        "net_change": +1000
    }
}
```

### Option B: Create Separate Group-Aware Matching System
**Strategy**: Run a parallel analysis using Group as primary key

**Algorithm:**
```
Create separate lookups with Group as first key:
    - (G, S, E, O, C)
    - (G, S, E, O)
    - (G, S, O, C)
    - etc.

Match rows within same group only
Track group-level statistics
```

**Disadvantages:**
- Duplicates matching logic
- More complex to maintain
- Requires significant refactoring

---

## ✅ Recommended Solution: Option A

### Implementation Plan

#### Phase 1: Data Discovery & Validation
**Goal**: Understand where Group column comes from and ensure it's available

**Tasks:**
1. ✅ Examine test files for Group column → **NOT FOUND**
2. ❓ Check production files for Group column → **NEED USER INPUT**
3. ❓ Determine if Group is:
   - Already in source files?
   - Derived from another column?
   - Added during processing?
4. ❓ Understand Group naming conventions and possible values

**Questions for User:**
- Where does the "Group" column come from in your production files?
- Is it present in the raw input files, or is it added during processing?
- What are typical Group names? (e.g., "Chapter3", "Faction3", etc.)
- Are Groups unique identifiers or can they have duplicates?

#### Phase 2: Core Algorithm Extension
**Goal**: Extend comparison.py to track group membership

**Files to Modify:**
- `src/core/comparison.py`
- `src/config.py` (add COL_GROUP constant)

**Changes to comparison.py:**

```python
# In config.py
COL_GROUP = "Group"

# In comparison.py - modify compare_rows() function
def compare_rows(df_curr, df_prev, prev_lookup_se, ..., prev_lookup_eoc):
    """
    Compare rows using TWO-PASS algorithm with 10-key pattern matching.
    NOW ALSO TRACKS GROUP MEMBERSHIP for word count analysis.
    """
    changes = []
    previous_strorigins = []
    changed_columns_map = {}
    counter = {}
    marked_prev_indices = set()

    # NEW: Group-level tracking
    group_analysis = {}  # group_name → statistics

    # ... existing PASS 1 and PASS 2 logic ...

    # NEW: After matching, extract group information
    for curr_idx, curr_row in df_curr.iterrows():
        curr_group = safe_str(curr_row.get(COL_GROUP, "Unknown"))
        curr_words = len(safe_str(curr_row[COL_STRORIGIN]).split())

        # Initialize group if not exists
        if curr_group not in group_analysis:
            group_analysis[curr_group] = {
                "total_words_curr": 0,
                "total_words_prev": 0,
                "deleted_words": 0,
                "added_words": 0,
                "changed_words": 0,
                "unchanged_words": 0,
                "migrated_in_words": 0,
                "migrated_out_words": 0
            }

        change_label, prev_idx, prev_strorigin, _ = pass1_results[curr_idx]

        if change_label == "New Row":
            # New row in this group
            group_analysis[curr_group]["added_words"] += curr_words
            group_analysis[curr_group]["total_words_curr"] += curr_words

        elif prev_idx is not None:
            prev_row = df_prev.loc[prev_idx]
            prev_group = safe_str(prev_row.get(COL_GROUP, "Unknown"))
            prev_words = len(safe_str(prev_row[COL_STRORIGIN]).split())

            # Initialize previous group if needed
            if prev_group not in group_analysis:
                group_analysis[prev_group] = {
                    "total_words_curr": 0,
                    "total_words_prev": 0,
                    "deleted_words": 0,
                    "added_words": 0,
                    "changed_words": 0,
                    "unchanged_words": 0,
                    "migrated_in_words": 0,
                    "migrated_out_words": 0
                }

            group_analysis[prev_group]["total_words_prev"] += prev_words
            group_analysis[curr_group]["total_words_curr"] += curr_words

            if curr_group == prev_group:
                # Same group - check for changes
                if "StrOrigin" in change_label:
                    group_analysis[curr_group]["changed_words"] += curr_words
                else:
                    group_analysis[curr_group]["unchanged_words"] += curr_words
            else:
                # GROUP MIGRATION DETECTED
                group_analysis[prev_group]["migrated_out_words"] += prev_words
                group_analysis[curr_group]["migrated_in_words"] += curr_words

    # Process deleted rows
    deleted_indices = [idx for idx in df_prev.index if idx not in marked_prev_indices]
    for del_idx in deleted_indices:
        del_row = df_prev.loc[del_idx]
        del_group = safe_str(del_row.get(COL_GROUP, "Unknown"))
        del_words = len(safe_str(del_row[COL_STRORIGIN]).split())

        if del_group not in group_analysis:
            group_analysis[del_group] = {
                "total_words_curr": 0,
                "total_words_prev": 0,
                "deleted_words": 0,
                "added_words": 0,
                "changed_words": 0,
                "unchanged_words": 0,
                "migrated_in_words": 0,
                "migrated_out_words": 0
            }

        group_analysis[del_group]["total_words_prev"] += del_words
        group_analysis[del_group]["deleted_words"] += del_words

    return changes, previous_strorigins, changed_columns_map, counter, marked_prev_indices, group_analysis
```

#### Phase 3: Excel Output - Group Word Analysis Sheet
**Goal**: Create new sheet with group-level statistics

**Files to Modify:**
- `src/io/excel_writer.py`
- Processor files that call excel_writer

**Sheet Structure:**
```
Sheet Name: "Group Word Analysis"

Columns:
1. Group Name
2. Total Words (Previous)
3. Total Words (Current)
4. Words Added (New Rows)
5. Words Deleted (Removed Rows)
6. Words Changed (StrOrigin Modified)
7. Words Unchanged (No Change)
8. Words Migrated In (From Other Groups)
9. Words Migrated Out (To Other Groups)
10. Net Change
11. % Change

Example Data:
| Group    | Prev  | Curr  | Added | Deleted | Changed | Unchanged | Migr In | Migr Out | Net    | % Chg  |
|----------|-------|-------|-------|---------|---------|-----------|---------|----------|--------|--------|
| Chapter3 | 15000 | 14000 | 500   | 1000    | 200     | 13300     | 0       | 1000     | -1000  | -6.7%  |
| Faction3 | 5000  | 6000  | 100   | 50      | 50      | 4800      | 1000    | 0        | +1000  | +20.0% |
| NEW_GRP  | 0     | 2000  | 2000  | 0       | 0       | 0         | 0       | 0        | +2000  | N/A    |
```

**Implementation:**

```python
# In excel_writer.py
def write_group_word_analysis(writer, group_analysis, sheet_name="Group Word Analysis"):
    """
    Write group-level word count analysis to Excel sheet.

    Args:
        writer: ExcelWriter object
        group_analysis: dict with group statistics
        sheet_name: name of sheet to create
    """
    # Convert to DataFrame
    rows = []
    for group_name, stats in sorted(group_analysis.items()):
        prev_total = stats["total_words_prev"]
        curr_total = stats["total_words_curr"]
        net_change = curr_total - prev_total

        if prev_total > 0:
            pct_change = (net_change / prev_total) * 100
        else:
            pct_change = None

        rows.append({
            "Group Name": group_name,
            "Total Words (Previous)": prev_total,
            "Total Words (Current)": curr_total,
            "Words Added": stats["added_words"],
            "Words Deleted": stats["deleted_words"],
            "Words Changed": stats["changed_words"],
            "Words Unchanged": stats["unchanged_words"],
            "Words Migrated In": stats["migrated_in_words"],
            "Words Migrated Out": stats["migrated_out_words"],
            "Net Change": net_change,
            "% Change": f"{pct_change:.2f}%" if pct_change is not None else "N/A"
        })

    df_group_analysis = pd.DataFrame(rows)

    # Write to Excel
    df_group_analysis.to_excel(writer, sheet_name=sheet_name, index=False)

    # Format worksheet
    worksheet = writer.sheets[sheet_name]

    # Set column widths
    worksheet.column_dimensions['A'].width = 25  # Group Name
    for col in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']:
        worksheet.column_dimensions[col].width = 15
    worksheet.column_dimensions['K'].width = 12  # % Change

    # Apply header formatting
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")

    for cell in worksheet[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # Apply number formatting
    for row in range(2, len(df_group_analysis) + 2):
        for col in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']:
            cell = worksheet[f"{col}{row}"]
            cell.number_format = '#,##0'

        # Net Change with color coding
        net_cell = worksheet[f"J{row}"]
        net_cell.number_format = '+#,##0;-#,##0;0'
        if net_cell.value and net_cell.value > 0:
            net_cell.font = Font(color="00B050")  # Green for positive
        elif net_cell.value and net_cell.value < 0:
            net_cell.font = Font(color="FF0000")  # Red for negative

    # Add summary row
    summary_row = len(df_group_analysis) + 3
    worksheet[f"A{summary_row}"] = "TOTAL"
    worksheet[f"A{summary_row}"].font = Font(bold=True)

    for col, col_name in [('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'),
                           ('F', 'F'), ('G', 'G'), ('H', 'H'), ('I', 'I'), ('J', 'J')]:
        worksheet[f"{col}{summary_row}"] = f"=SUM({col}2:{col}{len(df_group_analysis)+1})"
        worksheet[f"{col}{summary_row}"].font = Font(bold=True)
        worksheet[f"{col}{summary_row}"].number_format = '#,##0'
```

#### Phase 4: Integration with Processors
**Goal**: Wire up group analysis to all processor types

**Files to Modify:**
- `src/processors/raw_processor.py`
- `src/processors/master_processor.py`
- `src/processors/working_processor.py`
- `src/processors/alllang_processor.py`

**Changes:**
1. Update processor functions to receive and pass through group_analysis
2. Call `write_group_word_analysis()` after main output sheets
3. Add logging for group analysis statistics

```python
# Example in raw_processor.py
def process_raw_update(source_path, target_path, output_path, log_func=print):
    """Process RAW file update."""
    # ... existing code ...

    # Compare files
    changes, previous_strorigins, changed_columns_map, counter, marked_prev_indices, group_analysis = \
        compare_rows(df_curr, df_prev, prev_lookup_se, ..., prev_lookup_eoc)

    # ... existing output logic ...

    # Write group analysis sheet
    write_group_word_analysis(writer, group_analysis)

    # Log group analysis summary
    log_func("\n" + "="*60)
    log_func("GROUP WORD COUNT ANALYSIS")
    log_func("="*60)
    for group_name, stats in sorted(group_analysis.items()):
        net = stats["total_words_curr"] - stats["total_words_prev"]
        log_func(f"{group_name}: {stats['total_words_prev']:,} → {stats['total_words_curr']:,} ({net:+,} words)")
```

#### Phase 5: Testing & Validation
**Goal**: Ensure accuracy and correctness

**Test Cases:**

**Test 1: Basic Group Word Counting**
```
Setup:
- Group "Chapter1" in Previous: 3 rows with StrOrigin lengths [10, 15, 20] = 45 words
- Group "Chapter1" in Current: Same 3 rows (no changes)

Expected:
- Total Words (Previous): 45
- Total Words (Current): 45
- All other metrics: 0
```

**Test 2: Word Additions**
```
Setup:
- Group "Chapter1" in Previous: 2 rows [10, 15] = 25 words
- Group "Chapter1" in Current: 3 rows [10, 15, 12] = 37 words (1 new row)

Expected:
- Total Words (Previous): 25
- Total Words (Current): 37
- Words Added: 12
- Net Change: +12
```

**Test 3: Word Deletions**
```
Setup:
- Group "Chapter1" in Previous: 3 rows [10, 15, 20] = 45 words
- Group "Chapter1" in Current: 2 rows [10, 15] = 25 words (1 row deleted)

Expected:
- Total Words (Previous): 45
- Total Words (Current): 25
- Words Deleted: 20
- Net Change: -20
```

**Test 4: Word Changes (StrOrigin Modification)**
```
Setup:
- Group "Chapter1" in Previous: Row A with StrOrigin "안녕하세요 반갑습니다" = 2 words
- Group "Chapter1" in Current: Row A with StrOrigin "안녕하세요 반갑습니다 감사합니다" = 3 words

Expected:
- Words Changed: 3 (current word count)
- Net Change: +1
```

**Test 5: GROUP MIGRATION (Critical Test)**
```
Setup:
- Group "Chapter3" in Previous: Row X with StrOrigin = 50 words
- Group "Faction3" in Current: Same Row X (matched by 10-key) with StrOrigin = 50 words

Expected for Chapter3:
- Total Words (Previous): 50
- Total Words (Current): 0
- Words Migrated Out: 50
- Net Change: -50

Expected for Faction3:
- Total Words (Previous): 0
- Total Words (Current): 50
- Words Migrated In: 50
- Net Change: +50
```

**Test 6: Complex Scenario**
```
Setup:
- Group "Chapter3" in Previous: 1000 rows totaling 15,000 words
- Group "Faction3" in Previous: 300 rows totaling 5,000 words
- In Current:
  - 200 rows from Chapter3 → moved to Faction3 (3,000 words)
  - 100 rows from Chapter3 → deleted (1,500 words)
  - 50 new rows added to Chapter3 (800 words)
  - 25 rows in Faction3 → StrOrigin changed (500 words changed)

Expected for Chapter3:
- Total Words (Previous): 15,000
- Total Words (Current): 15,000 - 3,000 - 1,500 + 800 = 11,300
- Words Deleted: 1,500
- Words Added: 800
- Words Migrated Out: 3,000
- Net Change: -3,700

Expected for Faction3:
- Total Words (Previous): 5,000
- Total Words (Current): 5,000 + 3,000 - (changed rows prev words) + (changed rows curr words)
- Words Changed: 500 (current count)
- Words Migrated In: 3,000
```

#### Phase 6: Documentation & User Guide
**Goal**: Enable users to understand and use the feature

**Documentation Needs:**
1. Update README.md with Group Word Analysis feature
2. Add section to VRS_Manager_Process_Guide
3. Create example screenshots of output
4. Document interpretation of metrics

**Key Points for Users:**
- **Words Migrated In/Out**: Indicates content moving between groups
- **Net Change**: Can be positive even if Words Deleted > 0 (due to migrations)
- **Total = Unchanged + Changed + Deleted (for Previous)**
- **Total = Unchanged + Changed + Added + Migrated In (for Current)**

---

## 🚀 Implementation Timeline

### Phase 1: Test File Creation (Day 1)
**Goal**: Create comprehensive test files WITH Group column

**Tasks**:
- [ ] **1.1**: Add Group column to test file generator
  - Modify script that creates test_comprehensive_PREVIOUS.xlsx
  - Modify script that creates test_comprehensive_CURRENT.xlsx
  - Add Groups: "Intro", "Prolog", "Chapter1", "Chapter2", "Chapter3", "Chapter4", "Chapter5", "Chapter6", "Final Chapter"

- [ ] **1.2**: Design test scenarios
  - Assign rows to groups in PREVIOUS file
  - Create scenarios in CURRENT file:
    * Some rows stay in same group (no change)
    * Some rows move between groups (Chapter3 → Chapter6 migration)
    * Some rows deleted from groups
    * Some new rows added to groups
    * Some rows with StrOrigin changes within same group

- [ ] **1.3**: Generate new test files
  - Run generator script
  - Validate Group column exists in both files
  - Validate test scenarios are present

**Output**: test_comprehensive_PREVIOUS.xlsx and test_comprehensive_CURRENT.xlsx WITH Group column

---

### Phase 2: Core Algorithm Extension (Day 1-2)
**Goal**: Extend comparison.py to track group membership (NO changes to 10-key matching logic)

**Tasks**:
- [ ] **2.1**: Update config.py
  - Add `COL_GROUP = "Group"` constant

- [ ] **2.2**: Extend compare_rows() function in comparison.py
  - Add group_analysis dictionary to track statistics
  - After existing TWO-PASS logic, extract Group from current and previous rows
  - Count words per group (word_count = len(StrOrigin.split()))
  - Classify into: added, deleted, changed, unchanged, migrated_in, migrated_out
  - Return group_analysis as 6th return value

- [ ] **2.3**: Update function signature
  - Old: `return changes, previous_strorigins, changed_columns_map, counter, marked_prev_indices`
  - New: `return changes, previous_strorigins, changed_columns_map, counter, marked_prev_indices, group_analysis`

**Output**: comparison.py returns group_analysis dictionary

---

### Phase 3: Excel Output Sheet (Day 2)
**Goal**: Create "Group Word Analysis" sheet in output Excel files

**Tasks**:
- [ ] **3.1**: Implement write_group_word_analysis() in excel_writer.py
  - Convert group_analysis dict to DataFrame
  - Columns: Group Name, Total Words (Prev), Total Words (Curr), Words Added, Words Deleted, Words Changed, Words Migrated In, Words Migrated Out, Net Change, % Change
  - Add formatting (colors, number formats, bold headers)
  - Add summary row with totals

- [ ] **3.2**: Add helper function for word count formatting
  - Format large numbers with commas (e.g., 15,000)
  - Color code positive (green) and negative (red) changes

**Output**: New function in excel_writer.py ready to use

---

### Phase 4: Integration with Processors (Day 2-3)
**Goal**: Wire group_analysis through all processor types

**Tasks**:
- [ ] **4.1**: Update raw_processor.py
  - Update compare_rows() call to receive 6 return values (add group_analysis)
  - Call write_group_word_analysis(writer, group_analysis) after main sheets
  - Add logging for group statistics

- [ ] **4.2**: Update master_processor.py
  - Same changes as raw_processor.py

- [ ] **4.3**: Update working_processor.py
  - Same changes as raw_processor.py

- [ ] **4.4**: Update alllang_processor.py
  - Same changes as raw_processor.py

**Output**: All processors now output "Group Word Analysis" sheet

---

### Phase 5: Update Comprehensive Test (Day 3)
**Goal**: Extend test_comprehensive_twopass.py to validate group word counts

**Tasks**:
- [ ] **5.1**: Update test to receive group_analysis
  - Modify line 91-96 to capture 6 return values

- [ ] **5.2**: Add Group Word Count validation section
  - PHASE 10: Validate group word counts
  - Check expected vs actual for each group
  - Validate migrations are detected correctly
  - Validate totals match file-level totals

- [ ] **5.3**: Add expected counts for groups
  - Define expected word counts for each group in test
  - Define expected migrations (e.g., Chapter3 → Chapter6)
  - Assert all match

**Output**: test_comprehensive_twopass.py validates group analysis

---

### Phase 6: Testing & Validation (Day 3-4)
**Goal**: Run comprehensive tests and validate accuracy

**Tasks**:
- [ ] **6.1**: Run comprehensive test
  - Execute: `python3 tests/test_comprehensive_twopass.py`
  - Verify all existing tests still pass (no regression)
  - Verify new group validation passes

- [ ] **6.2**: Manual validation
  - Open output Excel file
  - Check "Group Word Analysis" sheet exists
  - Verify numbers are accurate
  - Verify formatting is correct

- [ ] **6.3**: Run on production-like data
  - Test with larger files
  - Verify performance is acceptable
  - Check edge cases (missing Group values, etc.)

**Output**: All tests passing, feature validated

---

### Phase 7: Documentation & Release (Day 4)
**Goal**: Document feature and prepare for release

**Tasks**:
- [ ] **7.1**: Update README.md
  - Add "Group Word Analysis" to features list
  - Add example screenshot or description

- [ ] **7.2**: Update VRS_Manager_Process_Guide
  - Add section explaining new sheet
  - Explain how to interpret metrics
  - Document migration detection

- [ ] **7.3**: Update version
  - Bump VERSION in config.py to next version (e.g., "1118.1")
  - Update VERSION_FOOTER with new feature description

- [ ] **7.4**: Git commit
  - Commit all changes with descriptive message
  - Tag release if needed

**Output**: Feature complete, documented, and released

---

**Total Estimated Time: 4 days**

---

## ⚠️ Risks & Mitigations

### Risk 1: Group Column Not Available
**Impact**: Cannot implement feature
**Mitigation**:
- Determine if Group can be derived from existing columns
- Add Group assignment logic if needed
- Fall back to derived grouping (e.g., by SequenceName prefix)

### Risk 2: Group Migrations Misclassified
**Impact**: Incorrect word count attribution
**Mitigation**:
- Extensive testing of migration scenarios
- Clear documentation of expected behavior
- User validation with real data

### Risk 3: Performance Impact
**Impact**: Slower processing for large files
**Mitigation**:
- Group tracking is O(n) complexity (same as existing)
- Minimal performance impact expected
- Can optimize if needed

### Risk 4: Group Column Inconsistencies
**Impact**: Missing or incorrect group assignments
**Mitigation**:
- Default to "Unknown" group for missing values
- Log warnings for missing group data
- Provide data validation tools

---

## 📈 Success Metrics

### Accuracy Targets
- ✅ 100% accurate total word count (already achieved)
- 🎯 100% accurate group-level word count
- 🎯 Correct migration detection (validated by user review)

### Usability Targets
- 🎯 Clear, intuitive sheet layout
- 🎯 Color-coded positive/negative changes
- 🎯 Summary row shows file-level totals
- 🎯 Matches existing file-level word count

### Performance Targets
- 🎯 < 5% processing time increase
- 🎯 Excel file size increase < 100KB

---

## 📝 Test File Creation Strategy

### Current Test File Generation
The comprehensive test files are currently created manually or via a separate script. They contain:
- 850 rows in PREVIOUS file
- 850 rows in CURRENT file
- Test scenarios for duplicates, changes, new rows, deleted rows
- 11 columns (no Group column currently)

### How to Add Group Column

**Option A: Manually edit existing files** (Quick)
1. Open test_comprehensive_PREVIOUS.xlsx in Excel
2. Insert new column "Group" after column A
3. Assign groups to rows (pattern below)
4. Save file
5. Repeat for test_comprehensive_CURRENT.xlsx with different assignments (to create migrations)

**Option B: Create Python script to add Group column** (Recommended)
```python
# Script: tests/add_group_column_to_tests.py
import pandas as pd

# Read existing test files
df_prev = pd.read_excel('tests/test_comprehensive_PREVIOUS.xlsx')
df_curr = pd.read_excel('tests/test_comprehensive_CURRENT.xlsx')

# Define groups (cycle through them)
groups = ["Intro", "Prolog", "Chapter1", "Chapter2", "Chapter3", "Chapter4", "Chapter5", "Chapter6", "Final Chapter"]

# Assign groups to PREVIOUS (simple distribution)
group_assignments_prev = []
for i in range(len(df_prev)):
    group_idx = (i // 95) % len(groups)  # ~95 rows per group
    group_assignments_prev.append(groups[group_idx])

df_prev.insert(1, 'Group', group_assignments_prev)  # Insert after first column

# Assign groups to CURRENT with some migrations
group_assignments_curr = []
for i in range(len(df_curr)):
    # Most rows keep same group
    prev_group = group_assignments_prev[i] if i < len(group_assignments_prev) else "Intro"

    # Create migrations: Move some Chapter3 rows to Chapter6
    if prev_group == "Chapter3" and i % 10 == 0:  # Every 10th Chapter3 row
        group_assignments_curr.append("Chapter6")  # MIGRATION!
    else:
        group_assignments_curr.append(prev_group)

df_curr.insert(1, 'Group', group_assignments_curr)

# Save updated files
df_prev.to_excel('tests/test_comprehensive_PREVIOUS.xlsx', index=False)
df_curr.to_excel('tests/test_comprehensive_CURRENT.xlsx', index=False)

print(f"✓ Added Group column to test files")
print(f"  PREVIOUS: {len(df_prev)} rows, Groups: {df_prev['Group'].unique()}")
print(f"  CURRENT: {len(df_curr)} rows, Groups: {df_curr['Group'].unique()}")
```

**Test Scenario Design**:
- **Intro**: 95 rows, stable (no changes)
- **Prolog**: 95 rows, 5 deletions
- **Chapter1**: 95 rows, 5 new additions
- **Chapter2**: 95 rows, 10 StrOrigin changes
- **Chapter3**: 95 rows, 10 rows MIGRATE to Chapter6
- **Chapter4**: 95 rows, stable
- **Chapter5**: 95 rows, 5 deletions + 5 additions
- **Chapter6**: 95 rows + 10 migrated from Chapter3 = 105 rows
- **Final Chapter**: 95 rows, stable

This creates a realistic test with migrations, additions, deletions, and changes.

---

## 📋 Quick Start Checklist

Ready to implement? Follow these steps in order:

### ✅ Step 1: Create Test Files with Group Column
```bash
# Create script to add Group column to test files
# Run: python3 tests/add_group_column_to_tests.py
```

### ✅ Step 2: Update config.py
```python
# Add to config.py
COL_GROUP = "Group"
```

### ✅ Step 3: Extend comparison.py
```python
# Modify compare_rows() to return group_analysis as 6th value
# Add group tracking logic after TWO-PASS algorithm
```

### ✅ Step 4: Create excel_writer.py function
```python
# Add write_group_word_analysis() function
# Formats and writes "Group Word Analysis" sheet
```

### ✅ Step 5: Update all processors
```python
# Update raw_processor.py, master_processor.py, working_processor.py, alllang_processor.py
# Add group_analysis to compare_rows() calls
# Call write_group_word_analysis()
```

### ✅ Step 6: Update test_comprehensive_twopass.py
```python
# Add validation for group word counts
# Check migrations are detected correctly
```

### ✅ Step 7: Run Tests
```bash
python3 tests/test_comprehensive_twopass.py
```

### ✅ Step 8: Validate Output
- Check Excel output has "Group Word Analysis" sheet
- Verify numbers are accurate
- Verify formatting looks good

### ✅ Step 9: Update Documentation
- Update README.md
- Update VRS_Manager_Process_Guide
- Bump version number

### ✅ Step 10: Commit & Release
```bash
git add .
git commit -m "Add Group Word Count Analysis feature"
```

---

## 🏁 Conclusion

This roadmap provides a **mathematically sound**, **technically feasible**, and **minimally invasive** approach to adding Group-level word count analysis to VRS Manager.

**Key Strengths:**
- ✅ **Zero changes to 10-key system** (keeps 100% accuracy intact)
- ✅ **Correctly handles group migrations** (Chapter3 → Chapter6)
- ✅ **Clear, actionable metrics** for voice actors and managers
- ✅ **Simple implementation** (4 days, 7 phases)
- ✅ **Fully testable** (comprehensive test suite)

**Implementation Approach:**
- Add Group tracking layer ON TOP of existing 10-key matching
- Track word counts per group using StrOrigin word count
- Detect migrations when matched row has different Group value
- Output new "Group Word Analysis" sheet with statistics

**Next Step:**
🚀 **START with Phase 1**: Create test files with Group column, then proceed through phases 2-7.

---

## 📊 Phase 2.2: Translation Status Tracking (UPCOMING)

### Problem Statement
Voice actors and project managers need to track translation progress at the group and super group level. Currently, there's no visibility into:
- How many words in each group are translated vs untranslated
- What percentage of each super group has been translated
- Which groups need translation work

### Solution: Add Translation Metrics to Group/Super Group Analysis

#### Data Source
**Column**: `Text` (existing column in production files)
**Logic**:
- If `Text` contains "NO TRANSLATION" (case-insensitive) → **Not Translated**
- Otherwise → **Translated**

#### New Metrics to Add

**For Group Word Analysis sheet:**
```
Current metrics:
- Total Words (Previous)
- Total Words (Current)
- Words Added, Deleted, Changed, Unchanged
- Words Migrated In/Out
- Net Change
- % Change

NEW metrics to add:
- Translated Words (Current): Count of words where Text does NOT contain "no translation"
- Untranslated Words (Current): Count of words where Text contains "no translation"
- Translation %: (Translated Words / Total Words Current) × 100
```

**For Super Group Word Analysis sheet:**
```
Same new metrics:
- Translated Words (Current)
- Untranslated Words (Current)
- Translation %
```

#### Implementation Plan

**Step 1: Update Group/Super Group Tracking Logic**

In `src/core/comparison.py` (group tracking section):
```python
# NEW: Add translation tracking
from src.config import COL_TEXT  # New constant

# In group tracking loop
for curr_idx, curr_row in df_curr.iterrows():
    curr_group = safe_str(curr_row.get(COL_GROUP, "Unknown"))
    curr_strorigin = safe_str(curr_row.get(COL_STRORIGIN, ""))
    curr_words = len(curr_strorigin.split()) if curr_strorigin else 0

    # NEW: Check translation status
    curr_text = safe_str(curr_row.get(COL_TEXT, "")).lower()
    is_translated = "no translation" not in curr_text

    # Initialize group if not exists
    if curr_group not in group_analysis:
        group_analysis[curr_group] = {
            # ... existing fields ...
            "translated_words": 0,        # NEW
            "untranslated_words": 0       # NEW
        }

    # Track translation status
    if is_translated:
        group_analysis[curr_group]["translated_words"] += curr_words
    else:
        group_analysis[curr_group]["untranslated_words"] += curr_words
```

**Step 2: Update Super Group Aggregation**

In `src/utils/super_groups.py` → `aggregate_to_super_groups()`:
```python
# Initialize super group stats with new fields
super_group_stats[sg] = {
    # ... existing fields ...
    "translated_words": 0,        # NEW
    "untranslated_words": 0       # NEW
}

# In processing loop
curr_text = safe_str(curr_row.get(COL_TEXT, "")).lower()
is_translated = "no translation" not in curr_text

if is_translated:
    super_group_stats[super_group]["translated_words"] += curr_words
else:
    super_group_stats[super_group]["untranslated_words"] += curr_words
```

**Step 3: Update Excel Output Functions**

In `src/io/excel_writer.py`:

Update `write_group_word_analysis()`:
```python
rows.append({
    # ... existing columns ...
    "Translated Words": stats["translated_words"],         # NEW
    "Untranslated Words": stats["untranslated_words"],     # NEW
    "Translation %": f"{pct_translated:.1f}%"              # NEW
})

# Calculate translation %
if curr_total > 0:
    pct_translated = (stats["translated_words"] / curr_total) * 100
else:
    pct_translated = 0.0
```

Update `write_super_group_word_analysis()` identically.

**Step 4: Update Column Definitions**

In `src/config.py`:
```python
# Add new constant
COL_TEXT = "Text"
```

**Step 5: Update Column Widths and Formatting**

In `src/io/excel_writer.py`:
```python
column_widths = {
    'A': 20,   # Group Name
    'B': 18,   # Total Words (Previous)
    'C': 18,   # Total Words (Current)
    'D': 14,   # Words Added
    'E': 14,   # Words Deleted
    'F': 14,   # Words Changed
    'G': 14,   # Words Unchanged
    'H': 16,   # Words Migrated In
    'I': 16,   # Words Migrated Out
    'J': 14,   # Net Change
    'K': 12,   # % Change
    'L': 16,   # Translated Words (NEW)
    'M': 16,   # Untranslated Words (NEW)
    'N': 14    # Translation % (NEW)
}
```

#### Expected Output

**Group Word Analysis sheet (with 3 new columns):**
```
Group Name | Total (Prev) | Total (Curr) | Added | Deleted | Changed | Unchanged | Migrated In | Migrated Out | Net | % | Translated | Untranslated | Trans %
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Chapter1   |    1,000     |    1,050     |  100  |   50    |   200   |    800    |      0      |      0       | +50 | +5% |     900    |     150      |  85.7%
Chapter2   |    1,200     |    1,200     |   50  |   50    |   100   |  1,050    |      0      |      0       |  +0 |  0% |   1,150    |      50      |  95.8%
```

**Super Group Word Analysis sheet (with 3 new columns):**
```
Super Group Name | Total (Prev) | Total (Curr) | Added | Deleted | Changed | Unchanged | Migrated In | Migrated Out | Net | % | Translated | Untranslated | Trans %
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Main Chapters    |   12,000     |   12,500     |  600  |  100    |  400    |  11,500   |      0      |      0       | +500| +4% |   10,500   |    2,000     |  84.0%
Quest Dialog     |    2,000     |    2,200     |  300  |  100    |  200    |   1,900   |      0      |      0       | +200| +10%|    2,100   |      100     |  95.5%
```

#### Testing Plan

1. **Update test file generator** (`tests/generate_5000row_test.py`):
   - Add `Text` column to generated rows
   - ~70% rows: Normal text (translated)
   - ~30% rows: "NO TRANSLATION" (untranslated)
   - Vary by group (some groups 100% translated, others 50%)

2. **Update comprehensive test** (`tests/test_5000row_comprehensive.py`):
   - Validate translation counts are accurate
   - Check translation % calculations
   - Verify totals: Translated + Untranslated = Total Words Current

3. **Expected test output**:
```
Translation Status Validation:
  ✓ Chapter1 translated: 850 / 1,000 words (85.0%)
  ✓ Chapter2 translated: 1,150 / 1,200 words (95.8%)
  ✓ Total translated: 12,500 / 18,000 words (69.4%)
  ✓ Translation totals match: Translated + Untranslated = Total ✓
```

#### Benefits

1. **For Voice Actors**:
   - See exactly which groups need translation work
   - Track translation progress by chapter/faction
   - Prioritize work on groups with low translation %

2. **For Project Managers**:
   - High-level view via Super Group Translation %
   - Track translation velocity (% change over time)
   - Identify bottlenecks (groups with 0% or low translation)

3. **For Stakeholders**:
   - Single metric: "84% of Main Chapters translated"
   - Easy to understand and report
   - Actionable data for resource allocation

#### Implementation Timeline

- **Estimated Time**: 1-2 days
- **Complexity**: Low (simple column check + aggregation)
- **Risk**: Very low (additive feature, doesn't change existing logic)

#### Validation Criteria

✅ Translation counts are 100% accurate (Translated + Untranslated = Total Words Current)
✅ Translation % calculation is correct for all groups
✅ Translation % calculation is correct for all super groups
✅ Edge case: Groups with 0 words show "N/A" or "0.0%" for Translation %
✅ Case-insensitive search works correctly ("no translation", "NO TRANSLATION", "No Translation" all detected)
✅ Excel output is properly formatted with new columns
✅ Column widths are appropriate for new data

---

**Next Steps After Phase 2.2**:
1. Consider adding translation status tracking to the main Comparison sheet
2. Consider adding "Translation Changed" as a new change type
3. Consider tracking translation % over time (historical data)

---

**Document Version**: 2.1
**Date**: 2025-11-17
**Author**: VRS Manager Development Team
**Status**: ✅ Ready to Implement (User Confirmed Group Column Exists)
