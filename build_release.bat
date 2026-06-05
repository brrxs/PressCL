@echo off
setlocal

:: ── Configuration ─────────────────────────────────────────────────────────────
set NAME=PressCL
set VERSION=0.3

:: Output file name
set ZIPFILE=%NAME%-v%VERSION%.zip

:: ── Build ──────────────────────────────────────────────────────────────────────
echo Building %ZIPFILE%...

:: Remove any previous build
if exist "%ZIPFILE%" del /f /q "%ZIPFILE%"

:: Use PowerShell to create a clean zip excluding dev/runtime folders
powershell -NoProfile -Command ^
  "$src = '%~dp0'; $out = '%~dp0%ZIPFILE%'; ^
   $exclude = @('.git', '.venv', '__pycache__', 'datos', 'logs', 'reports', 'analisis', '*.pyc', '*.pyo', '*.lnk', 'build_release.bat', 'TODO.md'); ^
   $items = Get-ChildItem -Path $src -Exclude $exclude; ^
   Compress-Archive -Path $items.FullName -DestinationPath $out -Force; ^
   Write-Host 'Done:' $out"

echo.
echo PressCL v%VERSION% packaged as %ZIPFILE%
echo Attach this file to the GitHub release for v%VERSION%.
echo.
pause
