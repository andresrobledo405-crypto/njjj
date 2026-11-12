@echo off
REM Limpieza de Windows + analisis con IA local (Ollama). Ejecutar como Administrador.
REM La IA SOLO aconseja: nunca borra nada por su cuenta.
chcp 65001 >nul
echo === 1/5 Espacio libre antes ===
powershell -NoProfile -Command "'Libre antes: {0:N1} GB' -f ((Get-PSDrive C).Free/1GB)"
echo === 2/5 Temporales y cachés seguros ===
net stop wuauserv >nul 2>&1
powershell -NoProfile -Command "$l=$env:TEMP,'C:\Windows\Temp','C:\Windows\SoftwareDistribution\Download','C:\Windows\Minidump',($env:LOCALAPPDATA+'\CrashDumps'),($env:LOCALAPPDATA+'\Microsoft\Windows\INetCache'),($env:LOCALAPPDATA+'\Google\Chrome\User Data\Default\Cache'),($env:LOCALAPPDATA+'\Google\Chrome\User Data\Default\Code Cache'),($env:LOCALAPPDATA+'\Microsoft\Edge\User Data\Default\Cache'),($env:LOCALAPPDATA+'\Microsoft\Edge\User Data\Default\Code Cache'),($env:LOCALAPPDATA+'\D3DSCache'),($env:LOCALAPPDATA+'\NVIDIA\DXCache'); foreach($p in $l){ if(Test-Path $p){ Get-ChildItem $p -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue; 'Limpio: '+$p } }"
net start wuauserv >nul 2>&1
echo === 3/5 Papelera, cachés de desarrollo y componentes de Windows ===
powershell -NoProfile -Command "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"
where npm >nul 2>&1 && npm cache clean --force
where pip >nul 2>&1 && pip cache purge
dism /online /Cleanup-Image /StartComponentCleanup /Quiet
echo === 4/5 Espacio libre despues ===
powershell -NoProfile -Command "'Libre despues: {0:N1} GB' -f ((Get-PSDrive C).Free/1GB)"
echo === 5/5 Analisis con IA local (solo recomienda) ===
where ollama >nul 2>&1 || echo Ollama no esta instalado. Para activar la IA: winget install Ollama.Ollama ^& ollama pull qwen3:8b
powershell -NoProfile -Command "if(Get-Command ollama -ErrorAction SilentlyContinue){ try{ $t=Get-ChildItem $env:USERPROFILE -Directory -Force -ErrorAction SilentlyContinue | ForEach-Object { [pscustomobject]@{Carpeta=$_.FullName;GB=[math]::Round((Get-ChildItem $_.FullName -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum/1GB,2)} } | Sort-Object GB -Descending | Select-Object -First 12 | Out-String; $t; $b=@{model='qwen3:8b';stream=$false;prompt=('Eres experto en Windows. Estas son mis carpetas mas grandes. Responde en español, breve: que suele ser seguro borrar o mover a otro disco y que NO debo tocar.'+$t)} | ConvertTo-Json; $r=Invoke-RestMethod http://localhost:11434/api/generate -Method Post -Body $b -ContentType 'application/json' -TimeoutSec 900; $r.response -replace '(?s)<think>.*?</think>','' }catch{ 'IA no disponible: '+$_.Exception.Message } }"
echo Listo. Revise las recomendaciones y borre usted lo que apruebe.
