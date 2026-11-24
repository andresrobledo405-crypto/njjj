# Publicar Clínica Pro en Render

Servicio web **clinicapro** (plan gratuito, Python), independiente de cualquier otro servicio.

| Campo | Valor |
|---|---|
| Repo / rama | `https://github.com/andresrobledo405-crypto/njjj` · rama `claude/clinicapro-general` |
| Build | `cd ClinicaPro && pip install -r requirements.txt` |
| Start | `cd ClinicaPro && uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips='*'` |
| Variables | `CLINICAPRO_NOMBRE=Clínica Pro`, `CLINICAPRO_ADMIN_USER=admin`, `CLINICAPRO_ADMIN_PASSWORD=<aleatoria>`, `CLINICAPRO_SECRET=<aleatoria>`, `CLINICAPRO_COOKIE_SECURE=1`, `TZ=America/Santiago` (horas y caja en hora de Chile) |

Genere las claves con `python -c "import secrets;print(secrets.token_urlsafe(18))"`. **No las suba al repositorio.**

## Persistencia de datos
El plan gratuito tiene disco efímero: la base SQLite (`data/`) **se pierde en cada reinicio o redeploy**. Úselo solo para demostración. Para datos reales:
1. **Disco persistente** (de pago): monte un disco en `/var/data` y fije `CLINICAPRO_DATA_DIR=/var/data`.
2. **PostgreSQL**: requiere adaptar la capa de datos (hoy es SQLite).

Cambiar la clave del administrador tras el primer ingreso (Admin → Mi clave). La variable `CLINICAPRO_ADMIN_PASSWORD` solo se usa mientras no existan usuarios.
