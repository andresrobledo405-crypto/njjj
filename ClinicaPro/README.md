# Clínica Pro — Gestión clínica

Sistema web móvil para clínicas y consultas médicas: agenda con detección de choques (profesional, paciente, sala), fichas de pacientes con alergias visibles, atenciones con adjuntos (foto/PDF de exámenes), caja con medios de pago y exportación a CSV compatible con Excel.

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
1. **Pacientes**: registrar nombre, RUT (se normaliza y no se repite), teléfono, alergias.
2. **Agenda**: agendar cita; el sistema rechaza choques de horario del profesional, del paciente o de la sala. Cambiar estado: En espera, Realizada, Cancelada, No asistió (una cita cancelada libera el horario).
3. **Atención**: registrar diagnóstico, tratamiento y adjuntar examen (JPG/PNG/WEBP/PDF, máx. 8 MB). La cita asociada pasa a *Realizada*.
4. **Caja**: registrar pagos (efectivo, tarjeta, transferencia, seguro). El panel muestra ingresos del mes.
5. Descargar citas y pagos en CSV (separador `;`, UTF-8 con BOM, abre directo en Excel).

## API
Documentación interactiva en `/docs`: `/api/patients`, `/api/professionals`, `/api/appointments`, `/api/agenda`, `/api/consultations`, `/api/payments`, `/api/dashboard`.

## Datos y respaldos
- Base: `data/clinica.db` · Adjuntos: `data/uploads`.
- Para respaldar: `backup_clinica_pro.bat` o copiar la carpeta `data`. No publicar el puerto en Internet.

## Entrega comercial
Versión lista para demostración y piloto local. Antes de operar con datos clínicos reales en Internet hay que agregar: autenticación por usuario y rol, HTTPS, auditoría de accesos a fichas, copias automáticas cifradas, política de retención y cumplimiento de la Ley 19.628/20.584 (datos sensibles de salud) y una base PostgreSQL administrada. Ver `GUIA_VENTA.md`.

## Validación técnica
```powershell
py -3 -m pytest -q
```
Pruebas: RUT, choques de agenda, adjuntos, pagos, dashboard, exportación y protección de borrado con historial.
