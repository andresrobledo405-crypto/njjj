@echo off
REM Doble clic: pide permisos de administrador y ejecuta todo-en-uno.ps1 (misma carpeta).
net session >nul 2>&1 || (powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs" & exit /b)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0todo-en-uno.ps1"
pause
