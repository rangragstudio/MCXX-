@echo off
cd /d "%~dp0"
start "MCX dashboard server" /min python dashboard_server.py
timeout /t 2 >nul
start http://127.0.0.1:8765
