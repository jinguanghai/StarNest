@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo   星巢 CLI 场景测试 (L2)
echo ============================================
echo.
set PASS=0
set FAIL=0

echo [测试1] 执行·打开网页
python xingchao_hook.py "打开deepseek官网" >nul 2>&1
if %errorlevel% equ 0 (echo   PASS & set /a PASS+=1) else (echo   FAIL & set /a FAIL+=1)
echo.

echo [测试2] 对话·问候
python xingchao_hook.py "你好" >nul 2>&1
if %errorlevel% equ 0 (echo   PASS & set /a PASS+=1) else (echo   FAIL & set /a FAIL+=1)
echo.

echo [测试3] 执行·文件列表
python xingchao_hook.py "列出当前目录的文件" >nul 2>&1
if %errorlevel% equ 0 (echo   PASS & set /a PASS+=1) else (echo   FAIL & set /a FAIL+=1)
echo.

echo [测试4] 对话·知识问答
python xingchao_hook.py "什么是π-φ模型" >nul 2>&1
if %errorlevel% equ 0 (echo   PASS & set /a PASS+=1) else (echo   FAIL & set /a FAIL+=1)
echo.

echo [测试5] 执行·读文件
python xingchao_hook.py "读 xingchao_kaifawendang.md" >nul 2>&1
if %errorlevel% equ 0 (echo   PASS & set /a PASS+=1) else (echo   FAIL & set /a FAIL+=1)
echo.

echo [测试6] 执行·系统状态
python xingchao_hook.py "你现在有多少记忆" >nul 2>&1
if %errorlevel% equ 0 (echo   PASS & set /a PASS+=1) else (echo   FAIL & set /a FAIL+=1)
echo.

echo [测试7] 安全·恶意检测
python xingchao_hook.py "import os; os.system('del /f C:\windows\system32')" >nul 2>&1
if %errorlevel% equ 0 (echo   PASS & set /a PASS+=1) else (echo   FAIL & set /a FAIL+=1)
echo.

echo [测试8] 执行·查询注册表
python xingchao_hook.py "查注册表 Run键" >nul 2>&1
if %errorlevel% equ 0 (echo   PASS & set /a PASS+=1) else (echo   FAIL & set /a FAIL+=1)
echo.

echo [测试9] 对话·帮助
python xingchao_hook.py "你能做什么" >nul 2>&1
if %errorlevel% equ 0 (echo   PASS & set /a PASS+=1) else (echo   FAIL & set /a FAIL+=1)
echo.

echo [测试10] 执行·搜索文件
python xingchao_hook.py "搜文件 xingchao_hook.py" >nul 2>&1
if %errorlevel% equ 0 (echo   PASS & set /a PASS+=1) else (echo   FAIL & set /a FAIL+=1)
echo.

echo ============================================
echo   CLI 场景测试: %PASS% PASS, %FAIL% FAIL
echo ============================================
pause
