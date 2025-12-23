#!/bin/bash
# ============================================================================
# VRS MANAGER PLAYGROUND INSTALL - WSL WRAPPER
# ============================================================================
# Purpose: Run playground_install.ps1 from WSL
# Usage: ./playground_install.sh [--launch] [--test]
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse arguments
LAUNCH_FLAG=""
TEST_FLAG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --launch)
            LAUNCH_FLAG="-LaunchAfterInstall"
            shift
            ;;
        --test)
            TEST_FLAG="-RunTests"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "========================================"
echo "VRS MANAGER PLAYGROUND INSTALL (WSL)"
echo "========================================"
echo ""

# Convert WSL path to Windows path
SCRIPT_WIN_PATH=$(wslpath -w "$SCRIPT_DIR/playground_install.ps1")

echo "Running PowerShell script: $SCRIPT_WIN_PATH"
echo ""

# Execute PowerShell from Windows
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe \
    -ExecutionPolicy Bypass \
    -File "$SCRIPT_WIN_PATH" \
    $LAUNCH_FLAG \
    $TEST_FLAG

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "[OK] Playground install completed successfully"
else
    echo "[ERROR] Playground install failed (exit code: $EXIT_CODE)"
fi

exit $EXIT_CODE
