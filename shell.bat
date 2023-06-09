@echo OFF

echo "Setting environment variables to ensure R.exe and python.exe are available"

set PYTHON_BIN_DIR=C:\Program Files\Python311

echo "Assuming PYTHON_BIN_DIR=%PYTHON_BIN_DIR%"

set PATH=%R_BIN_DIR%;%PYTHON_BIN_DIR%;%PATH%

:: cmd
powershell
