# KinePro — Gestión y biblioteca para kinesiólogos

App web móvil (español, Chile) para consultas de kinesiología: pacientes, agenda por **plan de tratamiento** (ej. “10 sesiones”), atenciones con **EVA y rangos medidos por sesión** con gráfico de evolución, **hojas de ejercicios para el hogar** imprimibles/PDF armadas desde la biblioteca, caja, login con roles (admin/profesional) y una **biblioteca de kinesiología de 115 entradas** con asistente opcional “Preguntar con IA”.

> ⚠ **Aviso:** el contenido clínico de la biblioteca fue redactado con apoyo de IA y **no está validado por un kinesiólogo**. El aviso es visible en la app y en las hojas para el profesional. `revision_gpt/` contiene el paquete para revisarlo; las correcciones se incorporan editando `app/library_data.txt` (no se inventan citas ni cifras).

## Novedades kinesiológicas
- **Planes**: pestaña Pacientes → ficha → *Nuevo plan* (motivo de consulta, diagnóstico kinésico, N sesiones). Progreso “4 de 10”; *Agendar sesiones* crea la serie (cada N días) omitiendo choques; el plan se cierra solo al completar las sesiones.
- **Atención**: desde la agenda (*Registrar atención*) o la pestaña Atención: plan, EVA 0–10 (toque), mediciones (movimiento, valor, ° o cm), enlaces a entradas de la biblioteca, adjunto.
- **Evolución**: ficha → plan → *Evolución*: gráficos de EVA y de cada medición por sesión.
- **Ejercicios para el hogar**: Biblioteca → *Ejercicios para el hogar*: plantillas con ejercicios de la biblioteca y dosis que define el profesional; *Imprimir / PDF* (con nombre del paciente) abre una hoja lista para imprimir o “Guardar como PDF”.

## Abrir sin complicaciones

### Primera instalación
1. Instalar Python 3.11 o superior desde <https://www.python.org/downloads/>.
2. Descomprimir esta carpeta en el computador de recepción.
3. Ejecutar `install_kinepro.ps1` con PowerShell.
4. Ejecutar `run_kinepro.bat`. Se abre `http://127.0.0.1:8000`.

Siguientes veces: doble clic en `run_kinepro.bat`.
Demostración con datos de ejemplo: `demo_kinepro.bat` (no borra datos existentes).
Copia de la base y adjuntos: `backup_kinepro.bat`.

## Uso en celulares
Computador y celulares en la misma red Wi-Fi. Buscar la IP con `ipconfig` y abrir `http://IP-DEL-COMPUTADOR:8000`; en el navegador elegir **Agregar a pantalla de inicio**.

## Flujo
1. **Pacientes**: registrar nombre, RUT (se normaliza y no se repite), teléfono, alergias.
2. **Agenda**: agendar cita; el sistema rechaza choques de horario del profesional, del paciente o de la sala. Cambiar estado: En espera, Realizada, Cancelada, No asistió (una cita cancelada libera el horario).
3. **Atención**: registrar diagnóstico, tratamiento y adjuntar examen (JPG/PNG/WEBP/PDF, máx. 8 MB). La cita asociada pasa a *Realizada*.
4. **Caja**: registrar pagos (efectivo, tarjeta, transferencia, seguro). El panel muestra ingresos del mes.
5. Descargar citas y pagos en CSV (separador `;`, UTF-8 con BOM, abre directo en Excel).

## API
Documentación interactiva en `/docs`: `/api/patients`, `/api/professionals`, `/api/appointments`, `/api/agenda`, `/api/consultations`, `/api/payments`, `/api/dashboard`, `/api/plans`, `/api/templates`, `/api/library`.

## Datos y respaldos
- Base: `data/kinepro.db` · Adjuntos: `data/uploads`.
- Para respaldar: `backup_kinepro.bat` o copiar la carpeta `data`. No publicar el puerto en Internet.

## Entrega comercial
Versión lista para demostración y piloto local. Ya incluye login con roles. Antes de operar con datos clínicos reales en Internet hay que agregar: HTTPS (lo da Render), auditoría de accesos a fichas, copias automáticas cifradas, política de retención y cumplimiento de la Ley 19.628/20.584 (datos sensibles de salud) y una base PostgreSQL administrada. Ver `GUIA_VENTA.md`.

## Validación técnica
```powershell
py -3 -m pytest -q
```
Pruebas (41): RUT, choques de agenda, planes y series de sesiones, EVA/mediciones/evolución, plantillas e impresión, enlaces a biblioteca, autenticación, adjuntos, pagos, dashboard, exportación y protección de borrado con historial.
