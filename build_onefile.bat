@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\\Scripts\\python.exe" (
  echo .venv not found. Please create venv first.
  pause
  exit /b 1
)

set "ICON_PATH=%~dp0data\\icon.ico"
if not exist "%ICON_PATH%" (
  echo Icon not found: %ICON_PATH%
  pause
  exit /b 1
)

".venv\\Scripts\\python.exe" -m pip install --upgrade pip pyinstaller

REM onefile = один .exe, без вбудованих матеріалів
".venv\\Scripts\\pyinstaller.exe" ^
  --onefile ^
  --noconsole ^
  --name "L1L2" ^
  --icon "%ICON_PATH%" ^
  --paths src ^
  run_app.py

REM Copy data folders next to EXE (exclude files with materials)
if not exist "dist\\L1L2" mkdir "dist\\L1L2"
if exist "dist\\L1L2.exe" (
  move /Y "dist\\L1L2.exe" "dist\\L1L2\\L1L2.exe" >nul
)

if not exist "dist\\L1L2\\database" mkdir "dist\\L1L2\\database"
if not exist "dist\\L1L2\\translations" mkdir "dist\\L1L2\\translations"
if not exist "dist\\L1L2\\settings" mkdir "dist\\L1L2\\settings"

xcopy "database\\*" "dist\\L1L2\\database\\" /E /I /Y >nul
xcopy "translations\\*" "dist\\L1L2\\translations\\" /E /I /Y >nul
xcopy "settings\\*" "dist\\L1L2\\settings\\" /E /I /Y >nul

echo.
echo Build complete. EXE is in dist\\L1L2\\L1L2.exe

REM Cleanup build artifacts
if exist "build" rmdir /s /q "build"
pause
