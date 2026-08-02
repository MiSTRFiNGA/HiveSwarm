@echo off
title HiVE SWARM
cd /d "%~dp0"
echo.
echo   ============================
echo     HiVE SWARM  -  launching
echo   ============================
echo.
set PORT=8795
REM Kill any listener already bound to this port, then start fresh.
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%PORT% .*LISTENING"') do taskkill /PID %%P /F >nul 2>&1
start "" /min cmd /c "python -m http.server %PORT% --bind 127.0.0.1"
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:%PORT%/index.html"
echo   Game opened at http://127.0.0.1:%PORT%/index.html
echo   (Keep this window open while playing; close it to stop the server.)
echo.
pause >nul
