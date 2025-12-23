# VRS Manager Quick Test Guide

**Purpose:** Test V2.1 UI fixes on Windows

---

## Step 1: Install to Playground (Windows)

Run in **Windows PowerShell** (not WSL):

```powershell
# Navigate to project folder
cd C:\NEIL_PROJECTS_WINDOWSBUILD\VRSManagerProject

# Run installer (GUI will appear)
.\VRSManager_v12231045_Light_Setup.exe

# When prompted for location, choose:
# C:\NEIL_PROJECTS_WINDOWSBUILD\VRSManagerProject\Playground\VRSManager
```

Or double-click the installer in Windows Explorer.

---

## Step 2: Launch VRS Manager

```powershell
cd C:\NEIL_PROJECTS_WINDOWSBUILD\VRSManagerProject\Playground\VRSManager
.\VRSManager.exe
```

---

## Step 3: Take Screenshots

Use the PowerShell script:

```powershell
cd C:\NEIL_PROJECTS_WINDOWSBUILD\VRSManagerProject

# Screenshot main window
.\take_screenshot.ps1 -WindowTitle "VRS Manager" -OutputPath "screenshots\01_main.png"

# Open Settings, then:
.\take_screenshot.ps1 -WindowTitle "Settings" -OutputPath "screenshots\02_settings.png"

# Open Column Settings, then:
.\take_screenshot.ps1 -WindowTitle "Column Settings" -OutputPath "screenshots\03_column_settings.png"
```

---

## Step 4: Verify V2.1 Fixes

Check screenshots for:

| Issue | What to Verify |
|-------|----------------|
| Text cut-off | "Apply & Save" button fully visible |
| Help text | All help text complete (not "...") |
| Window size | 880x800 default, resizable |
| Scrolling | Can scroll in auto-generated section |

---

## Alternative: Run from WSL (After Manual Install)

Once installed, you can launch from WSL:

```bash
# Launch VRS Manager on Windows
/mnt/c/NEIL_PROJECTS_WINDOWSBUILD/VRSManagerProject/Playground/VRSManager/VRSManager.exe &

# Wait, then take screenshot
sleep 5
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -File "C:\NEIL_PROJECTS_WINDOWSBUILD\VRSManagerProject\take_screenshot.ps1" -WindowTitle "VRS Manager" -OutputPath "C:\NEIL_PROJECTS_WINDOWSBUILD\VRSManagerProject\screenshots\test.png"
```

---

## Automated Test (After Manual Install)

```bash
cd /home/neil1988/vrsmanager
./testing_toolkit/scripts/playground_install.sh --test
```

This runs `launch_and_test.py` which:
1. Launches VRS Manager
2. Takes screenshots at each step
3. Reports results

---

*Note: NSIS silent install (`/S /D=path`) doesn't work reliably from WSL. Install manually first.*
