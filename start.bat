@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo .venv not found. Please create venv first.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" -m src.app
