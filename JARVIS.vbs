' Lanza JARVIS. Primera vez (sin clave o sin instalar): ventana visible. Despues: sin ninguna ventana.
Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
dir = fso.GetParentFolderName(WScript.ScriptFullName)
clave = sh.Environment("User")("GEMINI_API_KEY")
listo = fso.FileExists(dir & "\.jarvis_ok") And Len(clave) > 0
estilo = 1
If listo Then estilo = 0
sh.CurrentDirectory = dir
sh.Run "powershell -NoProfile -ExecutionPolicy Bypass -File """ & dir & "\run_jarvis.ps1""", estilo, False
