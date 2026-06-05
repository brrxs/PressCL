@echo off
echo Building release package...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0build_release.ps1"
echo.
pause
