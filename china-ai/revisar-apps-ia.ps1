# SOLO LECTURA: lista apps por tamano y pide a Ollama un informe. No desinstala nada.
$e='SilentlyContinue'
$k='HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*','HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*','HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*'
'Leyendo programas instalados (puede tardar si hay que medir carpetas)...'
$a=Get-ItemProperty $k -ErrorAction $e | Where-Object { $_.DisplayName -and -not $_.SystemComponent -and -not $_.ParentKeyName } | Sort-Object DisplayName -Unique | ForEach-Object {
  $mb=[math]::Round([double]$_.EstimatedSize/1024)
  if($mb -eq 0 -and $_.InstallLocation -and (Test-Path $_.InstallLocation)){ $mb=[math]::Round((Get-ChildItem $_.InstallLocation -Recurse -File -Force -ErrorAction $e | Measure-Object Length -Sum).Sum/1MB) }
  [pscustomobject]@{Nombre=$_.DisplayName;MB=$mb;Editor=$_.Publisher;Instalado=$_.InstallDate}
} | Sort-Object MB -Descending
$a | Select-Object -First 40 | Format-Table -AutoSize
$store=Get-AppxPackage -ErrorAction $e | Where-Object { -not $_.IsFramework -and $_.SignatureKind -ne 'System' } | Select-Object -ExpandProperty Name | Sort-Object -Unique
'Apps de la Tienda: '+@($store).Count
$mod=$null
try{ $mod=(Invoke-RestMethod http://localhost:11434/api/tags -TimeoutSec 3 -ErrorAction Stop).models[0].name }catch{}
if(-not $mod){ 'Ollama no responde. Abrelo (o ejecuta: ollama serve) y vuelve a correr este script.'; return }
'Consultando IA ('+$mod+'), puede tardar varios minutos...'
$lst=(@($a) | Select-Object -First 70 | ForEach-Object { $_.Nombre+' ['+$_.MB+' MB]' }) -join '; '
$p='Eres experto en Windows. Responde en español. Con esta lista de programas (tamaño en MB) y apps de la Tienda, haz un informe con 3 secciones: 1) PROBABLEMENTE INNECESARIOS (bloatware, barras de herramientas, utilidades del fabricante, duplicados, juegos preinstalados), 2) REVISAR (depende del uso), 3) NO TOCAR (sistema, drivers, seguridad). Una linea por programa con motivo corto. Programas: '+$lst+'. Apps Tienda: '+(($store|Select-Object -First 60) -join ', ')
try{
  $b=@{model=$mod;stream=$false;prompt=$p}|ConvertTo-Json
  $r=(Invoke-RestMethod http://localhost:11434/api/generate -Method Post -Body $b -ContentType 'application/json' -TimeoutSec 1800 -ErrorAction Stop).response -replace '(?s)<think>.*?</think>',''
  $r; $r | Out-File "$env:USERPROFILE\Desktop\informe-apps-ia.txt" -Encoding utf8
  'Informe guardado en el Escritorio: informe-apps-ia.txt'
}catch{ 'IA no disponible: '+$_.Exception.Message }
'Nada fue desinstalado. Para quitar algo: .\desinstalar-programas.ps1'
