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

## Notes

- **No auth required** for public repos
- **Rate limited** to 60 requests/hour without auth
- **JSON output** - easy to parse with Python
- **Real-time** - shows current status immediately

## When to Use

✅ User reports build failure without details
✅ Need to check if builds are running
✅ Want to see failure history/patterns
✅ Debugging workflow issues
✅ Confirming fixes worked

❌ Don't use for downloading logs (too large)
❌ Don't use for detailed step output (use web UI)
