@echo off
chdir /d "%~dp0"
chcp 65001 >nul
net session >nul 2>&1
if %errorLevel% equ 0 (
    echo [Admin Mode] Running in background...
) else (
    echo [Normal Mode] Running in background...
)

echo Set WshShell = CreateObject("WScript.Shell") > temp.vbs
echo WshShell.CurrentDirectory = "%CD%" >> temp.vbs
echo WshShell.Run "python main.py", 0, False >> temp.vbs
echo Set WshShell = Nothing >> temp.vbs
start temp.vbs
timeout /t 1 /nobreak >nul
del temp.vbs
exit