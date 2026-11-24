# Paquete para revisión externa (ChatGPT u otro)

**Qué enviar:** este prompt + `codigo_backend.txt` (backend FastAPI, ~38 KB) + `../app/static/index.html` (interfaz, ~93 KB; súbalo como archivo adjunto).
**Qué NO enviar jamás:** datos de pacientes, la carpeta `data/`, `.env`, claves o la base `clinica.db`. Este paquete contiene solo código.

---

## Prompt

Eres un revisor senior de software de salud (AppSec, backend Python y UX móvil). Revisa **Clínica Pro**, un sistema web para clínicas y consultas médicas en Chile: FastAPI + SQLite + una sola página HTML con JS (sin frameworks, sin CDN). Funciones: login con roles (admin/profesional), pacientes (RUT), profesionales, agenda con detección de choques, atenciones con adjuntos, caja, recordatorios de citas (solo copiar mensaje para WhatsApp, no se envía nada), documentos internos y exportación CSV. Se despliega en Render (plan gratuito, SQLite efímero).

Entrega, en este orden y en español:
1. **Vulnerabilidades** (OWASP Top 10, autenticación y sesión, autorización por rol, XSS, inyección SQL, CSRF, subida de archivos, fuga de datos, fuerza bruta). Para cada una: archivo y función, escenario de ataque concreto, severidad y corrección en código.
2. **Errores de lógica** (choques de agenda, zonas horarias de Chile, RUT, montos, estados de cita).
3. **Cumplimiento** Ley 19.628 y 20.584 (datos sensibles de salud): qué falta para operar con datos reales (auditoría de accesos, cifrado, respaldos, retención, consentimiento).
4. **Persistencia y escalado:** plan de migración de SQLite a PostgreSQL.
5. **UX/accesibilidad/rendimiento** de `index.html` (WCAG AA, táctil, animaciones, `prefers-reduced-motion`).
6. **Lo que falta** para un producto vendible a una clínica pequeña, priorizado (alto/medio/bajo).

Reglas: no inventes problemas; si algo es incierto, dilo. Cita el código exacto. Propón parches mínimos en diff. No pidas datos reales de pacientes.

---

## Ya cubierto (para no repetir)
scrypt para claves, sesión HttpOnly/SameSite=Strict/Secure, bloqueo tras 5 intentos fallidos, todo `/api` exige sesión, borrado solo admin, adjuntos validados por extensión y firma real (magic bytes), CSV neutraliza inyección de fórmulas, CSP/HSTS/no-store en cabeceras, escapado de todo texto dinámico, sin recursos externos, sin llamadas a servicios externos con datos de pacientes.
