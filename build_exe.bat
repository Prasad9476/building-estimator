@echo off
setlocal enabledelayedexpansion
title Building BuildingEstimator.exe
cls
cd /d "c:\Users\prasa\OneDrive\Desktop\kaushik mini"

echo.
echo ========================================
echo Building BuildingEstimator.exe
echo ========================================
echo This may take 5-10 minutes... please wait
echo.

python -m PyInstaller --onefile --add-data "templates;templates;templates" --name "BuildingEstimator" --hidden-import=flask --hidden-import=werkzeug --hidden-import=jinja2 app_exe.py

echo.
echo ========================================
echo Build process completed!
echo ========================================
echo.

if exist "dist\BuildingEstimator.exe" (
    echo SUCCESS! BuildingEstimator.exe created
    echo.
    echo Location: dist\BuildingEstimator.exe
    echo Size: 
    dir dist\BuildingEstimator.exe
    echo.
    echo You can now:
    echo 1. Copy BuildingEstimator.exe to other systems
    echo 2. Double-click to run (no installation needed)
    echo 3. Share via email or USB drive
    echo.
) else (
    echo Checking build output...
    if exist "dist" (
        echo dist folder found. Contents:
        dir dist
    ) else (
        echo WARNING: dist folder not found
    )
)

pause

