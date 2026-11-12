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
