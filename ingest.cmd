@echo off
setlocal
set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if not exist "%PYTHON_EXE%" (
  echo Python 3.11 not found at "%PYTHON_EXE%".
  echo Install Python 3.11 or update PYTHON_EXE in ingest.cmd.
  exit /b 1
)
"%PYTHON_EXE%" "%~dp0ingest.py" %*
