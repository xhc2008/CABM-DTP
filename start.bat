@echo off
echo Set WshShell = CreateObject("WScript.Shell") > temp.vbs
echo WshShell.Run "python main.py", 0, False >> temp.vbs
echo Set WshShell = Nothing >> temp.vbs
start temp.vbs
timeout /t 1 /nobreak >nul
del temp.vbs
exit