# Instalación de KinePro (requiere Python 3.11+)
Set-Location $PSScriptRoot
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
Write-Host "Listo. Ejecute run_kinepro.bat"
