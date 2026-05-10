@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo   星巢 V11.0 全量测试
echo   ======================================
echo.
echo   L1 L3 L5 (无LLM依赖, 快速):
python ceshi_quanbu.py --tools --fuzhiti
echo.
echo   ======================================
echo   如需完整 L2 测试 (需LLM, 较慢):
echo     python ceshi_quanbu.py --cli
echo   ======================================
pause
