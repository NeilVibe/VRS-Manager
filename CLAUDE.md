# Claude Code Reference - VRS Manager

## BUILD ("build it", "trigger build")
```bash
# Check current version
git tag -l "v1118.*" | sort -V | tail -1

# Increment and push (e.g. v1118.5 → v1118.6)
git tag v1118.X && git push origin v1118.X
```

## TESTING
```bash
python3 test_5000_perf.py      # Performance
python3 test_accuracy.py       # Accuracy
python3 test_math_verify.py    # Math verification
```

## CRITICAL PATTERN (DataFrame access)
```python
# ALWAYS use this:
value = safe_str(row.get(COL_NAME, ""))

# NEVER use this:
value = row[COL_NAME]  # ✗ Can cause dict errors
```

## CORE FILES
- `src/core/comparison.py` - Raw VRS Check
- `src/core/working_comparison.py` - Working VRS Check
- `src/core/lookups.py` - 10-key lookups (Raw)
- `src/core/working_helpers.py` - 10-key lookups (Working)

## COMMIT FORMAT
```
Brief summary

CHANGES:
- What changed
- Why it changed

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```
