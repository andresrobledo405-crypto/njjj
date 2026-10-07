@echo off
rem Deja JARVIS siempre activo: arranca al iniciar sesion y se relanza solo si se cierra o falla.
rem (Si ya hay uno corriendo, la copia nueva se cierra sola.) Ejecutar UNA vez. Sin permisos de administrador.
setlocal
cd /d "%~dp0"

if not exist "%~dp0.jarvis_ok" (
    echo [ERROR] Primero abra JARVIS una vez con JARVIS.vbs para instalar dependencias y poner su clave.
    exit /b 1
)
set "PYW="
for /f "delims=" %%i in ('where pythonw 2^>nul') do if not defined PYW set "PYW=%%i"
if not defined PYW (echo [ERROR] No se encontro pythonw. Instale Python 3. & exit /b 1)

set "ACCION=\"%PYW%\" \"%~dp0jarvis_system_mcp.py\""
schtasks /Create /TN "JARVIS-Inicio" /TR "%ACCION%" /SC ONLOGON /RL LIMITED /F || exit /b 1
schtasks /Create /TN "JARVIS-Vigilante" /TR "%ACCION%" /SC MINUTE /MO 5 /RL LIMITED /F || exit /b 1
schtasks /Run /TN "JARVIS-Inicio" >nul

echo.
echo [OK] JARVIS arrancara al iniciar sesion y se relanzara si se cae (revision cada 5 min).
echo Para quitarlo: desactivar_24x7.cmd
endlocal
