# Paquete Clínica Pro (gestión clínica general) para ChatGPT

Clínica Pro es la versión general del sistema para clínicas y consultas médicas: pacientes, profesionales, agenda con detección de choques (profesional, paciente, sala), atenciones con adjuntos, caja, documentos y protocolos internos, usuarios con roles y recordatorios de citas para copiar a WhatsApp.

## Qué contiene esta carpeta
- `ClinicaPro_codigo_completo.txt` — todo el código fuente en un solo archivo, con la ruta de cada archivo como encabezado.
- `ClinicaPro_proyecto.zip` — el proyecto completo tal como está en el repositorio (incluye pruebas, scripts de Windows e instrucciones de despliegue).

## Cómo usarlo
1. Abra una conversación **nueva** en ChatGPT (use un modelo con razonamiento si lo tiene).
2. Suba los archivos `.txt` (y el `.zip` si su plan permite descomprimir). Si su plan no deja subir archivos tan grandes, suba `ClinicaPro_codigo_completo.txt` por partes.
3. Pegue el **prompt inicial** de abajo.
4. Pídale tareas de a una (ideas más abajo).
5. Copie los archivos que devuelva a la carpeta del proyecto, corra las pruebas y, si todo pasa, entregue los cambios (o súbalos al repositorio).

## Prompt inicial (copiar y pegar)
```
Eres un ingeniero de software senior y revisor de seguridad. Trabajaremos en Clínica Pro, una app web en español para gestión de clínicas y consultas médicas en general en Chile (pacientes, profesionales, agenda con detección de choques, atenciones con adjuntos, caja, documentos y protocolos internos, recordatorios por WhatsApp para copiar y pegar). Pila técnica: Python 3.11+, FastAPI, SQLite (sqlite3 sin ORM), un front de HTML/CSS/JS sin framework, PWA instalable, pruebas con pytest. Idioma de la interfaz: español de Chile.
Te adjunto el código completo.
Antes de cambiar nada: léelo todo, resume en 10 líneas cómo está organizado (módulos, tablas, endpoints, autenticación) y dime qué riesgos de seguridad y de datos ves. Luego espera mi instrucción.
Reglas: no inventes funciones que no estén en el código; si algo no está claro, pregunta; devuelve siempre archivos completos con su ruta; mantén las pruebas existentes verdes y agrega pruebas para lo nuevo; ningún dato de pacientes debe salir a servicios externos; no pongas secretos en el código.
```

## Tareas sugeridas
- **Seguridad:** "Haz una auditoría de seguridad de `app/auth.py` y `app/main.py` (sesiones, roles, subida de archivos, inyección SQL, CSV, cabeceras). Lista hallazgos por gravedad con el archivo y la línea, y propón el arreglo."
- **Mejoras de producto:** "Propón 5 mejoras de alto impacto para una clínica pequeña, ordenadas por esfuerzo, y desarrolla la primera con pruebas."
- **Datos permanentes:** "Prepara la migración de SQLite a PostgreSQL manteniendo las pruebas verdes."
- **Cumplimiento (Chile):** "Lista qué falta para tratar datos de salud conforme a las leyes 19.628 y 20.584 (consentimiento, auditoría de accesos, retención, respaldos) y propón cómo implementarlo."
- **Accesibilidad y diseño:** "Revisa `app/static/` contra WCAG 2.2 AA y mejora contraste, foco y tamaño táctil."


## Reglas para trabajar con ChatGPT (importante)
- **Nunca** pegue en ChatGPT claves, contraseñas, el archivo `.env`, bases de datos ni datos reales de pacientes. Estos paquetes no los contienen: no los agregue.
- ChatGPT puede inventar APIs, cifras o referencias. Pídale que **cite el archivo y la línea** de lo que cambie, y revise cada cambio antes de aplicarlo.
- Pídale siempre que devuelva **archivos completos con su ruta** (`app/main.py`, etc.), no fragmentos sueltos: así el cambio se puede copiar sin errores.
- Después de aplicar cambios, ejecute las pruebas: `python -m pytest -q` dentro de la carpeta del proyecto. Si fallan, devuelva el error a ChatGPT.
- El contenido clínico fue redactado por IA y **no está validado por un profesional de la salud**: no lo use con pacientes reales sin esa revisión.
