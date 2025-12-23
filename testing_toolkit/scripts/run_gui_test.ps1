# VRS Manager GUI Test Runner (Native Windows)
# This script runs natively on Windows to bypass WSL input restrictions
# Results are saved to JSON for Claude to read

param(
    [string]$AppPath = "C:\NEIL_PROJECTS_WINDOWSBUILD\VRSManagerProject\Playground\VRSManager\VRSManager.exe",
    [string]$OutputDir = "C:\NEIL_PROJECTS_WINDOWSBUILD\VRSManagerProject\testing_toolkit\results"
)

# Ensure output directory exists
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$resultFile = "$OutputDir\test_result_$timestamp.json"
$logFile = "$OutputDir\test_log_$timestamp.txt"

# Initialize results
$results = @{
    timestamp = $timestamp
    status = "running"
    tests = @()
    screenshots = @()
    errors = @()
}

function Log($message) {
    $ts = Get-Date -Format "HH:mm:ss"
    $line = "[$ts] $message"
    Write-Host $line
    Add-Content -Path $logFile -Value $line
}

function Save-Results {
    $results | ConvertTo-Json -Depth 5 | Out-File -FilePath $resultFile -Encoding UTF8
}

function Add-Test($name, $passed, $reason = "") {
    $results.tests += @{
        name = $name
        passed = $passed
        reason = $reason
    }
    if ($passed) {
        Log "PASS: $name"
    } else {
        Log "FAIL: $name - $reason"
        $results.errors += "$name : $reason"
    }
    Save-Results
}

# Add C# code for window capture
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Drawing;
using System.Runtime.InteropServices;

public class WindowCapture {
    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool PrintWindow(IntPtr hwnd, IntPtr hDC, uint nFlags);

    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool SetCursorPos(int X, int Y);

    [DllImport("user32.dll")]
    public static extern void mouse_event(uint dwFlags, int dx, int dy, uint dwData, int dwExtraInfo);

    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left, Top, Right, Bottom; }

    public const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
    public const uint MOUSEEVENTF_LEFTUP = 0x0004;

    public static Bitmap CaptureWindow(IntPtr hwnd) {
        RECT rect;
        GetWindowRect(hwnd, out rect);
        int w = rect.Right - rect.Left;
        int h = rect.Bottom - rect.Top;
        if (w <= 0 || h <= 0) return null;
        Bitmap bmp = new Bitmap(w, h);
        using (Graphics g = Graphics.FromImage(bmp)) {
            IntPtr hdc = g.GetHdc();
            PrintWindow(hwnd, hdc, 2);
            g.ReleaseHdc(hdc);
        }
        return bmp;
    }

    public static void Click(int x, int y) {
        SetCursorPos(x, y);
        System.Threading.Thread.Sleep(100);
        mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0);
        System.Threading.Thread.Sleep(50);
        mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0);
    }
}
"@ -ReferencedAssemblies System.Drawing

function Capture-Window($hwnd, $outputPath) {
    try {
        $bmp = [WindowCapture]::CaptureWindow($hwnd)
        if ($bmp) {
            $bmp.Save($outputPath)
            $bmp.Dispose()
            $results.screenshots += $outputPath
            Log "Screenshot: $outputPath"
            return $true
        }
    } catch {
        Log "Screenshot failed: $_"
    }
    return $false
}

function Click-At($hwnd, $xOffset, $yOffset) {
    $rect = New-Object WindowCapture+RECT
    [WindowCapture]::GetWindowRect($hwnd, [ref]$rect)
    $x = $rect.Left + $xOffset
    $y = $rect.Top + $yOffset
    [WindowCapture]::SetForegroundWindow($hwnd)
    Start-Sleep -Milliseconds 200
    [WindowCapture]::Click($x, $y)
    Start-Sleep -Milliseconds 300
}

# ===== START TESTS =====
Log "=========================================="
Log "VRS MANAGER GUI TEST - Native Windows"
Log "=========================================="
Log "App: $AppPath"
Log "Output: $OutputDir"
Log ""

# TEST 1: Launch Application
Log "TEST 1: Launch Application"
if (-not (Test-Path $AppPath)) {
    Add-Test "Launch" $false "App not found: $AppPath"
    $results.status = "failed"
    Save-Results
    exit 1
}

$process = Start-Process -FilePath $AppPath -PassThru
Start-Sleep -Seconds 3

$mainWindow = Get-Process -Id $process.Id -ErrorAction SilentlyContinue
if ($mainWindow -and $mainWindow.MainWindowHandle -ne 0) {
    Add-Test "Launch" $true
    $mainHwnd = $mainWindow.MainWindowHandle
    Capture-Window $mainHwnd "$OutputDir\01_main_window.png"
} else {
    Add-Test "Launch" $false "Window handle not found"
    $results.status = "failed"
    Save-Results
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    exit 1
}

# TEST 2: Click Settings Button
Log "TEST 2: Open Settings Dialog"
Click-At $mainHwnd 248 680  # Settings button position
Start-Sleep -Milliseconds 800

# Check for new window
$allProcs = Get-Process -Name VRSManager -ErrorAction SilentlyContinue
$foundSettings = $false
foreach ($p in $allProcs) {
    if ($p.MainWindowTitle -like "*Settings*") {
        $foundSettings = $true
        $settingsHwnd = $p.MainWindowHandle
        break
    }
}

# Capture main window state
Capture-Window $mainHwnd "$OutputDir\02_after_settings_click.png"

if ($foundSettings) {
    Add-Test "Settings Dialog" $true
    Capture-Window $settingsHwnd "$OutputDir\02_settings_dialog.png"
} else {
    Add-Test "Settings Dialog" $false "Settings dialog not detected as separate window"
    Log "Note: Tkinter dialogs may share main process - checking visually"
}

# TEST 3: Final Summary
Log ""
Log "=========================================="
Log "TEST SUMMARY"
Log "=========================================="

$passed = ($results.tests | Where-Object { $_.passed }).Count
$total = $results.tests.Count
$results.status = if ($results.errors.Count -eq 0) { "passed" } else { "partial" }
$results.summary = "$passed/$total tests passed"

Log "Result: $($results.summary)"
Log "Screenshots: $($results.screenshots.Count) captured"

# Cleanup
Log ""
Log "Cleanup: Closing application"
Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

Save-Results
Log ""
Log "Results saved to: $resultFile"
Log "Done!"
