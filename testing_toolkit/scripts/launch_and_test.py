#!/usr/bin/env python3
"""
VRS Manager Autonomous GUI Test Runner
======================================

Launches VRS Manager and performs automated UI testing using pyautogui.
Takes screenshots at each step for visual verification.

Usage:
    python launch_and_test.py [--app-path PATH] [--screenshot-dir DIR]

Requirements:
    pip install pyautogui pillow pygetwindow
"""

import os
import sys
import time
import subprocess
import argparse
from datetime import datetime

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pyautogui
    import pygetwindow as gw
    from PIL import ImageGrab
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install pyautogui pillow pygetwindow")
    sys.exit(1)

# Configuration
DEFAULT_APP_PATH = r"C:\NEIL_PROJECTS_WINDOWSBUILD\VRSManagerProject\Playground\VRSManager\VRSManager.exe"
DEFAULT_SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "screenshots")

# Disable pyautogui fail-safe for automated testing
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.1


class TestResult:
    """Store test results."""
    def __init__(self):
        self.passed = []
        self.failed = []
        self.screenshots = []

    def add_pass(self, name):
        self.passed.append(name)
        log(f"  PASS: {name}", "OK")

    def add_fail(self, name, reason):
        self.failed.append((name, reason))
        log(f"  FAIL: {name} - {reason}", "ERROR")

    def add_screenshot(self, path):
        self.screenshots.append(path)

    def summary(self):
        total = len(self.passed) + len(self.failed)
        log("=" * 60)
        log(f"TEST RESULTS: {len(self.passed)}/{total} passed")
        log("=" * 60)
        if self.failed:
            log("FAILURES:", "ERROR")
            for name, reason in self.failed:
                log(f"  - {name}: {reason}", "ERROR")
        log(f"Screenshots: {len(self.screenshots)} saved")
        return len(self.failed) == 0


def log(message, level="INFO"):
    """Log with timestamp and color."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    colors = {
        "INFO": "",
        "OK": "\033[92m",      # Green
        "WARN": "\033[93m",    # Yellow
        "ERROR": "\033[91m",   # Red
        "RESET": "\033[0m"
    }
    color = colors.get(level, "")
    reset = colors["RESET"] if color else ""
    print(f"[{timestamp}] [{level}] {color}{message}{reset}")


def capture_window(window_title, output_path, results):
    """Capture window screenshot."""
    try:
        windows = gw.getWindowsWithTitle(window_title)
        if not windows:
            # Try partial match
            all_windows = gw.getAllWindows()
            windows = [w for w in all_windows if window_title.lower() in w.title.lower()]

        if not windows:
            log(f"Window not found: {window_title}", "WARN")
            # Fallback to full screen
            img = ImageGrab.grab()
            img.save(output_path)
            results.add_screenshot(output_path)
            return output_path

        window = windows[0]
        window.activate()
        time.sleep(0.3)

        # Get window bounds with padding
        bbox = (
            max(0, window.left),
            max(0, window.top),
            window.right,
            window.bottom
        )

        img = ImageGrab.grab(bbox=bbox)
        img.save(output_path)
        results.add_screenshot(output_path)
        log(f"Screenshot: {os.path.basename(output_path)}")
        return output_path

    except Exception as e:
        log(f"Screenshot failed: {e}", "ERROR")
        return None


def find_and_click(text_or_image, window_title=None, timeout=5):
    """Find and click element."""
    start = time.time()

    while time.time() - start < timeout:
        try:
            # If window specified, activate it first
            if window_title:
                windows = gw.getWindowsWithTitle(window_title)
                if windows:
                    windows[0].activate()
                    time.sleep(0.2)

            # Try to locate on screen (would need button images)
            # For now, we'll use coordinate-based clicking

            return True
        except Exception:
            time.sleep(0.5)

    return False


def wait_for_window(title, timeout=10):
    """Wait for window to appear."""
    start = time.time()
    while time.time() - start < timeout:
        windows = gw.getWindowsWithTitle(title)
        if windows:
            return windows[0]
        # Try partial match
        all_windows = gw.getAllWindows()
        for w in all_windows:
            if title.lower() in w.title.lower():
                return w
        time.sleep(0.5)
    return None


def click_at_offset(window, x_offset, y_offset):
    """Click at offset from window top-left."""
    window.activate()
    time.sleep(0.2)
    x = window.left + x_offset
    y = window.top + y_offset
    pyautogui.click(x, y)
    time.sleep(0.3)


def run_tests(app_path, screenshot_dir):
    """Run all GUI tests."""
    results = TestResult()

    log("=" * 60)
    log("VRS MANAGER AUTONOMOUS GUI TEST")
    log("=" * 60)
    log(f"App: {app_path}")
    log(f"Screenshots: {screenshot_dir}")
    log("")

    # Ensure screenshot directory exists
    os.makedirs(screenshot_dir, exist_ok=True)

    # ===== TEST 1: Launch Application =====
    log("TEST 1: Launch Application")
    try:
        if not os.path.exists(app_path):
            results.add_fail("Launch", f"App not found: {app_path}")
            return results

        process = subprocess.Popen(app_path)
        time.sleep(3)

        main_window = wait_for_window("VRS Manager", timeout=10)
        if main_window:
            results.add_pass("Application launched")
            capture_window("VRS Manager", os.path.join(screenshot_dir, "01_main_window.png"), results)
        else:
            results.add_fail("Launch", "Window not found after 10 seconds")
            return results

    except Exception as e:
        results.add_fail("Launch", str(e))
        return results

    # ===== TEST 2: Click Settings Button =====
    log("TEST 2: Open Settings Dialog")
    try:
        # Settings button is typically near bottom of main window
        # Approximate coordinates (adjust based on actual layout)
        # Main window is 480x800, Settings button is near bottom
        main_window.activate()
        time.sleep(0.3)

        # Click Settings button (approximate position)
        settings_y = main_window.top + 680  # Near bottom
        settings_x = main_window.left + 240  # Center
        pyautogui.click(settings_x, settings_y)
        time.sleep(0.5)

        # Wait for Settings dialog
        settings_window = wait_for_window("Settings", timeout=5)
        if settings_window:
            results.add_pass("Settings dialog opened")
            capture_window("Settings", os.path.join(screenshot_dir, "02_settings_dialog.png"), results)
        else:
            # Try capturing whatever is on screen
            capture_window("VRS Manager", os.path.join(screenshot_dir, "02_settings_attempt.png"), results)
            results.add_fail("Settings", "Settings dialog not found")

    except Exception as e:
        results.add_fail("Settings", str(e))

    # ===== TEST 3: Open Column Settings =====
    log("TEST 3: Open Column Settings")
    try:
        settings_window = wait_for_window("Settings", timeout=2)
        if settings_window:
            settings_window.activate()
            time.sleep(0.3)

            # Click Column Settings option (second button in dialog)
            column_y = settings_window.top + 180  # Second option
            column_x = settings_window.left + 200  # Center
            pyautogui.click(column_x, column_y)
            time.sleep(0.5)

            # Wait for Column Settings dialog
            column_window = wait_for_window("Column Settings", timeout=5)
            if column_window:
                results.add_pass("Column Settings opened")
                capture_window("Column Settings", os.path.join(screenshot_dir, "03_column_settings.png"), results)
            else:
                capture_window("VRS Manager", os.path.join(screenshot_dir, "03_column_attempt.png"), results)
                results.add_fail("Column Settings", "Column Settings dialog not found")

    except Exception as e:
        results.add_fail("Column Settings", str(e))

    # ===== TEST 4: Verify Button Text Visible =====
    log("TEST 4: Verify Button Visibility")
    try:
        column_window = wait_for_window("Column Settings", timeout=2)
        if column_window:
            # Take high-res screenshot for manual verification
            capture_window("Column Settings", os.path.join(screenshot_dir, "04_button_visibility.png"), results)
            results.add_pass("Button visibility screenshot captured")
            log("  MANUAL CHECK: Verify 'Apply & Save' button text is complete", "WARN")
        else:
            results.add_fail("Button Visibility", "Column Settings not open")

    except Exception as e:
        results.add_fail("Button Visibility", str(e))

    # ===== TEST 5: Check Help Text Visibility =====
    log("TEST 5: Check Help Text Visibility")
    try:
        column_window = wait_for_window("Column Settings", timeout=2)
        if column_window:
            # Scroll down if needed
            column_window.activate()
            pyautogui.scroll(-3)  # Scroll down
            time.sleep(0.3)
            capture_window("Column Settings", os.path.join(screenshot_dir, "05_help_text.png"), results)
            results.add_pass("Help text screenshot captured")
            log("  MANUAL CHECK: Verify all help text is complete (not cut off)", "WARN")
        else:
            results.add_fail("Help Text", "Column Settings not open")

    except Exception as e:
        results.add_fail("Help Text", str(e))

    # ===== CLEANUP =====
    log("CLEANUP: Closing application")
    try:
        # Close dialogs with Escape or close button
        pyautogui.press('escape')
        time.sleep(0.3)
        pyautogui.press('escape')
        time.sleep(0.3)

        # Terminate process
        process.terminate()
        time.sleep(1)
        if process.poll() is None:
            process.kill()
        results.add_pass("Application closed")

    except Exception as e:
        log(f"Cleanup warning: {e}", "WARN")

    return results


def main():
    parser = argparse.ArgumentParser(description="VRS Manager GUI Test Runner")
    parser.add_argument("--app-path", default=DEFAULT_APP_PATH, help="Path to VRSManager.exe")
    parser.add_argument("--screenshot-dir", default=DEFAULT_SCREENSHOT_DIR, help="Screenshot output directory")
    args = parser.parse_args()

    results = run_tests(args.app_path, args.screenshot_dir)
    success = results.summary()

    log("")
    log(f"Screenshots saved to: {args.screenshot_dir}")
    log("")

    if success:
        log("ALL TESTS PASSED - Review screenshots for visual verification", "OK")
        sys.exit(0)
    else:
        log("SOME TESTS FAILED - Check errors above", "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main()
