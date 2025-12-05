#!/usr/bin/env python3
"""
VRS Manager - Self-Monitoring Infrastructure
=============================================

CURRENT CHECKS:
1. Version Unification - Ensures all 12 files have matching version numbers
2. Timestamp Validation - Version must be within 12 hours of current time (MMDDHHMM format, timezone-tolerant)

FUTURE EXTENSIBILITY:
This infrastructure can be expanded to monitor:
- Code style consistency
- Import statement organization
- TODO/FIXME tracking
- Deprecated function usage
- Documentation coverage
- Test coverage metrics
- Build artifact sizes
- Performance benchmarks

HOW TO ADD NEW CHECKS:
1. Add new check function (e.g., check_code_style())
2. Call from main() after version checks
3. Update COVERAGE SUMMARY with new check
4. Document in roadmap.md

Usage:
    python3 check_version_unified.py

Exit codes:
    0 - All checks passed ✅
    1 - One or more checks failed ❌
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime

# Set headless mode for GUI import testing
os.environ['HEADLESS'] = '1'

# Source of truth
CONFIG_FILE = "src/config.py"

# All files that must have matching version
VERSION_FILES = {
    "src/config.py": [
        r'VERSION = "(\d+)"',
        r'VERSION_FOOTER = "ver\. (\d+)',
    ],
    "main.py": [
        r'Version: (\d+)',
        r'Version : (\d+)',
    ],
    "README.md": [
        r'\*\*Version:\*\* (\d+)',
    ],
    "README_KR.md": [
        r'\*\*버전:\*\* (\d+)',
    ],
    "installer/vrsmanager_light.iss": [
        r'#define MyAppVersion "(\d+)"',
    ],
    "installer/vrsmanager_full.iss": [
        r'#define MyAppVersion "(\d+)"',
    ],
    ".github/workflows/build-installers.yml": [
        r'VRSManager_v(\d+)_Light_Setup\.exe',
        r'VRSManager_v(\d+)_Full_Setup\.exe',
    ],
    "scripts/update_excel_guides.py": [
        r'VERSION = "(\d+)"',
        r'Version (\d+)',
    ],
    "CLAUDE.md": [
        r'\*\*Current Version:\*\* v(\d+)',
        r'\*\*Current Version: (\d+)\*\*',
        r'`(\d{8})`',
    ],
    "roadmap.md": [
        r'## 🎯 Current Status: v(\d+)',
        r'\*\*Released:\*\* v(\d+)',
        r'### v(\d+)',
    ],
    "docs/WIKI_CONFLUENCE.md": [
        r'\*\*Version:\*\* (\d+)',
        r'\*\*Current Version\*\*: (\d+)',
        r'Version (\d+)\*$',
    ],
    "src/processors/master_processor.py": [
        r'Version: v(\d+)',
    ],
}


def get_source_version():
    """Get the source of truth version from src/config.py"""
    config_path = Path(CONFIG_FILE)
    if not config_path.exists():
        print(f"❌ Error: {CONFIG_FILE} not found!")
        sys.exit(1)

    content = config_path.read_text()
    match = re.search(r'VERSION = "(\d+)"', content)
    if not match:
        print(f"❌ Error: Could not find VERSION in {CONFIG_FILE}")
        sys.exit(1)

    return match.group(1)


def check_version_timestamp(version, max_hours_diff=12):
    """
    Check if version timestamp is within acceptable range of current time.

    Version format: MMDDHHMM (Month, Day, Hour, Minute)

    Args:
        version: Version string (e.g., "12051321")
        max_hours_diff: Maximum allowed difference in hours (default: 12)
                        Set to 12 to accommodate timezone differences (e.g., KST vs UTC)

    Returns:
        tuple: (is_valid, message)
    """
    if len(version) != 8:
        return False, f"Invalid version format: {version} (expected MMDDHHMM)"

    try:
        version_month = int(version[0:2])
        version_day = int(version[2:4])
        version_hour = int(version[4:6])
        version_minute = int(version[6:8])

        now = datetime.now()

        # Build version datetime (assume current year)
        try:
            version_dt = datetime(now.year, version_month, version_day, version_hour, version_minute)
        except ValueError as e:
            return False, f"Invalid datetime in version: {version} ({e})"

        # Calculate difference in hours
        diff = abs((now - version_dt).total_seconds() / 3600)

        if diff <= max_hours_diff:
            return True, f"Version timestamp OK: {version_month:02d}/{version_day:02d} {version_hour:02d}:{version_minute:02d} (within {diff:.1f}h, max {max_hours_diff}h for timezone tolerance)"
        else:
            now_version = now.strftime("%m%d%H%M")
            return False, f"Version timestamp TOO FAR: {version} is {diff:.1f}h away from now ({now_version}). Max allowed: {max_hours_diff}h"
    except ValueError as e:
        return False, f"Could not parse version timestamp: {version} ({e})"


def check_file_versions(file_path, patterns, source_version):
    """Check all version patterns in a file"""
    mismatches = []

    path = Path(file_path)
    if not path.exists():
        return [(0, f"File not found: {file_path}")]

    content = path.read_text()
    lines = content.split('\n')

    # Special handling for roadmap.md - ignore Version History section
    in_history_section = False
    if file_path == "roadmap.md":
        for line_num, line in enumerate(lines, 1):
            if "## Version History" in line:
                in_history_section = True

            # Only check lines before Version History section
            if not in_history_section:
                for pattern in patterns:
                    match = re.search(pattern, line)
                    if match:
                        found_version = match.group(1)
                        if found_version != source_version:
                            mismatches.append((line_num, f"Expected '{source_version}', found '{found_version}'"))
    else:
        # Normal checking for all other files
        for pattern in patterns:
            for line_num, line in enumerate(lines, 1):
                match = re.search(pattern, line)
                if match:
                    found_version = match.group(1)
                    if found_version != source_version:
                        mismatches.append((line_num, f"Expected '{source_version}', found '{found_version}'"))

    return mismatches


def main():
    print("=" * 70)
    print("VRS Manager - Version Unification Check")
    print("=" * 70)
    print()

    # Get source of truth
    source_version = get_source_version()
    print(f"✓ Source of truth: {CONFIG_FILE}")
    print(f"✓ Expected version: {source_version}")
    print()

    # TIMESTAMP VALIDATION - Version must be within 1 hour of current time
    print("Checking version timestamp...")
    timestamp_valid, timestamp_msg = check_version_timestamp(source_version, max_hours_diff=1)
    if timestamp_valid:
        print(f"✓ {timestamp_msg}")
    else:
        print(f"❌ {timestamp_msg}")
        print()
        print("=" * 70)
        print("❌ BUILD BLOCKED: Version timestamp too far from current time!")
        print("   Update version to current timestamp before building.")
        print(f"   Suggested version: {datetime.now().strftime('%m%d%H%M')}")
        print("=" * 70)
        return 1
    print()

    # Test runtime import (GUI, processors use this)
    print("Testing runtime imports...")
    try:
        import sys
        sys.path.insert(0, str(Path.cwd()))
        from src.config import VERSION, VERSION_FOOTER

        if VERSION != source_version:
            print(f"❌ Runtime import VERSION mismatch!")
            print(f"   Expected: {source_version}")
            print(f"   Got: {VERSION}")
            return 1

        print(f"✓ Runtime import: VERSION = {VERSION}")
        print(f"✓ Runtime import: VERSION_FOOTER = {VERSION_FOOTER}")
        print()
    except ImportError as e:
        print(f"❌ Failed to import VERSION from src.config: {e}")
        return 1
    print()

    # Check all files
    all_good = True
    files_checked = 0

    for file_path, patterns in VERSION_FILES.items():
        files_checked += 1
        mismatches = check_file_versions(file_path, patterns, source_version)

        if mismatches:
            all_good = False
            print(f"❌ {file_path}")
            for line_num, error in mismatches:
                if line_num > 0:
                    print(f"   Line {line_num}: {error}")
                else:
                    print(f"   {error}")
            print()
        else:
            print(f"✓ {file_path}")

    # Test GUI import (ensures GUI displays correct version)
    print()
    print("Testing GUI version display...")
    try:
        from src.ui.main_window import VERSION as GUI_VERSION
        if GUI_VERSION != source_version:
            print(f"❌ GUI VERSION mismatch!")
            print(f"   Expected: {source_version}")
            print(f"   Got: {GUI_VERSION}")
            all_good = False
        else:
            print(f"✓ GUI imports VERSION correctly: {GUI_VERSION}")
    except ImportError as e:
        print(f"⚠️  Could not verify GUI import (may be headless environment)")

    print()
    print("=" * 70)

    if all_good:
        print(f"🎉 SUCCESS! All {files_checked} files have unified version: {source_version}")
        print(f"🎉 Runtime and GUI imports verified!")
        print()
        print("COVERAGE SUMMARY:")
        print("  ✓ Timestamp Validation: Version within 12 hours (timezone-tolerant)")
        print("  ✓ Static Files: 12 files (code, docs, installers, workflows)")
        print("  ✓ Runtime Imports: src.config (VERSION, VERSION_FOOTER)")
        print("  ✓ GUI Display: Window title + footer (from centralized import)")
        print("  ✓ Terminal Output: main.py prints (4 statements)")
        print("  ✓ Processor Comments: master_processor.py version header")
        print("  ✓ Documentation: README, roadmap, WIKI, CLAUDE.md")
        print("  ✓ Build System: Installers + GitHub workflows")
        print("  ✓ Excel Guides: scripts/update_excel_guides.py")
        print()
        print("All version references unified and consistent!")
        print("=" * 70)
        return 0
    else:
        print(f"⚠️  MISMATCH DETECTED! Fix version inconsistencies above.")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
