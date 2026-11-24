# Revisión de KinePro con ChatGPT

**Qué es:** `codigo_kinepro.txt` (≈194 KB) contiene todo el código de la app (backend FastAPI + SQLite, interfaz web, pruebas, configuración de despliegue). No incluye datos de pacientes, bases de datos, claves ni la biblioteca clínica (esa se revisa con `../revision_gpt/`).

**Cómo usarlo**
1. Abra ChatGPT (modelo con razonamiento y subida de archivos, de preferencia).
2. Adjunte `codigo_kinepro.txt`.
3. Pegue el prompt de abajo.
4. Traiga las respuestas a la sesión de desarrollo para que se apliquen y se prueben.

> No suba nada más: ni bases de datos, ni capturas con pacientes reales, ni claves.

## Prompt

```
Eres un revisor senior de software de salud (Chile) con experiencia en seguridad de aplicaciones web, privacidad de datos de salud y flujo clínico de kinesiología.

Adjunto el código completo de KinePro: app web móvil para kinesiólogos (agenda por plan de sesiones, fichas, EVA y rangos medidos por sesión con gráfico de evolución, plantillas de ejercicios para el hogar imprimibles, biblioteca clínica, caja, roles admin/profesional, registro de actividad, respaldo). Backend FastAPI + SQLite, front en HTML/JS sin frameworks. Se publica en Render (plan gratuito, disco efímero). El contenido clínico de la biblioteca fue redactado con IA y NO está validado por un kinesiólogo (es un aviso visible en la app).

Revisa el código y entrega, en español:

1. SEGURIDAD: vulnerabilidades reales (autenticación/sesión, autorización por rol, XSS, inyección, CSRF, subida de archivos, cabeceras, manejo de secretos, límites de tasa). Para cada hallazgo: archivo y función, escenario de ataque concreto y arreglo propuesto en código.
2. PRIVACIDAD Y CUMPLIMIENTO (Chile): brechas frente a la Ley 19.628 (y su actualización por la Ley 21.719 si aplica), la Ley 20.584 sobre derechos del paciente y ficha clínica, y buenas prácticas para datos sensibles de salud: consentimiento, retención, auditoría, cifrado, derechos de acceso/rectificación/eliminación, respaldos. Distingue lo que el software debe hacer de lo que es responsabilidad del profesional. Cita una norma solo si estás seguro de ella; si no, di "verificar con un abogado".
3. ERRORES Y CASOS BORDE: bugs lógicos, condiciones de carrera, estados inconsistentes (planes, citas, atenciones, pagos), zonas horarias, validaciones faltantes. Con ejemplo de entrada que lo rompe.
4. FUNCIONALIDAD QUE FALTA para un kinesiólogo independiente o un centro pequeño: lista priorizada (alto/medio/bajo) con justificación, sin inventar requisitos normativos. Considera ficha clínica, consentimiento informado, evaluación inicial/reevaluación, escalas validadas, certificados/informes, boletas/cobro, recordatorios, multi-sede, acceso del paciente.
5. UX/ACCESIBILIDAD móvil: problemas concretos de uso con una mano, lectores de pantalla, contraste, flujos largos.
6. PRUEBAS: qué casos importantes no están cubiertos.

Reglas: no inventes citas, cifras ni normas; marca lo incierto como "no verificado". Ordena cada sección por severidad. Termina con un top 10 de acciones, en orden, que un desarrollador pueda ejecutar esta semana.
```
