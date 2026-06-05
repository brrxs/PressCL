@echo off
echo ============================================
echo  PressCL - Configuracion
echo ============================================
echo.

set ROOT=%~dp0
set ROOT=%ROOT:~0,-1%

cd /d "%ROOT%\app"

echo [1/4] Creando entorno virtual...
python -m venv .venv
if errorlevel 1 (
    echo ERROR: No se pudo crear el entorno virtual.
    echo Asegurate de tener Python 3.10 o superior instalado.
    pause
    exit /b 1
)

echo [2/4] Instalando dependencias...
.venv\Scripts\pip install -r requirements.txt streamlit pandas --quiet
if errorlevel 1 (
    echo ERROR: Fallo la instalacion de dependencias.
    pause
    exit /b 1
)

echo [3/4] Instalando navegador Chromium para Playwright...
.venv\Scripts\python -m playwright install chromium
if errorlevel 1 (
    echo ERROR: Fallo la instalacion de Playwright.
    pause
    exit /b 1
)

echo [4/4] Creando acceso directo PressCL...
powershell -NoProfile -Command ^
  "$root = '%ROOT%'; ^
   $ws = New-Object -ComObject WScript.Shell; ^
   $sc = $ws.CreateShortcut($root + '\PressCL.lnk'); ^
   $sc.TargetPath = 'wscript.exe'; ^
   $sc.Arguments = '\"' + $root + '\app\launch.vbs\"'; ^
   $sc.WorkingDirectory = $root + '\app'; ^
   $sc.Description = 'PressCL'; ^
   $sc.IconLocation = $root + '\app\style-kit\assets\favicon.ico,0'; ^
   $sc.Save()"

echo.
echo ============================================
echo  Listo. Abre PressCL para iniciar la app.
echo ============================================
pause
