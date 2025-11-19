# Claude Code Reference - VRS Manager

This file contains commands and procedures for Claude to execute when requested by the user.

---

## BUILD TRIGGERS

### When user says: "build it", "trigger build", "compile", etc.

**Execute this command:**
```bash
# Increment version tag (check current tags first)
git tag v1118.X  # Replace X with next version number
git push origin v1118.X
```

**Current version format:** `v1118.X` where X increments (5, 6, 7, etc.)

**Check existing tags:**
```bash
git tag -l "v1118.*" | sort -V | tail -1
```

**Build will auto-trigger on GitHub Actions:**
- Workflow: "Build Executables"
- Platform: Windows only
- Output: VRSManager.exe in Artifacts
- Check status: https://github.com/NeilVibe/VRS-Manager/actions

---

## VERSION MANAGEMENT

### Current Version
- **v1118.5** - Latest stable (dict error fixes, comprehensive testing)

### Version History
- v1118.4 - Super Group enhancements
- v1118.3 - TimeFrame preservation
- v1118.2 - Excel guides update
- v1118.1 - Phase 1.0.1 completion

### Incrementing Version
When ready for new release:
1. Check current: `git tag -l | grep v1118 | sort -V | tail -1`
2. Increment: Add 1 to last number (e.g., v1118.5 → v1118.6)
3. Push tag: `git tag v1118.6 && git push origin v1118.6`

---

## TESTING COMMANDS

### Run comprehensive tests
```bash
python3 test_5000_perf.py        # Performance test (5000 rows)
python3 test_accuracy.py         # Accuracy verification
python3 test_math_verify.py      # Mathematical verification
python3 test_working_real.py     # Real file structure test
```

### Run specific processor tests
```bash
# Test Raw VRS Check
python3 -c "from src.processors.raw_processor import RawProcessor; p = RawProcessor(); p.run()"

# Test Working VRS Check
python3 -c "from src.processors.working_processor import WorkingProcessor; p = WorkingProcessor(); p.run()"
```

---

## CRITICAL BUG FIXES APPLIED

### Dict Error Fixes (v1118.5)
- **src/core/working_helpers.py**: Changed lookups to store `idx` instead of `row_dict`
- **src/core/lookups.py**: Added `safe_str()` to all column access
- **src/core/comparison.py**: Added `safe_str()` to all prev_row access
- **src/core/working_comparison.py**: Added `safe_str()` to all prev_row access

### Safe String Pattern
Always use this pattern for DataFrame column access:
```python
value = safe_str(row.get(COL_NAME, ""))
```

NOT this:
```python
value = row[COL_NAME]  # ✗ Can cause dict errors
```

---

## COMMIT STANDARDS

### Commit Message Format
```
Brief summary line (imperative mood)

DETAILED CHANGES:
- Bullet point changes
- What was modified and why

TESTING:
- Test results
- Performance metrics if applicable

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Standard Git Commands
```bash
# Commit and push
git add -A
git commit -m "message here"
git push origin main

# Create release tag
git tag v1118.X
git push origin v1118.X
```

---

## FILE LOCATIONS

### Core Processing Files
- `src/core/comparison.py` - Raw VRS Check comparison logic
- `src/core/working_comparison.py` - Working VRS Check comparison logic
- `src/core/lookups.py` - 10-key lookup building (Raw)
- `src/core/working_helpers.py` - 10-key lookup building (Working)
- `src/core/alllang_helpers.py` - All Language Check logic

### Test Files
- `tests/test_5000_PREVIOUS.xlsx` - 4,200 row comprehensive test (PREVIOUS)
- `tests/test_5000_CURRENT.xlsx` - 4,200 row comprehensive test (CURRENT)
- `tests/REAL PREVIOUS FILE TEST STRUCTURE.xlsx` - Real user data structure
- `tests/REAL CURRENT FILE TEST STRUCTURE.xlsx` - Real user data structure

### Configuration
- `VRSManager.spec` - PyInstaller build configuration
- `.github/workflows/build-executables.yml` - GitHub Actions workflow
- `requirements.txt` - Python dependencies

---

## PERFORMANCE BENCHMARKS

### Expected Performance (5000-row test)
- **Raw VRS Check**: ~879 rows/sec (~4.8s total)
- **Working VRS Check**: ~856 rows/sec (~4.9s total)

### Accuracy Requirements
- Change detection: 100%
- New row detection: 100%
- Deleted row detection: 100%
- No rows lost in processing
- No duplicate counting

---

## USER REQUEST PATTERNS

### "build it" → Push version tag
```bash
git tag v1118.X && git push origin v1118.X
```

### "test everything" → Run all tests
```bash
python3 test_5000_perf.py && python3 test_accuracy.py && python3 test_math_verify.py
```

### "commit and push" → Standard workflow
```bash
git add -A && git commit -m "message" && git push origin main
```

---

**Last Updated:** 2025-11-19 (v1118.5)
