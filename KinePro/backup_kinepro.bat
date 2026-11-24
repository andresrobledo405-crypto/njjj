@echo off
cd /d "%~dp0"
set STAMP=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%
set STAMP=%STAMP: =0%
mkdir backups\%STAMP%
xcopy /E /I /Y data backups\%STAMP%\data >nul
echo Respaldo creado en backups\%STAMP%
pause
