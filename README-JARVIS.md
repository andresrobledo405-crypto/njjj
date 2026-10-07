# J.A.R.V.I.S. OS

Asistente de voz de escritorio (Gemini + herramientas locales).

## Instalación automática (Windows, desde cmd)
```
curl -L -o instalar_jarvis.cmd https://raw.githubusercontent.com/andresrobledo405-crypto/njjj/claude/modest-fermat-p6jnyk/instalar_jarvis.cmd
instalar_jarvis.cmd claude/modest-fermat-p6jnyk
```
Descarga o actualiza JARVIS en `%USERPROFILE%\jarvis` y lo abre. Tras el merge, omita la rama (usa `main`).

## Uso manual (Windows)
1. Haga doble clic en `JARVIS.vbs` (o `JARVIS.bat`). Tras la primera vez abre sin ventana de consola; errores en `jarvis.log`.
   La primera vez La primera vez pide su clave de Google AI Studio y la guarda.
2. Instala dependencias y abre la interfaz.
3. Diga "Jarvis" y luego la orden.

## Herramientas
| Función | Qué hace |
|---|---|
| `recordar_dato` / `buscar_en_memoria` | Memoria persistente en SQLite |
| `diagnostico_sistema` | CPU, RAM, batería |
| `leer_portapapeles` / `escribir_portapapeles` | Portapapeles |
| `controlar_volumen` | subir, bajar, establecer (0-100), silenciar, activar_sonido, consultar |
| `controlar_dispositivo_tuya` | Domótica Tuya (`TUYA_DEVICE_ID`, `TUYA_IP_ADDRESS`, `TUYA_LOCAL_KEY`) |

Volumen: Windows usa `pycaw`; macOS `osascript`; Linux `pactl`.

## Convivencia con Manus
JARVIS y Manus (https://manus.im/desktop) pueden estar abiertos a la vez.
- **Delegar:** diga "Jarvis, pídele a Manus que investigue X". JARVIS copia la tarea al portapapeles y abre Manus; usted pega (Ctrl+V) y aprueba.
- **Micrófono:** JARVIS solo lo usa mientras escucha. Si Manus usa voz, no active ambos a la vez.
- **Carpetas:** en Manus > My Computer > Add Folder, **no autorice** la carpeta de JARVIS (`%USERPROFILE%\jarvis`): ahí quedan su memoria (`jarvis_system.db`) y `jarvis.log`.
- **Una sola copia:** JARVIS rechaza abrirse dos veces.

## Pruebas
`python3 -m unittest discover -s tests`  (simulan el audio; no necesitan hardware)
