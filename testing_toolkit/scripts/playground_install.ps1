# ============================================================================
# VRS MANAGER PLAYGROUND INSTALL SCRIPT
# ============================================================================
# Purpose: Install VRS Manager to Playground folder for testing
# Usage: .\playground_install.ps1 [-InstallerPath "path\to\setup.exe"]
# ============================================================================

param(
    [string]$InstallerPath = "",
    [string]$PlaygroundPath = "C:\NEIL_PROJECTS_WINDOWSBUILD\VRSManagerProject\Playground\VRSManager",
    [switch]$SkipClean,
    [switch]$LaunchAfterInstall,
    [switch]$RunTests
)

$ErrorActionPreference = "Stop"

function Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "HH:mm:ss"
    $color = switch ($Level) {
        "INFO" { "White" }
        "OK" { "Green" }
        "WARN" { "Yellow" }
        "ERROR" { "Red" }
        default { "White" }
    }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

function Clean-Playground {
    Log "Cleaning Playground: $PlaygroundPath"

    # Kill any running VRS Manager processes
    $processes = Get-Process -Name "VRSManager*" -ErrorAction SilentlyContinue
    if ($processes) {
        Log "Killing running VRSManager processes..." -Level "WARN"
        $processes | Stop-Process -Force
        Start-Sleep -Seconds 2
    }

    # Remove existing installation
    if (Test-Path $PlaygroundPath) {
        Log "Removing existing installation..."
        Remove-Item -Path $PlaygroundPath -Recurse -Force -ErrorAction SilentlyContinue
    }

    # Create fresh directory
    New-Item -Path $PlaygroundPath -ItemType Directory -Force | Out-Null
    Log "Playground cleaned" -Level "OK"
}

function Install-VRSManager {
    param([string]$Installer)

    if (-not (Test-Path $Installer)) {
        Log "Installer not found: $Installer" -Level "ERROR"
        return $false
    }

    Log "Installing VRS Manager..."
    Log "Installer: $Installer"
    Log "Target: $PlaygroundPath"

    try {
        # NSIS silent install to specific directory
        $args = "/S /D=$PlaygroundPath"
        Start-Process -FilePath $Installer -ArgumentList $args -Wait -NoNewWindow

        # Verify installation
        $exePath = Join-Path $PlaygroundPath "VRSManager.exe"
        if (Test-Path $exePath) {
            Log "Installation successful!" -Level "OK"
            return $true
        } else {
            Log "Installation failed - exe not found" -Level "ERROR"
            return $false
        }
    }
    catch {
        Log "Installation error: $_" -Level "ERROR"
        return $false
    }
}

function Copy-FromBuild {
    Log "Copying from local build..."

    # Look for dist_light or dist_full
    $distPaths = @(
        "C:\path\to\vrsmanager\dist_light\VRSManager",
        "C:\path\to\vrsmanager\dist_full\VRSManager"
    )

    foreach ($dist in $distPaths) {
        if (Test-Path $dist) {
            Log "Found build: $dist"
            Copy-Item -Path "$dist\*" -Destination $PlaygroundPath -Recurse -Force
            Log "Copy complete" -Level "OK"
            return $true
        }
    }

    Log "No local build found" -Level "WARN"
    return $false
}

function Launch-VRSManager {
    $exePath = Join-Path $PlaygroundPath "VRSManager.exe"

    if (-not (Test-Path $exePath)) {
        Log "VRSManager.exe not found" -Level "ERROR"
        return
    }

    Log "Launching VRS Manager..."
    Start-Process -FilePath $exePath
    Log "VRS Manager launched" -Level "OK"
}

function Run-Tests {
    Log "Running automated tests..."

    $testScript = Join-Path $PSScriptRoot "launch_and_test.py"

    if (-not (Test-Path $testScript)) {
        Log "Test script not found: $testScript" -Level "ERROR"
        return
    }

    python $testScript --app-path (Join-Path $PlaygroundPath "VRSManager.exe")
}

# ============================================================================
# MAIN
# ============================================================================

Log "========================================"
Log "VRS MANAGER PLAYGROUND INSTALLER"
Log "========================================"
Log ""

# Step 1: Clean (unless skipped)
if (-not $SkipClean) {
    Clean-Playground
}

# Step 2: Install
if ($InstallerPath) {
    $success = Install-VRSManager -Installer $InstallerPath
} else {
    Log "No installer specified. Trying to copy from local build..." -Level "WARN"
    $success = Copy-FromBuild

    if (-not $success) {
        Log ""
        Log "Usage: .\playground_install.ps1 -InstallerPath 'C:\path\to\VRSManager_Setup.exe'" -Level "INFO"
        Log ""
        exit 1
    }
}

if (-not $success) {
    Log "Installation failed!" -Level "ERROR"
    exit 1
}

# Step 3: Verify
$exePath = Join-Path $PlaygroundPath "VRSManager.exe"
if (Test-Path $exePath) {
    $fileInfo = Get-Item $exePath
    Log ""
    Log "INSTALLATION COMPLETE" -Level "OK"
    Log "  Path: $exePath"
    Log "  Size: $([math]::Round($fileInfo.Length / 1MB, 2)) MB"
    Log ""
} else {
    Log "Verification failed - exe not found" -Level "ERROR"
    exit 1
}

# Step 4: Launch (if requested)
if ($LaunchAfterInstall) {
    Launch-VRSManager
}

# Step 5: Run tests (if requested)
if ($RunTests) {
    Run-Tests
}

Log "Done!"
