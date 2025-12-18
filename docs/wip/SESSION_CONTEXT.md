# Session Context - Claude Handoff Document

**Last Updated:** 2025-12-18
**Version:** v12181615
**Session:** StringOrigin & Mainline Logic + CI Pipeline Update

---

## Current State

| Item | Status |
|------|--------|
| Version | v12181615 |
| Completed Tasks | **2** (TASK-001 + CI update) |
| Tests | Pending run |
| Status | Ready for testing |

---

## What Was Accomplished (2025-12-18)

### TASK-001: StringOrigin & Mainline Logic - COMPLETED

**Change 1:** StrOrigin column now uses NEW value
- When strorigin changes + has status → strorigin = NEW (from current/mainline)
- Previously: strorigin = previous (kept old value)

**Change 2:** Mainline text conditional loading
- When no status + text == "NO TRANSLATION" → use mainline text
- When no status + text has value → keep previous text
- Previously: always used mainline when no status

**Files:** `src/core/import_logic.py:42-56` and `:116-129`

### CI Pipeline Executive Power - COMPLETED

Updated CI to auto-generate version like LocalizationTools:
- Version format: MMDDHHMM (KST)
- Pipeline injects version into all files at build time
- No more manual version in BUILD_TRIGGER.txt

**Files:**
- `.github/workflows/build-installers.yml` - Auto-generate + inject version
- `scripts/check_version_unified.py` - Added `--skip-timestamp` flag

---

## Version Changes Summary (v12181615)

| Change | Description |
|--------|-------------|
| StrOrigin column | Uses NEW value (not previous) when status exists |
| Mainline loading | Only when no status AND text == "NO TRANSLATION" |
| CI versioning | Auto-generated MMDDHHMM format |

---

## Files Modified This Session

| File | Changes |
|------|---------|
| `src/core/import_logic.py` | StrOrigin + mainline logic |
| `src/config.py` | VERSION = "12181615" |
| `.github/workflows/build-installers.yml` | Auto-generate version |
| `scripts/check_version_unified.py` | --skip-timestamp flag |
| `CLAUDE.md` | Navigation hub updates |
| `roadmap.md` | Version + task reference |
| `docs/wip/*` | WIP documentation structure |

---

## Next Steps

1. Run full tests (518 tests)
2. Verify tests pass
3. Commit and push
4. Trigger build with `Build LIGHT` in BUILD_TRIGGER.txt

---

## Quick Commands

```bash
# Run tests
python3 tests/test_unified_change_detection.py

# Check version
python3 scripts/check_version_unified.py
```

---

*This document is the source of truth for session handoff.*
