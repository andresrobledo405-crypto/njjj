# Publicar KinePro en Render

Servicio existente: `kinepro` (`srv-dc2oghjm8hqs73853iqg`, workspace `tea-cufbdbogph6c7382o0vg`), repo `andresrobledo405-crypto/njjj`, rama `claude/modest-volta-kgrtr2`.

## Configuración (ya aplicada)
La configuración vive en `render.yaml` (raíz del repo) y el servicio está adoptado por el Blueprint `exs-dc2vamm1egvs73futm6g` con auto-sync: Root Directory `KinePro`, Build `pip install -r requirements.txt`, Start `uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips='*'`, Health Check `/api/health`, rama `claude/modest-volta-kgrtr2`. Para cambiar algo, edite `render.yaml` y haga push.

## Variables de entorno
| Variable | Para qué |
|---|---|
| `KINEPRO_ADMIN_PASSWORD` | Clave del usuario `admin` (se crea al arrancar con la base vacía). **Cámbiela desde Admin → Mi clave.** |
| `KINEPRO_SECRET` | Firma de las cookies de sesión (aleatoria, larga). El Blueprint la genera solo si no existe; hoy ya está definida. |
| `KINEPRO_COOKIE_SECURE=1` | Cookie solo por HTTPS. |
| `TZ=America/Santiago` | Hora local para “hoy” y la fecha de cada atención (Render usa UTC). |
| `OPENAI_API_KEY` (opcional) | Activa “Preguntar con IA”; solo se envían la pregunta y entradas de la biblioteca, nunca datos de pacientes. |
| `KINEPRO_DATA_DIR` | Carpeta de datos (con disco persistente: la ruta del disco, p. ej. `/var/data`). |

Nunca se commitean claves: están solo en Render.

## ⚠ Persistencia de datos (importante)
El plan **gratuito** de Render tiene disco efímero: **la base SQLite y los adjuntos se pierden en cada reinicio/redeploy** (y el servicio se duerme tras 15 min sin uso). Sirve para demostración, **no para datos reales de pacientes**. Opciones (requieren aprobación del usuario porque tienen costo):
1. **Disco persistente** (plan de pago, p. ej. Starter + Disk): montar en `/var/data` y poner `KINEPRO_DATA_DIR=/var/data`. Es lo más simple.
2. **PostgreSQL administrado**: requiere migrar `app/db.py` (hoy SQLite) — trabajo adicional.
Mientras tanto: Admin → **Respaldo** descarga un .zip (base + adjuntos); hágalo con frecuencia. Además: respaldos periódicos y, para datos reales, cumplir Ley 19.628 / 20.584 (ver README).

## Verificación después de desplegar
`curl https://kinepro.onrender.com/api/health` → `{"status":"ok"}`; abrir la URL, ingresar como `admin`.
