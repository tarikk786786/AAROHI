@echo off
chcp 65001 >nul
title Start AAROHI
cd /d "%~dp0"

echo Starting AAROHI in the background (port 7777)...
REM Hidden start via start-javis.vbs. Log: server\javis.log. Stop: stop-javis.bat.
wscript //nologo start-javis.vbs

echo.
echo Started. Wait ~10s then open http://127.0.0.1:7777 and press Ctrl+Shift+R.
echo (Stop: stop-javis.bat. Errors: server\javis.log)
timeout /t 4 >nul
