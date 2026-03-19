@echo off
setlocal EnableExtensions

call "%~dp0build_exe.bat" "py -3.8" "win7-8" "requirements-legacy-win7-8.txt"
exit /b %errorlevel%
