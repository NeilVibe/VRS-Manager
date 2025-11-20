# Processor Parity Analysis - RAW vs WORKING

**Date:** 2025-11-20
**Version:** v11201321
**Status:** ⚠️ WORKING PROCESSOR MISSING SUPER GROUP WORD ANALYSIS

---

## 🔍 FINDINGS

### Current State Comparison

| Feature | RAW Processor | WORKING Processor | Status |
|---------|---------------|-------------------|--------|
| **StrOrigin Analysis Sheet** | ✅ Implemented | ✅ Implemented | ✅ **PARITY** |
| **Super Group Word Analysis Sheet** | ✅ Implemented | ❌ **MISSING** | ❌ **GAP FOUND** |

---

## 📊 DETAILED ANALYSIS

### 1. StrOrigin Analysis - ✅ BOTH PROCESSORS HAVE THIS

**RAW Processor:** `src/processors/raw_processor.py:166-260`
```python
def create_strorigin_analysis_sheet(self):
    # Filters rows where CHANGES contains "StrOrigin"
    # Uses StrOriginAnalyzer (BERT or LIGHT version)
    # Creates: Previous StrOrigin | Current StrOrigin | Analysis | Diff Detail
    # Returns DataFrame with analyzed rows
```

**WORKING Processor:** `src/processors/working_processor.py:162-270`
```python
def create_strorigin_analysis_sheet(self):
    # IDENTICAL LOGIC to RAW processor
    # Filters rows where CHANGES contains "StrOrigin"
    # Uses StrOriginAnalyzer (BERT or LIGHT version)
    # Creates: Previous StrOrigin | Current StrOrigin | Analysis | Diff Detail
    # Returns DataFrame with analyzed rows
```

**Conclusion:** ✅ **FULLY IMPLEMENTED IN BOTH** - No action needed

---

### 2. Super Group Word Analysis - ❌ ONLY RAW HAS THIS

**RAW Processor:** `src/processors/raw_processor.py:279-291`
```python
def write_output(self):
    # ...
    if hasattr(self, 'pass1_results'):
        log("Generating Super Group Word Analysis...")
        super_group_analysis, migration_details = aggregate_to_super_groups(
            self.df_curr,
            self.df_prev,
            self.pass1_results  # ← KEY DATA from compare_rows()
        )
        write_super_group_word_analysis(writer, super_group_analysis, migration_details)
        log(f"  → {len(super_group_analysis)} super groups analyzed")
```

**Data Source:** RAW gets `pass1_results` from `compare_rows()` in `src/core/comparison.py`

```python
# RAW processor - process_data() line 132
changes, previous_strorigins, changed_columns_map, self.counter, marked_prev_indices, group_analysis, pass1_results = compare_rows(...)
self.pass1_results = pass1_results  # Store for super group aggregation
```

**WORKING Processor:** `src/processors/working_processor.py:write_output()`
- ❌ **NO Super Group Word Analysis code**
- ❌ **NO `pass1_results` available**

**Data Source:** WORKING uses `process_working_comparison()` which only returns:
```python
# src/core/working_comparison.py:407
return pd.DataFrame(results), counter, marked_prev_indices
# ❌ Does NOT return pass1_results or group_analysis
```

**Conclusion:** ❌ **MISSING IN WORKING PROCESSOR**

---

## 🎯 REQUIRED CHANGES - PLAN OF ACTION

### Phase 1: Modify `process_working_comparison()` to return `pass1_results`

**File:** `src/core/working_comparison.py`

**Current Return Statement (line 407):**
```python
return pd.DataFrame(results), counter, marked_prev_indices
```

**New Return Statement:**
```python
return pd.DataFrame(results), counter, marked_prev_indices, pass1_results
```

**Required:**
1. Ensure `pass1_results` is collected during the comparison loop (likely already exists, just not returned)
2. Update return statement to include `pass1_results`

---

### Phase 2: Update `WorkingProcessor.process_data()` to capture `pass1_results`

**File:** `src/processors/working_processor.py`

**Current Code (line 130-135):**
```python
self.df_result, self.counter, marked_prev_indices = process_working_comparison(
    self.df_curr, self.df_prev,
    self.prev_lookup_se, self.prev_lookup_so, self.prev_lookup_sc,
    self.prev_lookup_eo, self.prev_lookup_ec, self.prev_lookup_oc,
    self.prev_lookup_seo, self.prev_lookup_sec, self.prev_lookup_soc, self.prev_lookup_eoc
)
```

**New Code:**
```python
self.df_result, self.counter, marked_prev_indices, self.pass1_results = process_working_comparison(
    self.df_curr, self.df_prev,
    self.prev_lookup_se, self.prev_lookup_so, self.prev_lookup_sc,
    self.prev_lookup_eo, self.prev_lookup_ec, self.prev_lookup_oc,
    self.prev_lookup_seo, self.prev_lookup_sec, self.prev_lookup_soc, self.prev_lookup_eoc
)
```

---

### Phase 3: Add Super Group Word Analysis to `WorkingProcessor.write_output()`

**File:** `src/processors/working_processor.py`

**Current Code (line 290):**
```python
self.df_summary.to_excel(writer, sheet_name="Summary Report", index=False, header=True)
```

**Add After Summary Report (before Phase 2.3 comment):**
```python
self.df_summary.to_excel(writer, sheet_name="Summary Report", index=False, header=True)

# Super Group Word Analysis (parity with RAW processor)
if hasattr(self, 'pass1_results'):
    log("Generating Super Group Word Analysis...")
    super_group_analysis, migration_details = aggregate_to_super_groups(
        self.df_curr,
        self.df_prev,
        self.pass1_results
    )
    write_super_group_word_analysis(writer, super_group_analysis, migration_details)
    log(f"  → {len(super_group_analysis)} super groups analyzed")
    if migration_details:
        log(f"  → {len(migration_details)} migrations detected")

# Phase 2.3: Create StrOrigin Change Analysis sheet
log("Creating StrOrigin Change Analysis sheet...")
```

**Required Imports (add to top of file if missing):**
```python
from src.io.excel_writer import write_super_group_word_analysis
from src.utils.super_groups import aggregate_to_super_groups
```

---

## 📝 IMPLEMENTATION CHECKLIST

### ✅ Preparation (CURRENT STEP)
- [x] Analyze RAW vs WORKING processor differences
- [x] Document findings in PROCESSOR_PARITY_ANALYSIS.md
- [x] Create detailed plan of action
- [ ] Update roadmap.md with new phase
- [ ] Commit preparation documents

### 🔲 Phase 1: Update working_comparison.py
- [ ] Read `src/core/working_comparison.py` completely
- [ ] Verify `pass1_results` is being collected in the comparison loop
- [ ] Update return statement to include `pass1_results`
- [ ] Test compilation (no runtime test yet)
- [ ] Commit: "Phase 1: Update process_working_comparison to return pass1_results"

### 🔲 Phase 2: Update WorkingProcessor.process_data()
- [ ] Update `working_processor.py` line 130-135
- [ ] Capture `self.pass1_results` from return value
- [ ] Test compilation
- [ ] Commit: "Phase 2: Capture pass1_results in WorkingProcessor"

### 🔲 Phase 3: Add Super Group Word Analysis
- [ ] Add imports to `working_processor.py`
- [ ] Add Super Group Word Analysis code to `write_output()`
- [ ] Verify placement (after Summary Report, before StrOrigin Analysis)
- [ ] Test compilation
- [ ] Commit: "Phase 3: Add Super Group Word Analysis to Working processor"

### 🔲 Testing & Validation
- [ ] Run RAW processor test to verify baseline
- [ ] Run WORKING processor test to verify Super Group sheet appears
- [ ] Compare RAW vs WORKING Super Group sheet output
- [ ] Verify identical logic and output format
- [ ] Run comprehensive test suite (`tests/test_all_processors.py`)
- [ ] Commit: "Tests: Verify Super Group parity between RAW and WORKING"

### 🔲 Documentation & Release
- [ ] Update version (if needed)
- [ ] Update README.md with Super Group parity note
- [ ] Update WIKI_CONFLUENCE.md
- [ ] Final commit: "Complete: Working processor Super Group parity achieved"
- [ ] Git push

---

## 🎓 UNDERSTANDING THE SUPER GROUP WORD ANALYSIS

### What is it?
The Super Group Word Analysis sheet aggregates word count changes at the "super group" level rather than individual rows.

### Why is it important?
- Shows word count changes by major content groups (scenes, chapters, etc.)
- Helps translators/editors see which sections grew or shrunk
- Identifies content migrations between super groups
- Provides big-picture view of content changes

### What data does it need?
- `pass1_results`: Detailed row-by-row matching results from PASS 1 of the TWO-PASS algorithm
- `df_curr`: Current file data (with super group info)
- `df_prev`: Previous file data (with super group info)

### What does `aggregate_to_super_groups()` do?
```python
# Located in: src/utils/super_groups.py
def aggregate_to_super_groups(df_curr, df_prev, pass1_results):
    # Groups rows by super group identifier
    # Sums word counts for each super group
    # Compares current vs previous word counts
    # Detects content migrations between super groups
    # Returns: (super_group_analysis, migration_details)
```

### Output Columns (in Excel sheet):
- Super Group ID
- Previous Word Count
- Current Word Count
- Word Count Change (+/-)
- Percentage Change
- Migration Status (if content moved)

---

## 🚀 EXPECTED OUTCOME

### Before (Current State):
- **RAW Processor Output:** 5 sheets
  1. Comparison
  2. Deleted Rows
  3. Summary Report
  4. **Super Group Word Analysis** ✅
  5. StrOrigin Change Analysis ✅

- **WORKING Processor Output:** 4 sheets
  1. Work Transform
  2. 📅 Update History
  3. Deleted Rows
  4. Summary Report
  5. StrOrigin Change Analysis ✅
  6. ❌ **MISSING: Super Group Word Analysis**

### After (Target State):
- **RAW Processor Output:** 5 sheets (unchanged)
- **WORKING Processor Output:** 5 sheets
  1. Work Transform
  2. 📅 Update History
  3. Deleted Rows
  4. Summary Report
  5. **Super Group Word Analysis** ✅ **ADDED**
  6. StrOrigin Change Analysis ✅

**Result:** ✅ **FULL PARITY ACHIEVED**

---

## 📊 IMPACT ASSESSMENT

### Code Changes:
- **Files Modified:** 2
  1. `src/core/working_comparison.py` - 1 line change (return statement)
  2. `src/processors/working_processor.py` - ~15 lines added (imports + analysis code)

### Risk Level: **LOW**
- No algorithmic changes, just exposing existing data
- Super Group logic already tested and working in RAW processor
- Simply copying proven implementation to WORKING processor

### Testing Required:
- Unit tests (existing test suite should cover)
- Integration test (run WORKING processor end-to-end)
- Output comparison (RAW vs WORKING Super Group sheets)

### Version Bump:
- Recommend: **v11201322** (minor feature parity update)
- Not a new feature, but fills functional gap
- No breaking changes

---

## 📝 NOTES FOR FUTURE DEVELOPMENT

### Why was this gap created?
- RAW processor implemented first with full feature set
- WORKING processor focused on conditional import logic
- Super Group analysis was added to RAW but not backported to WORKING
- StrOrigin analysis was added to both (but Super Group was overlooked)

### How to prevent gaps in future?
1. ✅ Create parity checklist in CLAUDE.md
2. ✅ Document processor features in comparison table
3. ✅ Run parity check before each release
4. ✅ Test both processors with same input files

### Future Enhancements (Post-Parity):
- Consider refactoring shared sheet creation into base processor
- Create `BaseProcessor.write_super_group_analysis()` method
- Both RAW and WORKING can call shared implementation
- Reduces code duplication

---

**Analysis Complete!**
**Next Step:** Update roadmap.md with Phase 3.1.3 - Processor Parity Update
