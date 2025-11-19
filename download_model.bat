@echo off
REM ============================================================================
REM VRS Manager - BERT Model Offline Setup
REM ============================================================================
REM This script downloads the Korean BERT model for StrOrigin Change Analysis
REM to enable offline use.
REM
REM Requirements: Python 3.7+ with internet connection
REM Output: models/kr-sbert/ directory (447MB)
REM ============================================================================

echo.
echo ============================================================================
echo VRS Manager - BERT Model Offline Setup
echo ============================================================================
echo.
echo This will download the Korean BERT model (447MB) for offline use.
echo.
echo Requirements:
echo   - Python 3.7 or newer
echo   - Internet connection
echo   - ~1GB free disk space (temporary + final)
echo.
echo ============================================================================
echo.

REM Check if Python is installed
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.7+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

python --version
echo   OK - Python found
echo.

REM Check if pip is available
echo [2/4] Checking pip installation...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: pip is not available!
    echo.
    echo For Python 3.7+, pip should be included by default.
    echo Try reinstalling Python from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

python -m pip --version
echo   OK - pip found
echo.

REM Install sentence-transformers
echo [3/4] Installing required packages (sentence-transformers)...
echo This may take a few minutes...
echo.

python -m pip install sentence-transformers --quiet
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install sentence-transformers
    echo.
    echo Please check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo   OK - Packages installed
echo.

REM Download model
echo [4/4] Downloading BERT model (447MB)...
echo This will take 5-10 minutes depending on internet speed...
echo.

python -c "from sentence_transformers import SentenceTransformer; print('  Downloading model from Hugging Face...'); model = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS'); model.save('./models/kr-sbert'); print('  Model saved to: models/kr-sbert/')"

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to download model
    echo.
    echo Possible causes:
    echo   - No internet connection
    echo   - Hugging Face servers unavailable
    echo   - Insufficient disk space
    echo.
    echo Please try again later.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo SUCCESS! Model downloaded and ready for offline use.
echo ============================================================================
echo.
echo Location: models/kr-sbert/
echo Size: ~447MB
echo.
echo You can now use VRS Manager offline with StrOrigin Change Analysis.
echo This computer or other offline computers can use this model.
echo.
echo To transfer to another computer:
echo   1. Copy the entire "models" folder
echo   2. Place it next to VRSManager.exe
echo.
echo ============================================================================
echo.
pause
