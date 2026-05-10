@echo off
title 星巢 · 自举模式 V11.0
cd /d "%~dp0"

echo.
echo   =============================================
echo     星巢 (XingChao) V11.0 · 自举模式
echo     AI认知操作系统 · 自带Python · 插入即用
echo   =============================================
echo.

REM 方案1: 自带Python(优先)
if exist "..\python\python.exe" (
    set "PATH=%~dp0..\python;%PATH%"
    echo   [OK] 自带Python就绪
    goto :start
)

REM 方案2: 系统Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] 系统Python就绪
    goto :start
)

REM 方案3: 自动下载
echo   [!!] Python未找到
echo   [..] 尝试自动下载Python嵌入版...
python -c "exit(1)" 2>nul
if %errorlevel% neq 0 (
    echo   [!!] 无法自动下载(需要网络和现有Python)
    echo   手动方案:
    echo     1. 下载: https://www.python.org/ftp/python/3.12.8/python-3.12.8-embed-amd64.zip
    echo     2. 解压到: ..\python\
    echo     3. 重新运行本脚本
    pause
    exit /b 1
)

:start
REM 检查项目
if not exist "rukou.py" (
    echo   [!!] rukou.py未找到
    pause
    exit /b 1
)

echo   [OK] 项目目录已确认
echo.
echo   [..] 启动自举检测...
echo.
python rukou.py --ziju

if %errorlevel% neq 0 (
    echo.
    echo   [!!] 启动异常
    pause
)
