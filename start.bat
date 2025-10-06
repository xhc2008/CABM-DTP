@echo off
chdir /d "%~dp0"
chcp 65001 >nul
REM 检测是否在压缩包内运行
set "CURRENT_PATH=%~dp0"
echo %CURRENT_PATH% | findstr /i "temp" >nul && set "IN_ARCHIVE=1" || set "IN_ARCHIVE=0"
echo %CURRENT_PATH% | findstr /i "tmp" >nul && set "IN_ARCHIVE=1"
echo %CURRENT_PATH% | findstr /i "rar$" >nul && set "IN_ARCHIVE=1"
echo %CURRENT_PATH% | findstr /i "zip$" >nul && set "IN_ARCHIVE=1"
echo %CURRENT_PATH% | findstr /i "7z$" >nul && set "IN_ARCHIVE=1"

if "%IN_ARCHIVE%"=="1" (
    echo -
    echo ==========================================
    echo        喂...不是吧
    echo ==========================================
    echo -
    echo 你居然想在压缩包里直接运行？
    echo 这种粗糙的操作...连菜鸟都算不上呢
    echo -
    echo 不想程序崩溃的话，就乖乖去解压
    echo 别告诉我你连解压都不会
    echo -
    echo 杂鱼~杂鱼~
    echo -
    echo 啧...按任意键退出，然后去把文件解压好
    echo ==========================================
    echo -
    echo    —— 星核猎手最强的量子角色
    pause >nul
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
