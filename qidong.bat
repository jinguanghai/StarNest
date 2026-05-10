@echo off
cd /d "%~dp0"
start /min python xingchao_sidecar.py
timeout /t 12
start "" "C:\Users\jin\AppData\Local\Programs\OpenCode\OpenCode.exe"
