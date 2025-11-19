# GitHub Actions Debugging via API

## Critical Commands for Checking Build History

### 1. List Recent Workflow Runs
```bash
curl -s "https://api.github.com/repos/NeilVibe/VRS-Manager/actions/runs?per_page=10" | \
python3 -c "import sys, json; runs = json.load(sys.stdin)['workflow_runs']; \
[print(f\"{r['name']}: {r['status']} - {r['conclusion']} - {r['created_at']}\") for r in runs[:10]]"
```

**Output:**
```
Build LIGHT and FULL Installers: completed - failure - 2025-11-19T13:20:35Z
Build Executables: completed - cancelled - 2025-11-19T13:20:35Z
```

**Shows:**
- Workflow name
- Status (completed, in_progress, queued)
- Conclusion (success, failure, cancelled)
- Start time

### 2. Get Latest Failed Run Details
```bash
curl -s "https://api.github.com/repos/NeilVibe/VRS-Manager/actions/runs?per_page=1" | \
python3 -c "import sys, json; run = json.load(sys.stdin)['workflow_runs'][0]; \
print(f\"Run ID: {run['id']}\"); print(f\"URL: {run['html_url']}\")"
```

**Output:**
```
Run ID: 19502750683
URL: https://github.com/NeilVibe/VRS-Manager/actions/runs/19502750683
```

### 3. Find Which Steps Failed
```bash
curl -s "https://api.github.com/repos/NeilVibe/VRS-Manager/actions/runs/19502750683/jobs" | \
python3 -c "
import sys, json
jobs = json.load(sys.stdin)['jobs']
for job in jobs:
    if job['conclusion'] == 'failure':
        print(f\"\n=== {job['name']} ===\")
        for step in job['steps']:
            if step['conclusion'] == 'failure':
                print(f\"FAILED STEP: {step['name']}\")
                print(f\"Status: {step['conclusion']}\")
"
```

**Output:**
```
=== Build FULL Installer ===
FAILED STEP: Download BERT model
Status: failure

=== Build LIGHT Installer ===
FAILED STEP: Verify LIGHT build
Status: failure
```

## Generic Template (Replace Repo Name)

```bash
# Replace OWNER/REPO with actual values
REPO="NeilVibe/VRS-Manager"

# 1. List recent runs
curl -s "https://api.github.com/repos/$REPO/actions/runs?per_page=10" | \
python3 -c "import sys, json; runs = json.load(sys.stdin)['workflow_runs']; \
[print(f\"{r['name']}: {r['status']} - {r['conclusion']} - {r['created_at']}\") for r in runs[:10]]"

# 2. Get latest run ID
RUN_ID=$(curl -s "https://api.github.com/repos/$REPO/actions/runs?per_page=1" | \
python3 -c "import sys, json; print(json.load(sys.stdin)['workflow_runs'][0]['id'])")

# 3. Check failed steps
curl -s "https://api.github.com/repos/$REPO/actions/runs/$RUN_ID/jobs" | \
python3 -c "
import sys, json
jobs = json.load(sys.stdin)['jobs']
for job in jobs:
    if job['conclusion'] == 'failure':
        print(f\"\n=== {job['name']} ===\")
        for step in job['steps']:
            if step['conclusion'] == 'failure':
                print(f\"FAILED STEP: {step['name']}\")
"
```

## Why This Is Critical

**Problem:**
- User says "build failed" but doesn't paste error
- Can't access GitHub Actions UI directly
- Need to diagnose without seeing the actual logs

**Solution:**
- Use GitHub API to query workflow runs
- Find which job failed
- Find which step failed
- Identify root cause

**Example from Phase 3.0:**
```
User: "Build failed"
Me: *checks API*
Output: "FAILED STEP: Download BERT model"
Fix: Removed download step (model now in LFS)
```

## Additional Useful Queries

### Get All Jobs for a Run
```bash
curl -s "https://api.github.com/repos/$REPO/actions/runs/$RUN_ID/jobs" | \
python3 -c "import sys, json; jobs = json.load(sys.stdin)['jobs']; \
[print(f\"{j['name']}: {j['conclusion']}\") for j in jobs]"
```

### Check if Workflows Are Running
```bash
curl -s "https://api.github.com/repos/$REPO/actions/runs?status=in_progress" | \
python3 -c "import sys, json; runs = json.load(sys.stdin)['workflow_runs']; \
print(f\"Running: {len(runs)} workflows\")"
```

### List All Workflow Files
```bash
curl -s "https://api.github.com/repos/$REPO/actions/workflows" | \
python3 -c "import sys, json; workflows = json.load(sys.stdin)['workflows']; \
[print(f\"{w['name']}: {w['path']}\") for w in workflows]"
```

## 🔥 BEST METHOD: Get Full Error Logs with `gh` CLI

**This is the MOST EFFECTIVE way to debug builds!** The API methods above show which step failed, but the `gh` CLI gets the ACTUAL error messages.

### Setup (One-Time)

If `gh auth status` shows authentication failed, ask user for a GitHub token:

1. User goes to https://github.com/settings/tokens
2. Generate new token (classic) with `repo` + `workflow` permissions
3. Run:
```bash
echo "TOKEN_HERE" | gh auth login --with-token
```

### Get Full Logs for Failed Steps

```bash
# Get the failed run ID first
RUN_ID=$(curl -s "https://api.github.com/repos/OWNER/REPO/actions/runs?per_page=1" | \
python3 -c "import sys, json; print(json.load(sys.stdin)['workflow_runs'][0]['id'])")

# Get FULL error logs (shows actual error messages!)
gh run view $RUN_ID --log-failed
```

**Or directly with run ID:**
```bash
gh run view 19503424622 --log-failed
```

### Filter Logs for Specific Step

```bash
# Get logs for specific failed step
gh run view 19503424622 --log-failed | grep -A 30 "Compile LIGHT installer"
```

### Real Example from Phase 3.0 Build #2

**Command:**
```bash
gh run view 19503424622 --log-failed | grep -B 5 -A 30 "Compile LIGHT installer"
```

**Output:**
```
Build LIGHT Installer  Compile LIGHT installer
Error on line 127 in D:\a\VRS-Manager\VRS-Manager\installer\vrsmanager_light.iss: Column 4:
Invalid number of parameters.
Compile aborted.
##[error]Process completed with exit code 1.
```

**This shows the EXACT error!** Not just "step failed" but the actual line number and error message.

### Why This Changed Everything

**Before (API only):**
- ❌ Could only see: "Compile LIGHT installer: failure"
- ❌ Had to guess what went wrong
- ❌ No visibility into actual error messages

**After (gh CLI):**
- ✅ Saw exact error: "Line 127: Invalid number of parameters"
- ✅ Saw exact error: "Missing required file: pytorch_model.bin"
- ✅ Fixed both issues immediately without guessing

### Complete Debugging Workflow

```bash
# 1. Check latest run status
gh run list --limit 1

# 2. Get run ID if failed
RUN_ID=$(gh run list --limit 1 --json databaseId --jq '.[0].databaseId')

# 3. View failed logs
gh run view $RUN_ID --log-failed

# 4. Search for specific error
gh run view $RUN_ID --log-failed | grep -i "error"

# 5. Get context around error
gh run view $RUN_ID --log-failed | grep -B 10 -A 10 "KEYWORD"
```

## Notes

- **API (no auth):** Shows which steps failed, good for quick checks
- **gh CLI (with auth):** Shows FULL error logs, ESSENTIAL for actual debugging
- **Rate limited** to 60 requests/hour without auth (API)
- **Authenticated gh CLI:** Much higher rate limits
- **JSON output** - easy to parse with Python
- **Real-time** - shows current status immediately

## When to Use Each Method

### Use API (No Auth) When:
✅ Quick check: "Is build running or failed?"
✅ Identifying which step failed
✅ Checking build history/patterns
✅ User just needs status update

### Use gh CLI (With Auth) When:
✅ **User reports build failure** - Get exact error message!
✅ **Need actual error text** - Not just step name
✅ **Debugging complex failures** - See full stack traces
✅ **Line numbers/file paths needed** - Pinpoint exact location

### Don't Use For:
❌ Downloading massive log files (use web UI)
❌ When user has already pasted error message
