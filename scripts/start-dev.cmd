@echo off
setlocal

set SCRIPT_DIR=%~dp0
echo Frontend URL: http://127.0.0.1:3000
echo Backend URL: http://127.0.0.1:8001
echo.
powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%dev.ps1"
