@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo .venv not found. Please create venv first.
  pause
  exit /b 1
)

set "ICON_PATH=%~dp0data\icon.ico"
if not exist "%ICON_PATH%" (
  echo Icon not found: %ICON_PATH%
  pause
  exit /b 1
)

".venv\Scripts\python.exe" -m pip install --upgrade pip pyinstaller
".venv\Scripts\python.exe" sync_version.py
if errorlevel 1 (
  pause
  exit /b 1
)

REM onedir build with synced app/exe version
".venv\Scripts\pyinstaller.exe" ^
  --onedir ^
  --noconsole ^
  --name "L1L2" ^
  --icon "%ICON_PATH%" ^
  --version-file "version_info.txt" ^
  --paths src ^
  run_app.py

REM Copy data folders next to EXE (PyInstaller puts them under _internal by default)
if not exist "dist\\L1L2\\database" mkdir "dist\\L1L2\\database"
if not exist "dist\\L1L2\\files" mkdir "dist\\L1L2\\files"
if not exist "dist\\L1L2\\translations" mkdir "dist\\L1L2\\translations"
if not exist "dist\\L1L2\\settings" mkdir "dist\\L1L2\\settings"

xcopy "database\\*" "dist\\L1L2\\database\\" /E /I /Y >nul
xcopy "files\\*" "dist\\L1L2\\files\\" /E /I /Y >nul
xcopy "translations\\*" "dist\\L1L2\\translations\\" /E /I /Y >nul
xcopy "settings\\*" "dist\\L1L2\\settings\\" /E /I /Y >nul

echo.
echo Build complete. EXE is in dist\L1L2\L1L2.exe

REM Cleanup build artifacts
if exist "build" rmdir /s /q "build"
pause
