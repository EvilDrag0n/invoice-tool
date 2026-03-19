@echo off
setlocal EnableExtensions

set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%"

if "%~1"=="" (
    set "PYTHON_CMD=python"
) else (
    set "PYTHON_CMD=%~1"
)

if "%~2"=="" (
    set "BUILD_SUFFIX="
) else (
    set "BUILD_SUFFIX=-%~2"
)

if "%~3"=="" (
    set "REQ_FILE=requirements.txt"
) else (
    set "REQ_FILE=%~3"
)

set "VENV_DIR=%SCRIPT_DIR%.venv-build%BUILD_SUFFIX%"
set "DIST_DIR=%SCRIPT_DIR%dist%BUILD_SUFFIX%"
set "WORK_DIR=%SCRIPT_DIR%build%BUILD_SUFFIX%"

echo [1/5] Resetting isolated build virtual environment...
if exist "%VENV_DIR%" rmdir /s /q "%VENV_DIR%"
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
if exist "%WORK_DIR%" rmdir /s /q "%WORK_DIR%"
call %PYTHON_CMD% -m venv "%VENV_DIR%"
if errorlevel 1 goto :fail

echo [2/5] Upgrading packaging tools in isolated environment...
call "%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto :fail

echo [3/5] Installing runtime requirements plus PyInstaller only...
call "%VENV_DIR%\Scripts\python.exe" -m pip install -r "%REQ_FILE%" pyinstaller
if errorlevel 1 goto :fail

echo [4/5] Building fast-start onedir package from isolated environment...
call "%VENV_DIR%\Scripts\pyinstaller.exe" --clean --noconfirm --distpath "%DIST_DIR%" --workpath "%WORK_DIR%" "InvoiceTool.spec"
if errorlevel 1 goto :fail

echo [5/5] Build completed successfully.
echo Output: "%DIST_DIR%\InvoiceTool\InvoiceTool.exe"
popd
exit /b 0

:fail
echo Build failed.
popd
exit /b 1
