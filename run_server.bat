@echo off
title Building Estimation System - Server
color 0A

echo.
echo ========================================
echo Building Estimation System - Server
echo ========================================
echo.

REM Show IP Address
echo Your IP Address:
for /f "delims=" %%a in ('powershell -Command "Get-NetIPConfiguration | Where-Object {$_.IPv4DefaultGateway -ne $null} | Select-Object -ExpandProperty IPv4Address | Select-Object -ExpandProperty IPAddress"') do (
    set IP=%%a
)

if defined IP (
    echo %IP%
) else (
    echo Could not detect IP automatically
    ipconfig /all | findstr /C:"IPv4"
)

echo.
echo ========================================
echo Starting Server...
echo ========================================
echo.
echo Server is running on:
echo   Local:  http://localhost:5000
echo   Network: http://%IP%:5000
echo.
echo Share the Network URL with others to access this system
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
