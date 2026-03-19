@echo off
setlocal EnableExtensions

set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%"

set "VENV_DIR=%SCRIPT_DIR%.venv-build"

echo [1/5] Resetting isolated build virtual environment...
if exist "%VENV_DIR%" rmdir /s /q "%VENV_DIR%"
python -m venv "%VENV_DIR%"
if errorlevel 1 goto :fail

echo [2/5] Upgrading packaging tools in isolated environment...
call "%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto :fail

echo [3/5] Installing runtime requirements plus PyInstaller only...
call "%VENV_DIR%\Scripts\python.exe" -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto :fail

echo [4/5] Building fast-start onedir package from isolated environment...
call "%VENV_DIR%\Scripts\pyinstaller.exe" --clean --noconfirm "InvoiceTool.spec"
if errorlevel 1 goto :fail

echo [5/5] Build completed successfully.
echo Output: "%SCRIPT_DIR%dist\InvoiceTool\InvoiceTool.exe"
popd
exit /b 0

:fail
echo Build failed.
popd
exit /b 1
