<#
.SYNOPSIS
    Script de inicialización y control de entorno para JARVIS OS.
#>
param (
    [string]$ApiKey = $env:GEMINI_API_KEY
)

Clear-Host
$ErrorActionPreference = "Stop"

Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "             INICIALIZANDO PREPARATIVOS DE J.A.R.V.I.S. OS          " -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

try {
    # 1. COMPROBACIÓN E INSTALACIÓN DE LIBRERÍAS
    Write-Host "[1/3] Validando entorno de dependencias Python..." -ForegroundColor Yellow
    $Marca = Join-Path $PSScriptRoot ".jarvis_ok"
    if (-not (Test-Path $Marca)) {
        & pip install google-genai pyttsx3 speechrecognition customtkinter requests tinytuya pyperclip psutil mcp pycaw comtypes pyaudio --quiet
        if ($LASTEXITCODE -ne 0) { throw "Falló la instalación de dependencias (pip). Revise su conexión y que Python esté en el PATH." }
        New-Item -ItemType File -Path $Marca -Force | Out-Null
    }
    Write-Host "[OK] Todas las librerías necesarias están instaladas." -ForegroundColor Green
    Write-Host ""

    # 2. CONFIGURACIÓN DEL ENTORNO SEGURO
    Write-Host "[2/3] Verificando variables de entorno del sistema..." -ForegroundColor Yellow
    if ([string]::IsNullOrEmpty($ApiKey)) { $ApiKey = [Environment]::GetEnvironmentVariable("GEMINI_API_KEY", "User") }
    if ([string]::IsNullOrEmpty($ApiKey) -or $ApiKey -eq "tu_clave_aqui") {
        # Primera ejecución: pide la clave una sola vez y la guarda para el usuario actual
        $ApiKey = Read-Host "Pegue su clave de Google AI Studio (se guarda solo en su usuario de Windows)"
        if (-not [string]::IsNullOrWhiteSpace($ApiKey)) {
            [Environment]::SetEnvironmentVariable("GEMINI_API_KEY", $ApiKey.Trim(), "User")
        }
    }
    $env:GEMINI_API_KEY = "$ApiKey".Trim()

    if ([string]::IsNullOrEmpty($env:GEMINI_API_KEY)) {
        throw "No se ingresó ninguna clave GEMINI_API_KEY. Obtenga una gratis en https://aistudio.google.com/apikey"
    }
    Write-Host "[OK] Variables de entorno de la IA inyectadas correctamente." -ForegroundColor Green
    Write-Host ""

    # 3. VERIFICACIÓN DEL ARCHIVO FUENTE Y EJECUCIÓN
    Write-Host "[3/3] Iniciando Servidor Central J.A.R.V.I.S..." -ForegroundColor Yellow
    $ScriptPath = Join-Path $PSScriptRoot "jarvis_system_mcp.py"

    if (-not (Test-Path $ScriptPath)) {
        throw "No se encontró el archivo maestro 'jarvis_system_mcp.py' en la ruta actual: $PSScriptRoot"
    }

    Write-Host "====================================================================" -ForegroundColor Cyan
    Write-Host "Lanzando GUI y motores conversacionales..." -ForegroundColor Gray
    Write-Host ""

    # Lanza la interfaz sin ventana de consola (pythonw) y cierra esta consola
    $Python = (Get-Command python).Source
    $PythonW = Join-Path (Split-Path $Python) "pythonw.exe"
    if (-not (Test-Path $PythonW)) { $PythonW = $Python }
    Start-Process -FilePath $PythonW -ArgumentList "`"$ScriptPath`"" -WorkingDirectory $PSScriptRoot

} catch {
    $Fallo = $true
    Write-Host ""
    Write-Host "====================================================================" -ForegroundColor Red
    Write-Host "[ERROR CRÍTICO DEL SISTEMA]" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor LightRed
    Write-Host "====================================================================" -ForegroundColor Red
} finally {
    Write-Host ""
    if ($Fallo) { Write-Host "[PROCESO FINALIZADO] Presione cualquier tecla para cerrar..." -ForegroundColor Gray }
    if ($Fallo) { $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") }
}
