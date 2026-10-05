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
    & pip install google-genai pyttsx3 speechrecognition customtkinter requests tinytuya pyperclip psutil mcp pycaw comtypes --quiet
    Write-Host "[OK] Todas las librerías necesarias están instaladas." -ForegroundColor Green
    Write-Host ""

    # 2. CONFIGURACIÓN DEL ENTORNO SEGURO
    Write-Host "[2/3] Verificando variables de entorno del sistema..." -ForegroundColor Yellow
    if ([string]::IsNullOrEmpty($ApiKey) -or $ApiKey -eq "tu_clave_aqui") {
        # Si no pasas clave, busca o define una temporal aquí para la sesión
        $env:GEMINI_API_KEY = "AIzaSyTuClaveRealDeGeminiAqui"
    } else {
        $env:GEMINI_API_KEY = $ApiKey
    }

    if ([string]::IsNullOrEmpty($env:GEMINI_API_KEY) -or $env:GEMINI_API_KEY -eq "AIzaSyTuClaveRealDeGeminiAqui") {
        throw "La variable GEMINI_API_KEY está vacía. Por favor edite el script y ponga su clave válida de Google AI Studio."
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

    # Arranca Python de forma directa asegurando el subproceso
    & python $ScriptPath

} catch {
    Write-Host ""
    Write-Host "====================================================================" -ForegroundColor Red
    Write-Host "[ERROR CRÍTICO DEL SISTEMA]" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor LightRed
    Write-Host "====================================================================" -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "[PROCESO FINALIZADO] Presione cualquier tecla para cerrar la consola de depuración..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
