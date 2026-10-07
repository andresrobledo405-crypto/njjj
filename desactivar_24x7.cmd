@echo off
schtasks /Delete /TN "JARVIS-Inicio" /F
schtasks /Delete /TN "JARVIS-Vigilante" /F
echo Listo. JARVIS ya no arranca solo. Si esta abierto, ciérrelo con su ventana o diciendo "Jarvis, salir".
