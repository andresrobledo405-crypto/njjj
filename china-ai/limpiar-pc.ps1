$e='SilentlyContinue'
$f0=(Get-PSDrive C).Free
'Libre antes: {0:N1} GB' -f ($f0/1GB)
$ol=$env:LOCALAPPDATA+'\Programs\Ollama'
if(-not(Get-Command ollama -ErrorAction $e)){
'Instalando Ollama...'
winget install -e --id Ollama.Ollama --accept-package-agreements --accept-source-agreements --silent
$env:Path+=';'+$ol+';'+[Environment]::GetEnvironmentVariable('Path','Machine')+';'+[Environment]::GetEnvironmentVariable('Path','User')
}
$ok=$false
for($i=0;$i -lt 20 -and -not $ok;$i++){ try{ Invoke-RestMethod http://localhost:11434/api/tags -TimeoutSec 2 -ErrorAction Stop | Out-Null; $ok=$true }catch{ if($i -eq 2){ Start-Process ollama -ArgumentList 'serve' -WindowStyle Hidden -ErrorAction $e }; Start-Sleep 2 } }
$ram=(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory/1GB
$m=if($ram -ge 12){'qwen3:8b'}else{'qwen3:4b'}
if($ok){ 'Descargando modelo '+$m+' (puede tardar)...'; ollama pull $m }else{ 'Ollama no arranco; se omite la IA.' }
Stop-Service wuauserv -ErrorAction $e
$l=$env:TEMP,'C:\Windows\Temp','C:\Windows\SoftwareDistribution\Download','C:\Windows\Minidump',($env:LOCALAPPDATA+'\CrashDumps'),($env:LOCALAPPDATA+'\Microsoft\Windows\INetCache'),($env:LOCALAPPDATA+'\Google\Chrome\User Data\Default\Cache'),($env:LOCALAPPDATA+'\Google\Chrome\User Data\Default\Code Cache'),($env:LOCALAPPDATA+'\Microsoft\Edge\User Data\Default\Cache'),($env:LOCALAPPDATA+'\Microsoft\Edge\User Data\Default\Code Cache'),($env:LOCALAPPDATA+'\D3DSCache'),($env:LOCALAPPDATA+'\NVIDIA\DXCache')
foreach($p in $l){ if(Test-Path $p){ Get-ChildItem $p -Force -ErrorAction $e | Remove-Item -Recurse -Force -ErrorAction $e; 'Limpio: '+$p } }
Start-Service wuauserv -ErrorAction $e
Clear-RecycleBin -Force -ErrorAction $e
if(Get-Command npm -ErrorAction $e){ npm cache clean --force }
if(Get-Command pip -ErrorAction $e){ pip cache purge }
'Limpiando componentes de Windows (DISM)...'
dism /online /Cleanup-Image /StartComponentCleanup /Quiet
$f1=(Get-PSDrive C).Free
'Libre despues: {0:N1} GB (balance: {1:N1} GB, incluye la descarga del modelo)' -f ($f1/1GB),(($f1-$f0)/1GB)
if($ok){ try{
$t=Get-ChildItem $env:USERPROFILE -Directory -Force -ErrorAction $e | ForEach-Object { [pscustomobject]@{Carpeta=$_.FullName;GB=[math]::Round((Get-ChildItem $_.FullName -Recurse -File -Force -ErrorAction $e | Measure-Object Length -Sum).Sum/1GB,2)} } | Sort-Object GB -Descending | Select-Object -First 12 | Out-String
$t
'--- Recomendacion de la IA (solo aconseja, no borra) ---'
$b=@{model=$m;stream=$false;prompt=('Eres experto en Windows. Estas son mis carpetas mas grandes. Responde en español, breve: que suele ser seguro borrar o mover a otro disco y que NO debo tocar.'+$t)} | ConvertTo-Json
$r=Invoke-RestMethod http://localhost:11434/api/generate -Method Post -Body $b -ContentType 'application/json' -TimeoutSec 1200 -ErrorAction Stop
$r.response -replace '(?s)<think>.*?</think>',''
}catch{ 'IA no disponible: '+$_.Exception.Message } }
'LISTO.'
