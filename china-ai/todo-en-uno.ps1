# TODO EN UNO: instala Ollama+modelo, limpia, y desinstala programas con consejo de IA (tu confirmas).
Write-Host '=== PASO 1-2: Ollama, limpieza y analisis de carpetas ===' -ForegroundColor Cyan
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
Write-Host ''; Read-Host 'Enter para continuar con el PASO 3 (desinstalar programas, tu eliges)' | Out-Null
Write-Host '=== PASO 3: desinstalar programas ===' -ForegroundColor Cyan
$e='SilentlyContinue'
$f0=(Get-PSDrive C).Free
$k='HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*','HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*','HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*'
$skip='Microsoft Visual C\+\+|\.NET|Windows|WebView2|NVIDIA|Intel|AMD|Realtek|Driver|Update for|Security Update|Hotfix|Ollama|Microsoft Edge$'
$a=Get-ItemProperty $k -ErrorAction $e | Where-Object { $_.DisplayName -and -not $_.SystemComponent -and -not $_.ParentKeyName -and $_.DisplayName -notmatch $skip -and ($_.UninstallString -or $_.QuietUninstallString) } | Sort-Object DisplayName -Unique | ForEach-Object { [pscustomobject]@{Nombre=$_.DisplayName;MB=[math]::Round([double]$_.EstimatedSize/1024);Editor=$_.Publisher;Instalado=$_.InstallDate;Ref=$_} } | Sort-Object MB -Descending
'Programas encontrados: '+@($a).Count
$mod=$null
try{ $mod=(Invoke-RestMethod http://localhost:11434/api/tags -TimeoutSec 3 -ErrorAction Stop).models[0].name }catch{}
if($mod){
'Consultando IA ('+$mod+')... solo aconseja, no desinstala.'
$lst=(@($a) | Select-Object -First 80 | ForEach-Object { $_.Nombre+' ('+$_.MB+' MB)' }) -join '; '
try{ $b=@{model=$mod;stream=$false;prompt=('Lista de programas instalados en Windows. En español y breve, indica cuales suelen ser innecesarios o bloatware (barras de herramientas, juegos preinstalados, utilidades del fabricante, duplicados) y cuales NO conviene desinstalar. Programas: '+$lst)} | ConvertTo-Json; (Invoke-RestMethod http://localhost:11434/api/generate -Method Post -Body $b -ContentType 'application/json' -TimeoutSec 900 -ErrorAction Stop).response -replace '(?s)<think>.*?</think>','' }catch{ 'IA no disponible.' }
}else{ 'Ollama no esta activo: se omite el consejo de la IA.' }
'>>> Se abrira una ventana: marca con Ctrl+clic los programas a DESINSTALAR y pulsa OK. Cancelar = no se toca nada.'
$sel=@($a) | Select-Object Nombre,MB,Editor,Instalado | Out-GridView -PassThru -Title 'Marca los programas a desinstalar (Ctrl+clic) y pulsa OK'
if(-not $sel){ 'No seleccionaste nada. Fin.'; return }
$todo=@($a) | Where-Object { $sel.Nombre -contains $_.Nombre }
'Se desinstalaran:'
$todo | ForEach-Object { ' - '+$_.Nombre+' ('+$_.MB+' MB)' }
if((Read-Host 'Escribe SI para continuar') -ne 'SI'){ 'Cancelado.'; return }
foreach($p in $todo){
'Desinstalando: '+$p.Nombre
$r=$p.Ref
$u=$r.QuietUninstallString
if(-not $u){ $u=$r.UninstallString; if($u -match '(?i)msiexec'){ $u=($u -replace '(?i)/I','/X')+' /qn /norestart' } }
Start-Process cmd -ArgumentList '/c',('"'+$u+'"') -Wait -NoNewWindow
}
$f1=(Get-PSDrive C).Free
'Libre antes: {0:N1} GB | despues: {1:N1} GB' -f ($f0/1GB),($f1/1GB)
'LISTO. Algunos desinstaladores terminan en segundo plano o piden reinicio.'
