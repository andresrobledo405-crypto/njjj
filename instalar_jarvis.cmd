@echo off
rem Instala (o actualiza) JARVIS y lo abre. Uso: instalar_jarvis.cmd [rama]   (por defecto: main)
setlocal
set "RAMA=%~1"
if "%RAMA%"=="" set "RAMA=main"
set "REPO=https://github.com/andresrobledo405-crypto/njjj.git"
set "DESTINO=%USERPROFILE%\jarvis"

where git >nul 2>nul || (echo [ERROR] Falta Git. Instale: winget install Git.Git & exit /b 1)
where python >nul 2>nul || (echo [ERROR] Falta Python 3.10+. Instale: winget install Python.Python.3.12 & exit /b 1)

if exist "%DESTINO%\.git" (
    echo Actualizando JARVIS en %DESTINO% ...
    git -C "%DESTINO%" fetch origin "%RAMA%" || exit /b 1
    git -C "%DESTINO%" checkout "%RAMA%" || exit /b 1
    git -C "%DESTINO%" pull origin "%RAMA%" || exit /b 1
) else (
    echo Descargando JARVIS en %DESTINO% ...
    git clone --branch "%RAMA%" "%REPO%" "%DESTINO%" || exit /b 1
)

call "%DESTINO%\JARVIS.bat"
endlocal
