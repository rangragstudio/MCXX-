@echo off
schtasks /Delete /TN MCXAgency /F
schtasks /Delete /TN MCXDashboard /F
echo Schedules removed. Your files are untouched. (If the dashboard window is still open, close it from Task Manager: pythonw.exe)
pause
