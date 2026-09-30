# njjj — IA en su teléfono

Cuatro formas de integrar IA, en un solo proyecto:

| # | Opción | Dónde |
|---|--------|-------|
| 1 | App móvil con Claude (chat + fotos) | `mobile/` + `server/` |
| 2 | IA local sin internet (llama.cpp) | `mobile/local.js` |
| 3 | Asistentes ya hechos | `docs/ASISTENTES.md` |
| 4 | Asistente por SMS y llamadas (Twilio) | `server/index.js` (`/sms`, `/voice`) |

## 1. Servidor
```bash
cd server
cp .env.example .env    # ponga su ANTHROPIC_API_KEY y una APP_KEY
npm install
npm start
```
Endpoints: `GET /health`, `POST /chat`, `POST /chat/stream` (header `x-app-key`), `POST /sms`, `POST /voice`.
La clave de Anthropic vive solo en el servidor, nunca en la app.

## 2. App móvil
```bash
cd mobile
# edite config.js: SERVER_URL (IP de su PC o dominio HTTPS) y APP_KEY
npm install
npx expo start          # chat en la nube: vale con Expo Go
```
El **modo local** (interruptor "Local") usa `llama.rn`, que necesita código nativo:
`npx expo prebuild && npx expo run:android` (o `run:ios`). La primera vez descarga un modelo de ~1.5 GB.

## 3. SMS y llamadas con Twilio
1. Exponga el servidor con HTTPS (Render, Fly.io, o `ngrok http 3000` para pruebas).
2. En Twilio, en su número: *Messaging → A message comes in* → `https://SU_URL/sms` (POST); *Voice → A call comes in* → `https://SU_URL/voice` (POST).
3. Envíe un SMS o llame a ese número.

## 4. Asistentes existentes
Ver [docs/ASISTENTES.md](docs/ASISTENTES.md).

## Notas
- El historial de SMS/llamadas está en memoria; use una base de datos en producción.
- Los webhooks de Twilio validan la firma si define `TWILIO_AUTH_TOKEN` y `PUBLIC_URL` en `.env`.
- Gasto: cada mensaje consume créditos de la API de Anthropic y de Twilio.
