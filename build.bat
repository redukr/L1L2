@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo .venv not found. Please create venv first.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" -m pip install --upgrade pip pyinstaller

REM onefile = один .exe
".venv\Scripts\pyinstaller.exe" ^
  --onefile ^
  --noconsole ^
  --name "L1L2" ^
  --paths src ^
  run_app.py

echo.
echo Build complete. EXE is in dist\L1L2.exe
pause
