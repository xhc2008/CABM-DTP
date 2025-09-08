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
:: 检查是否通过右键"以管理员身份运行"启动
net session >nul 2>&1
if %errorLevel% equ 0 (
    echo 【管理员模式】正在以管理员权限运行...
    python main.py
) else (
    echo 【普通模式】正在以非管理员权限运行...
    python main.py
)

pause