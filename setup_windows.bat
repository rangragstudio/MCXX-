@echo off
cd /d "%~dp0"
echo === MCX paper-trading agency: one-time setup ===
python --version >nul 2>&1
if errorlevel 1 (
  echo Python is not installed. Install Python 3.10+ from python.org and TICK "Add python.exe to PATH", then run this file again.
  pause & exit /b 1
)
for /f "delims=" %%i in ('where python') do (set PY=%%i & goto :havepy)
:havepy
echo Installing data package...
python -m pip install --quiet yfinance tzdata
if errorlevel 1 ( echo pip install failed. Check your internet. & pause & exit /b 1 )
echo Matching prices to MCX (press Enter to skip any; skipped ones use unscaled proxy prices):
set /p P1=MCX Gold Petal price per gram (for example 15300): 
if not "%P1%"=="" python fetch_data.py --calibrate GOLDPETAL %P1%
set /p P2=MCX Silver 100 price (rupees per 10 g, for example 2350): 
if not "%P2%"=="" python fetch_data.py --calibrate SILVER100 %P2%
set /p P3=MCX Crude Oil Mini price per barrel (for example 9000): 
if not "%P3%"=="" python fetch_data.py --calibrate CRUDEOILM %P3%
echo Running the first paper-trading step...
python run_scheduled.py
type logs\run.log
echo Creating the daily schedule (8:00 AM; catches up if the PC was off)...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$a=New-ScheduledTaskAction -Execute '%PY%' -Argument 'run_scheduled.py' -WorkingDirectory '%~dp0'; $t=New-ScheduledTaskTrigger -Daily -At 8:00AM; $s=New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries; Register-ScheduledTask -TaskName 'MCXAgency' -Action $a -Trigger $t -Settings $s -Force | Out-Null"
if errorlevel 1 ( echo Could not create the schedule. Right-click this file and choose Run as administrator. & pause & exit /b 1 )
echo Setting the dashboard to start when you log in...
set PYW=%PY:python.exe=pythonw.exe%
powershell -NoProfile -ExecutionPolicy Bypass -Command "$a=New-ScheduledTaskAction -Execute '%PYW%' -Argument 'dashboard_server.py' -WorkingDirectory '%~dp0'; $t=New-ScheduledTaskTrigger -AtLogOn; $s=New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit 0; Register-ScheduledTask -TaskName 'MCXDashboard' -Action $a -Trigger $t -Settings $s -Force | Out-Null; Start-ScheduledTask -TaskName 'MCXDashboard'"
timeout /t 3 >nul
start http://127.0.0.1:8765
echo.
echo DONE. Leave this folder where it is. After 15 trading days a file named RESULT_AFTER_15_DAYS.md opens by itself.
echo Live dashboard: http://127.0.0.1:8765  (or double-click open_dashboard.bat). Progress log: logs\run.log
pause
