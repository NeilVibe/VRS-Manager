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
