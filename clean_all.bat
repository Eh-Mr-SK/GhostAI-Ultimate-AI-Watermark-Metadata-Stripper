@echo off
title Ultimate AI Content Cleaner - Videos & Images
cls
echo ================================================================================
echo    🚀 Ultimate AI Content Cleaner - Videos ^& Images 🚀
echo ================================================================================
echo    Removes visible watermarks (Gemini/Veo, Runway, etc.)
echo    Strips ALL metadata (EXIF, XMP, IPTC, C2PA, GPS, AI tags)
echo    Supports: Videos (MP4, MOV, MKV, AVI) + Images (JPG, PNG, WEBP, HEIC)
echo ================================================================================
echo.

:: Check for Python
set "PYTHON_EXE=python"
%PYTHON_EXE% --version >nul 2>&1
if %errorlevel% neq 0 (
    if exist "%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\python.exe" (
        set "PYTHON_EXE=%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\python.exe"
    ) else (
        echo [ERROR] Python is not installed or not in PATH.
        echo Please install Python and try again.
        pause
        exit /b
    )
)

:: Check for FFmpeg
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] FFmpeg is not installed or not in PATH.
    echo Please install FFmpeg and try again.
    pause
    exit /b
)

:: Install/update requirements
echo Checking dependencies...
%PYTHON_EXE% -m pip install Pillow piexif tqdm colorama --quiet 2>nul

echo Starting Graphical User Interface (GUI)...
start "" %PYTHON_EXE% "%~dp0clean_all.py"
exit
