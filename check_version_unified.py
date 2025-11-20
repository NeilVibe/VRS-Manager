#!/usr/bin/env python3
"""
Version Unification Checker

Verifies that the version number is consistent across all project files.
This prevents version mismatches that can confuse users and cause build issues.

Usage:
    python3 check_version_unified.py

Exit codes:
    0 - All versions unified ✅
    1 - Version mismatch found ❌
"""

import re
import sys
from pathlib import Path

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
    "update_excel_guides.py": [
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
    "WIKI_CONFLUENCE.md": [
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

    print()
    print("=" * 70)

    if all_good:
        print(f"🎉 SUCCESS! All {files_checked} files have unified version: {source_version}")
        print("=" * 70)
        return 0
    else:
        print(f"⚠️  MISMATCH DETECTED! Fix version inconsistencies above.")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
