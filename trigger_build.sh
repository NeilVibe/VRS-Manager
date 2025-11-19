#!/bin/bash
#
# Trigger GitHub Actions build manually
# Usage: ./trigger_build.sh
#

echo "========================================"
echo "Triggering GitHub Actions Build"
echo "========================================"

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI (gh) not found. Installing..."

    # Try to install gh CLI
    if command -v apt-get &> /dev/null; then
        echo "Using apt-get to install gh..."
        curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
        sudo apt-get update
        sudo apt-get install gh -y
    else
        echo "ERROR: Cannot install gh CLI automatically on this system."
        echo "Please install manually from: https://cli.github.com/"
        exit 1
    fi
fi

# Trigger the workflow
echo ""
echo "Triggering 'Build Executables' workflow..."
gh workflow run "Build Executables" --ref main

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Build triggered successfully!"
    echo ""
    echo "Check status at: https://github.com/NeilVibe/VRS-Manager/actions"
    echo "Or run: gh run list --workflow='Build Executables'"
else
    echo ""
    echo "✗ Failed to trigger build"
    echo "You may need to authenticate: gh auth login"
fi

echo "========================================"
