# VRS Manager Autonomous Testing Protocol

**Created:** 2025-12-23 | **Status:** Active | **Framework:** pyautogui + PIL

---

## Overview

This document defines the autonomous testing protocol for VRS Manager, a Python/tkinter desktop application. Since tkinter is NOT Electron-based, we use **pyautogui** for GUI automation instead of CDP (Chrome DevTools Protocol).

---

## CRITICAL LIMITATION (2025-12-23)

**Input simulation from WSL does NOT work** for tkinter applications due to Windows UIPI (User Interface Privilege Isolation).

### What Works from WSL:
- ✅ Launching VRS Manager
- ✅ Taking screenshots (PrintWindow API)
- ✅ Reading/writing files
- ✅ Process management

### What Does NOT Work from WSL:
- ❌ mouse_event clicks
- ❌ SendInput API
- ❌ pyautogui clicks
- ❌ PostMessage WM_LBUTTONDOWN
- ❌ UI Automation (tkinter buttons have no accessible names)

### Viable Options for Full Autonomy:

| Option | How | Autonomy Level |
|--------|-----|----------------|
| **GitHub Actions** | `windows-latest` runner | Full (CI/CD) |
| **Windows Task Scheduler** | Scheduled .ps1 script | Full (local) |
| **Manual + Screenshot** | User clicks, Claude verifies | Semi-autonomous |

---

## Architecture

### Why Not CDP?

| Framework | CDP Support | Reason |
|-----------|-------------|--------|
| Electron | ✅ Yes | Uses Chromium internally |
| tkinter | ❌ No | Native Python GUI, no browser |
| PyQt/PySide | ❌ No | Native Qt widgets |
| wxPython | ❌ No | Native widgets |

### Tkinter Testing Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    VRS Manager (tkinter)                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐       │
│   │  pyautogui  │   │   Pillow    │   │  pywinauto  │       │
│   │  (clicks,   │   │(screenshots)│   │  (Windows   │       │
│   │   typing)   │   │             │   │   UI API)   │       │
│   └─────────────┘   └─────────────┘   └─────────────┘       │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                     Windows Display                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Python Dependencies

```bash
pip install pyautogui pillow pywinauto
```

### Folder Structure

```
testing_toolkit/
├── VRS_MANAGER_TEST_PROTOCOL.md    # This document
├── requirements.txt                 # Test dependencies
├── scripts/
│   ├── playground_install.ps1      # Install VRS Manager to Playground
│   ├── launch_and_test.py          # Main test runner
│   ├── test_main_window.py         # Main window tests
│   ├── test_column_settings.py     # Column settings dialog tests
│   └── test_file_upload.py         # File upload tests
├── screenshots/                     # Test output screenshots
│   └── .gitkeep
└── test_data/
    └── sample_vrs.xlsx             # Test Excel file
```

---

## Playground Setup

### Windows Path
```
C:\NEIL_PROJECTS_WINDOWSBUILD\VRSManagerProject\Playground\VRSManager
```

### WSL Path
```
/mnt/c/NEIL_PROJECTS_WINDOWSBUILD/VRSManagerProject/Playground/VRSManager
```

### Installation Protocol

1. **Download Installer**
   - Get latest from GitHub Releases
   - Or build locally with `pyinstaller`

2. **Install to Playground**
   ```powershell
   .\playground_install.ps1 -InstallerPath "path\to\VRSManager_Setup.exe"
   ```

3. **Verify Installation**
   ```powershell
   Test-Path "C:\NEIL_PROJECTS_WINDOWSBUILD\VRSManagerProject\Playground\VRSManager\VRSManager.exe"
   ```

---

## Test Execution Protocol

### Phase 1: Launch Application

```python
import subprocess
import time
import pyautogui

# Launch VRS Manager
app_path = r"C:\NEIL_PROJECTS_WINDOWSBUILD\VRSManagerProject\Playground\VRSManager\VRSManager.exe"
process = subprocess.Popen(app_path)

# Wait for window to appear
time.sleep(3)

# Verify window exists
windows = pyautogui.getWindowsWithTitle("VRS Manager")
assert len(windows) > 0, "VRS Manager window not found"
```

### Phase 2: Screenshot Capture

```python
from PIL import ImageGrab
import os

def capture_window(title, output_path):
    """Capture specific window by title."""
    import pygetwindow as gw

    window = gw.getWindowsWithTitle(title)[0]
    window.activate()
    time.sleep(0.3)

    # Get window bounds
    bbox = (window.left, window.top, window.right, window.bottom)

    # Capture
    img = ImageGrab.grab(bbox=bbox)
    img.save(output_path)
    print(f"Screenshot saved: {output_path}")
    return output_path
```

### Phase 3: UI Interaction

```python
def click_button(button_text, window_title="VRS Manager"):
    """Click button by locating its text."""
    import pyautogui

    # Focus window
    window = pyautogui.getWindowsWithTitle(window_title)[0]
    window.activate()
    time.sleep(0.2)

    # Locate button (using image matching or coordinates)
    # Option 1: Use saved button image
    location = pyautogui.locateOnScreen(f'buttons/{button_text}.png')
    if location:
        pyautogui.click(pyautogui.center(location))
        return True

    # Option 2: Use known coordinates (less reliable)
    return False
```

---

## Test Cases

### TC-001: Main Window Loads

| Step | Action | Expected | Screenshot |
|------|--------|----------|------------|
| 1 | Launch VRSManager.exe | Window appears | `01_main_window.png` |
| 2 | Verify title | "VRS Manager by Neil Schmitt" | - |
| 3 | Verify buttons | All 5 buttons visible | - |

### TC-002: Settings Dialog

| Step | Action | Expected | Screenshot |
|------|--------|----------|------------|
| 1 | Click "Settings" | Settings dialog opens | `02_settings_dialog.png` |
| 2 | Verify options | Priority Mode + Column Settings | - |
| 3 | Click "Column Settings" | Column dialog opens | `03_column_settings.png` |

### TC-003: Column Settings - Text Visibility

| Step | Action | Expected | Screenshot |
|------|--------|----------|------------|
| 1 | Open Column Settings | Dialog visible | - |
| 2 | Check button text | "Apply & Save" fully visible | `04_buttons.png` |
| 3 | Check help text | All help text readable | - |
| 4 | Verify no cut-off | All text complete | VERIFY |

### TC-004: File Upload

| Step | Action | Expected | Screenshot |
|------|--------|----------|------------|
| 1 | Click "Upload" | File dialog opens | - |
| 2 | Select Excel file | File selected | - |
| 3 | Wait for analysis | Progress shown, no freeze | `05_analyzing.png` |
| 4 | Verify columns | All columns listed | `06_columns_list.png` |

### TC-005: Optional Columns Visibility

| Step | Action | Expected | Screenshot |
|------|--------|----------|------------|
| 1 | Upload file with 14+ columns | Analysis complete | - |
| 2 | Scroll optional columns | All columns accessible | `07_all_columns.png` |
| 3 | Count visible columns | All 14 visible (scrollable) | VERIFY |

---

## Verification Protocol

### Visual Verification Checklist

After each test run, verify screenshots for:

- [ ] All button text fully visible (no cut-off)
- [ ] All help/info text readable
- [ ] Dialog properly sized
- [ ] Scrollbars appear when needed
- [ ] No overlapping elements
- [ ] Consistent styling

### Automated Verification (Future)

```python
def verify_text_visible(screenshot_path, expected_text):
    """Use OCR to verify text is visible in screenshot."""
    import pytesseract
    from PIL import Image

    img = Image.open(screenshot_path)
    text = pytesseract.image_to_string(img)

    return expected_text in text
```

---

## Running Tests

### From Windows PowerShell

```powershell
cd C:\NEIL_PROJECTS_WINDOWSBUILD\VRSManagerProject

# Run all tests
python testing_toolkit\scripts\launch_and_test.py

# Run specific test
python testing_toolkit\scripts\test_column_settings.py
```

### From WSL (Launches on Windows)

```bash
cd /home/neil1988/vrsmanager

# Convert path and run via PowerShell
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -ExecutionPolicy Bypass -Command "cd C:\NEIL_PROJECTS_WINDOWSBUILD\VRSManagerProject; python testing_toolkit\scripts\launch_and_test.py"
```

---

## Troubleshooting

### Window Not Found

```python
# List all windows
import pygetwindow as gw
print([w.title for w in gw.getAllWindows() if w.title])
```

### Screenshot Fails

```python
# Use full screen as fallback
from PIL import ImageGrab
img = ImageGrab.grab()
img.save("fallback_screenshot.png")
```

### Click Not Working

```python
# Debug: show mouse position
import pyautogui
print(pyautogui.position())

# Debug: highlight click area
pyautogui.moveTo(x, y)
time.sleep(1)  # Visually verify position
pyautogui.click()
```

---

## Integration with CI/CD

### GitHub Actions (Windows Runner)

```yaml
test-gui:
  runs-on: windows-latest
  steps:
    - name: Install dependencies
      run: pip install pyautogui pillow pygetwindow

    - name: Run GUI tests
      run: python testing_toolkit/scripts/launch_and_test.py

    - name: Upload screenshots
      uses: actions/upload-artifact@v3
      with:
        name: test-screenshots
        path: testing_toolkit/screenshots/
```

---

## Change Log

| Date | Change |
|------|--------|
| 2025-12-23 | Initial protocol created |

---

*This protocol adapts patterns from LocalizationTools CDP testing for tkinter applications.*
