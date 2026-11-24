# Clínica Pro — Gestión clínica

Sistema web móvil para clínicas y consultas médicas de **cualquier especialidad**: login con roles, agenda con detección de choques (profesional, paciente, sala), ficha de paciente con historial, atenciones con adjuntos (foto/PDF de exámenes), recordatorios de citas para WhatsApp (se copian y se envían a mano), caja con informe diario/mensual, documentos internos de la clínica y exportación a CSV compatible con Excel. No incluye contenido clínico precargado ni servicios de IA: ningún dato sale del servidor.

## Abrir sin complicaciones

### Primera instalación
1. Instalar Python 3.11 o superior desde <https://www.python.org/downloads/>.
2. Descomprimir esta carpeta en el computador de recepción.
3. Ejecutar `install_clinica_pro.ps1` con PowerShell.
4. Ejecutar `run_clinica_pro.bat`. Se abre `http://127.0.0.1:8000`.

Siguientes veces: doble clic en `run_clinica_pro.bat`.
Demostración con datos de ejemplo: `demo_clinica_pro.bat` (no borra datos existentes).
Copia de la base y adjuntos: `backup_clinica_pro.bat`.

## Uso en celulares
Computador y celulares en la misma red Wi-Fi. Buscar la IP con `ipconfig` y abrir `http://IP-DEL-COMPUTADOR:8000`; en el navegador elegir **Agregar a pantalla de inicio**.

## Flujo
1. **Ingreso**: usuario y clave. Roles: *administrador* (usuarios, documentos) y *profesional*. En el primer arranque se crea `admin` con la clave de `CLINICAPRO_ADMIN_PASSWORD` (o una generada en `data/admin_inicial.txt`).
2. **Pacientes**: nombre, RUT (normalizado, no se repite), teléfono, alergias. Al tocar un paciente se abre su **ficha con historial** (citas, atenciones, pagos).
3. **Agenda**: el sistema rechaza choques de profesional, paciente o sala. Estados: En espera, Realizada, Cancelada, No asistió.
4. **Atención**: diagnóstico, tratamiento y adjunto (JPG/PNG/WEBP/PDF, máx. 8 MB); la cita pasa a *Realizada*.
5. **Recordatorios**: lista de citas de mañana (o de otra fecha) con el mensaje listo; botón *Copiar mensaje* y enlace a WhatsApp. **Nada se envía automáticamente.**
6. **Caja**: pagos por medio (efectivo, tarjeta, transferencia, seguro) y **informe de caja diario y mensual**.
7. **Documentos**: módulo opcional donde el administrador sube/edita notas internas (protocolos, consentimientos, tarifas). Viene vacío. No guarde datos de pacientes ahí.
8. Exportar citas y pagos en CSV (separador `;`, UTF-8 con BOM).

## Configuración (variables de entorno)
`CLINICAPRO_NOMBRE`, `CLINICAPRO_ADMIN_USER`, `CLINICAPRO_ADMIN_PASSWORD`, `CLINICAPRO_SECRET` (firma de sesiones), `CLINICAPRO_COOKIE_SECURE=1` (con HTTPS), `CLINICAPRO_DATA_DIR`. Ver `.env.example`. Publicación en Render: `DEPLOY.md`.

## API
Documentación en `/docs` (requiere sesión). Todo `/api` exige sesión salvo `/api/auth/login`, `/api/health` y `/api/meta` (solo el nombre de la clínica). Rutas: `/api/patients` (+`/{id}/history`), `/api/professionals`, `/api/appointments`, `/api/agenda`, `/api/reminders`, `/api/consultations`, `/api/payments`, `/api/reports/cash`, `/api/documents`, `/api/dashboard`, `/api/users`.

## Datos y respaldos
- Base: `data/clinica.db` · Adjuntos: `data/uploads`.
- Para respaldar: `backup_clinica_pro.bat` o copiar la carpeta `data`. No publicar el puerto en Internet.

## Seguridad
Contraseñas con scrypt, sesión en cookie firmada (HttpOnly, SameSite=Strict, Secure con HTTPS), bloqueo tras 5 intentos fallidos, sin secretos en el repositorio y sin llamadas a servicios externos con datos de pacientes. Pendiente para operar con datos reales en Internet: auditoría de accesos, copias automáticas cifradas, base PostgreSQL administrada y cumplimiento de las leyes 19.628 y 20.584. Ver `GUIA_VENTA.md`.

## Validación técnica
```
python -m pytest -q
```
Cubre RUT, choques de agenda, adjuntos, pagos, dashboard, exportación, login y roles, documentos, recordatorios, ficha de paciente e informe de caja.
