# Paquete KinePro (kinesiología) para ChatGPT

KinePro es la versión del sistema orientada a kinesiología: agenda y fichas, planes de sesiones, registro de dolor (EVA) y mediciones con gráficos, plantillas de ejercicios para el hogar, caja, usuarios con roles y una biblioteca de kinesiología de 115 entradas.

## Qué contiene esta carpeta
- `KinePro_codigo_completo.txt` — todo el código fuente en un solo archivo, con la ruta de cada archivo como encabezado.
- `KinePro_biblioteca_contenido.txt` — el contenido clínico de la biblioteca (para revisarlo o ampliarlo).
- `KinePro_proyecto.zip` — el proyecto completo tal como está en el repositorio (incluye pruebas, scripts de Windows e instrucciones de despliegue).

## Cómo usarlo
1. Abra una conversación **nueva** en ChatGPT (use un modelo con razonamiento si lo tiene).
2. Suba los archivos `.txt` (y el `.zip` si su plan permite descomprimir). Si su plan no deja subir archivos tan grandes, suba `KinePro_codigo_completo.txt` por partes.
3. Pegue el **prompt inicial** de abajo.
4. Pídale tareas de a una (ideas más abajo).
5. Copie los archivos que devuelva a la carpeta del proyecto, corra las pruebas y, si todo pasa, entregue los cambios (o súbalos al repositorio).

## Prompt inicial (copiar y pegar)
```
Eres un ingeniero de software senior y revisor de seguridad. Trabajaremos en KinePro, una app web en español para kinesiólogos en Chile (agenda, fichas, planes de sesiones, EVA y mediciones, ejercicios para el hogar, caja, biblioteca de kinesiología y asistente de IA opcional con OpenAI). Pila técnica: Python 3.11+, FastAPI, SQLite (sqlite3 sin ORM), un front de HTML/CSS/JS sin framework, PWA instalable, pruebas con pytest. Idioma de la interfaz: español de Chile.
Te adjunto: (1) el código completo, (2) el contenido de la biblioteca clínica.
Antes de cambiar nada: lee todo, resume en 10 líneas cómo está organizado (módulos, tablas, endpoints, flujo de autenticación) y dime qué riesgos de seguridad y de datos ves. Luego espera mi instrucción.
Reglas: no inventes funciones que no estén en el código; si algo no está claro, pregunta; devuelve siempre archivos completos con su ruta; mantén las pruebas existentes verdes y agrega pruebas para lo nuevo; ningún dato de pacientes debe salir a servicios externos; no pongas secretos en el código.
```

## Tareas sugeridas
- **Seguridad:** "Haz una auditoría de seguridad de `app/auth.py` y `app/main.py` (sesiones, roles, subida de archivos, inyección SQL, CSV, cabeceras). Lista hallazgos por gravedad con el archivo y la línea, y propón el arreglo."
- **Contenido clínico:** "Revisa `KinePro_biblioteca_contenido.txt` entrada por entrada. Etiqueta cada una como OK, CORREGIR, ACTUALIZAR, FALTA o DUDA; cita la frase exacta y no inventes referencias." (La carpeta `revision_gpt/` del proyecto trae un prompt detallado para esto.)
- **Mejoras de producto:** "Propón 5 mejoras de alto impacto para un kinesiólogo en consulta, ordenadas por esfuerzo, y desarrolla la primera con pruebas."
- **Datos permanentes:** "Prepara la migración de SQLite a PostgreSQL manteniendo las pruebas verdes."
- **Accesibilidad y diseño:** "Revisa `app/static/` contra WCAG 2.2 AA y mejora contraste, foco y tamaño táctil."


## Reglas para trabajar con ChatGPT (importante)
- **Nunca** pegue en ChatGPT claves, contraseñas, el archivo `.env`, bases de datos ni datos reales de pacientes. Estos paquetes no los contienen: no los agregue.
- ChatGPT puede inventar APIs, cifras o referencias. Pídale que **cite el archivo y la línea** de lo que cambie, y revise cada cambio antes de aplicarlo.
- Pídale siempre que devuelva **archivos completos con su ruta** (`app/main.py`, etc.), no fragmentos sueltos: así el cambio se puede copiar sin errores.
- Después de aplicar cambios, ejecute las pruebas: `python -m pytest -q` dentro de la carpeta del proyecto. Si fallan, devuelva el error a ChatGPT.
- El contenido clínico fue redactado por IA y **no está validado por un profesional de la salud**: no lo use con pacientes reales sin esa revisión.

## Nota sobre el asistente "Preguntar con IA"
Está en el código pero solo funciona con una clave de OpenAI configurada en el servidor (`OPENAI_API_KEY`). Esa clave no va en este paquete.
