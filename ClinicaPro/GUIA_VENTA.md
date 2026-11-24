# Guía de venta — Clínica Pro

**Cliente ideal:** consultas médicas de cualquier especialidad, centros dentales y policlínicos pequeños que hoy usan papel o Excel.

**Dolor que resuelve:** dobles reservas, fichas perdidas, alergias no vistas, cierre de caja manual.

## Demostración (10 min)
1. Ejecutar `demo_clinica_pro.bat`.
2. Mostrar la agenda del día y el aviso de alergias en la cita.
3. Intentar agendar un choque de horario → el sistema lo rechaza.
4. Registrar una atención con foto de un examen desde el celular.
5. Abrir la ficha de un paciente (historial) y la pestaña Recordatorios: copiar el mensaje de WhatsApp de las citas de mañana.
6. Registrar un pago, mostrar el informe de caja diario/mensual y descargar Excel.

## Propuesta
- **Piloto local:** instalación en 1 computador + celulares por Wi-Fi, capacitación de 1 hora.
- **Mensual:** soporte, respaldos y actualizaciones. *(Definir precios según el cliente; no se fijan aquí.)*
- **Ya incluido:** usuarios y roles, recordatorios para WhatsApp (copiar y enviar), ficha con historial, informe de caja, documentos internos.
- **Fase 2 (servicio en Internet):** auditoría de accesos, respaldos cifrados, PostgreSQL administrada, envío automático de recordatorios (opcional).

## Objeciones frecuentes
- *¿Y la privacidad?* Datos en el computador o servidor de la clínica; no se envían a servicios externos ni a IA. En fase 2, cifrado y auditoría.
- *¿Se puede migrar mi Excel?* Sí, vía API/CSV en el onboarding.
