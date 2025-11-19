# VRS Manager - Developer Guide

## Quick Reference for Phase 2 Modules

### How to Import

```python
# Core processing functions
from src.core import (
    generate_casting_key,      # Generate CastingKey from character info
    build_lookups,              # Build lookups for raw VRS (fast)
    build_working_lookups,      # Build lookups for working process
    compare_rows,               # Main comparison engine
    classify_change,            # Classify changes (raw VRS)
    classify_working_change,    # Classify changes (working)
    classify_alllang_change,    # Classify changes (alllang)
    find_deleted_rows,          # Find deleted (3-key system)
    find_working_deleted_rows   # Find deleted (4-key system)
)

# I/O functions
from src.io import (
    safe_read_excel,            # Read Excel safely with openpyxl
    normalize_dataframe_status, # Normalize STATUS column
    filter_output_columns,      # Filter to output columns
    apply_direct_coloring,      # Apply colors to worksheet
    widen_summary_columns,      # Set summary column widths
    format_update_history_sheet # Format history sheet
)

# History management
from src.history import (
    load_update_history,        # Load history JSON
    save_update_history,        # Save history JSON
    add_working_update_record,  # Add working process record
    add_alllang_update_record,  # Add alllang record
    add_master_file_update_record # Add master record
)

# Utilities
from src.utils.helpers import (
    log,                        # Timestamped logging
    safe_str,                   # Safe string conversion
    contains_korean,            # Check for Korean text
    is_after_recording_status,  # Check status type
    generate_previous_data      # Generate PreviousData field
)

from src.utils.progress import (
    print_progress,             # Print progress bar
    finalize_progress           # Clear progress bar
)

# Configuration
from src.config import (
    COL_SEQUENCE, COL_EVENTNAME, COL_STRORIGIN,  # Column names
    OUTPUT_COLUMNS,             # Output column list
    AFTER_RECORDING_STATUSES    # Post-recording statuses
)
```

### Common Usage Patterns

#### Pattern 1: Reading and Normalizing Excel Files

```python
from src.io import safe_read_excel, normalize_dataframe_status

# Read Excel file safely
df = safe_read_excel("path/to/file.xlsx")

# Normalize STATUS column
df = normalize_dataframe_status(df)
```

#### Pattern 2: Building Lookups for Comparison

```python
from src.core import build_lookups, build_working_lookups

# For RAW VRS Check (fast, tuple-based)
lookup_cw, lookup_cg, lookup_es, lookup_cs = build_lookups(df_previous)

# For Working Process (dict-based, more flexible)
prev_cw, prev_cg, prev_es, prev_cs = build_working_lookups(df_prev, "PREVIOUS")
curr_cw, curr_cg, curr_es, curr_cs = build_working_lookups(df_curr, "CURRENT")
```

#### Pattern 3: Comparing Rows

```python
from src.core import compare_rows, find_deleted_rows

# Compare current against previous
changes, prev_strorigins, changed_cols_map, counter = compare_rows(
    df_current, 
    prev_lookup_cw, 
    prev_lookup_cg, 
    prev_lookup_es,
    prev_lookup_cs
)

# Add results to dataframe
df_current["CHANGES"] = changes
df_current["Previous StrOrigin"] = prev_strorigins

# Find deleted rows
df_deleted = find_deleted_rows(df_previous, df_current)
```

#### Pattern 4: Generating Casting Keys

```python
from src.core import generate_casting_key

# Generate for each row
df["CastingKey"] = df.apply(
    lambda row: generate_casting_key(
        row["CharacterKey"],
        row["DialogVoice"],
        row["Speaker|CharacterGroupKey"],
        row.get("DialogType", "")
    ),
    axis=1
)
```

#### Pattern 5: Writing and Formatting Excel Output

```python
from src.io import filter_output_columns, apply_direct_coloring
from openpyxl import load_workbook
import pandas as pd

# Filter to output columns
df_output = filter_output_columns(df, OUTPUT_COLUMNS)

# Write to Excel
output_path = "output.xlsx"
df_output.to_excel(output_path, index=False, sheet_name="Result")

# Apply formatting
wb = load_workbook(output_path)
ws = wb["Result"]
apply_direct_coloring(ws, is_master=False, changed_columns_map=changed_cols_map)
wb.save(output_path)
```

#### Pattern 6: Tracking Update History

```python
from src.history import add_working_update_record, load_update_history

# Add a new record
record = add_working_update_record(
    output_filename="output.xlsx",
    prev_path="/path/to/previous.xlsx",
    curr_path="/path/to/current.xlsx",
    counter={"New Row": 10, "StrOrigin Change": 5},
    total_rows=1000
)

# Load history to display
history = load_update_history("working")
for update in history["updates"]:
    print(f"{update['timestamp']}: {update['output_file']}")
```

### The 4-Tier Key System

The VRS Manager uses a sophisticated 4-tier key system for matching rows:

```python
# Key 1: (SequenceName, EventName) - Primary match
key_cw = (row["SequenceName"], row["EventName"])

# Key 2: (SequenceName, StrOrigin) - Alternative match
key_cg = (row["SequenceName"], row["StrOrigin"])

# Key 3: (EventName, StrOrigin) - Sequence changed
key_es = (row["EventName"], row["StrOrigin"])

# Key 4: (CastingKey, SequenceName) - Character verification
key_cs = (row["CastingKey"], row["SequenceName"])
```

**Matching Logic:**
1. Try Key 1 first (direct match)
2. If not found, try Key 2 with Key 4 verification
   - If Key 4 matches: Same character, EventName changed
   - If Key 4 doesn't match: Different character, new row
3. If not found, try Key 3 (SequenceName changed)
4. If not found: New row

### Module Responsibilities

| Module | Responsibility | Key Functions |
|--------|----------------|---------------|
| `src.config` | Constants and configuration | Column names, status sets, output columns |
| `src.utils.helpers` | Utility functions | safe_str, log, contains_korean, generate_previous_data |
| `src.utils.progress` | Progress display | print_progress, finalize_progress |
| `src.core.casting` | Casting key generation | generate_casting_key |
| `src.core.lookups` | Lookup building | build_lookups, build_working_lookups |
| `src.core.comparison` | Row comparison | compare_rows, classify_*, find_deleted_rows |
| `src.io.excel_reader` | Excel input | safe_read_excel, normalize_dataframe_status |
| `src.io.excel_writer` | Excel output | filter_output_columns |
| `src.io.formatters` | Excel formatting | apply_direct_coloring, widen_summary_columns |
| `src.history.history_manager` | History tracking | load/save/add update records |

### Best Practices

1. **Always use safe_str()** when working with values that might be None or NaN
2. **Use log()** for timestamped messages instead of print()
3. **Use print_progress()** for long-running loops
4. **Always call finalize_progress()** after a progress loop
5. **Build lookups once** at the start of processing, not in loops
6. **Filter output columns** before writing to Excel
7. **Apply formatting** after writing data to workbook
8. **Track history** for all processes that modify data

### Error Handling

```python
from src.io import safe_read_excel
from src.utils.helpers import log

try:
    df = safe_read_excel(file_path)
except ValueError as e:
    log(f"Error reading Excel file: {e}")
    return
except FileNotFoundError:
    log(f"File not found: {file_path}")
    return
```

### Testing Modules

All modules are syntax-validated. To test imports:

```bash
python3 -m py_compile src/core/casting.py
python3 -m py_compile src/core/lookups.py
python3 -m py_compile src/core/comparison.py
# etc...
```

To test in Python (requires dependencies installed):

```python
# Test imports
from src.core import generate_casting_key
from src.io import safe_read_excel
from src.history import load_update_history

# Test basic functionality
key = generate_casting_key("char1", "voice1", "speaker1", "dialog")
print(f"Generated key: {key}")
```

## Next Steps

Phase 3 will create processor modules that orchestrate these building blocks:
- `src.processors.raw_vrs_processor` - RAW VRS Check
- `src.processors.working_processor` - Working Process
- `src.processors.alllang_processor` - All Language Process
- `src.processors.master_processor` - Master File Update
