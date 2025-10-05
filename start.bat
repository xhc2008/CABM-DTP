@echo off
chdir /d "%~dp0"
chcp 65001 >nul

if not exist ".env" (
    echo Error: .env file not found in current directory!
    echo Please make sure the .env file exists in:
    echo %CD%
    pause
    exit /b 1
)

net session >nul 2>&1
if %errorLevel% equ 0 (
    echo [Admin Mode] Starting...
) else (
    echo [Normal Mode] Starting...
)

python main.py

:: 只在出错时暂停（退出码不为0）
if %errorLevel% neq 0 (
    echo.
    echo Program exited with error code: %errorLevel%
    pause
)
