@echo off
chcp 65001 >nul
title Start AAROHI
cd /d "%~dp0"
echo Starting AAROHI in the background (port 7777)...
wscript //nologo start-javis.vbs /open
echo.
echo Dashboard: http://127.0.0.1:7777
echo Stop: stop-javis.bat   Log: server\javis.log
timeout /t 3 >nul
