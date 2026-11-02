@echo off
chcp 65001 >nul
title AAROHI - one-click setup
cd /d "%~dp0"
echo.
echo  ==========================================
echo   AAROHI Companion - Windows setup
echo  ==========================================
echo   Installs Python deps, desktop control,
echo   pins Hinglish Swara voice, starts server.
echo  ==========================================
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*
if errorlevel 1 (
  echo.
  echo  Setup failed. See messages above.
  pause
  exit /b 1
)
exit /b 0
