@echo off
echo Starting D2L Assignment Assistant (Electron Dev Mode)...
echo.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath 'cmd.exe' -ArgumentList '/c','npm run electron:dev' -WorkingDirectory '%CD%' -WindowStyle Hidden"
exit /b 0
