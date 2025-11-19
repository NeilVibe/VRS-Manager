# Claude Code Reference - VRS Manager

## BUILD ("build it", "trigger build")
```bash
# Update BUILD_TRIGGER.txt with new version and push to main
echo "Last build: v1118.X" >> BUILD_TRIGGER.txt
git add BUILD_TRIGGER.txt
git commit -m "Trigger build v1118.X"
git push origin main
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
