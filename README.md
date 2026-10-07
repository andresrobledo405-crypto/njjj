# njjj — IA en su teléfono

Cuatro formas de integrar IA, en un solo proyecto:

| # | Opción | Dónde |
|---|--------|-------|
| 1 | App móvil con Claude (chat + fotos) | `mobile/` + `server/` |
| 2 | IA local sin internet (llama.cpp) | `mobile/local.js` |
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

## Notas
- El historial de SMS/llamadas está en memoria; use una base de datos en producción.
- Los webhooks de Twilio validan la firma si define `TWILIO_AUTH_TOKEN` y `PUBLIC_URL` en `.env`.
- Gasto: cada mensaje consume créditos de la API de Anthropic y de Twilio.

## Instalar en Android como app real (APK)
Con una cuenta gratuita de Expo (expo.dev), sin Android Studio:
```bash
cd mobile
npm install -g eas-cli
eas login
eas build -p android --profile apk    # ~15 min en la nube; al final da un enlace/QR para descargar el .apk
```
Abra el enlace en el teléfono e instale el APK (permita "instalar apps desconocidas").
`usesCleartextTraffic` está activado para poder usar `http://IP-de-su-PC:3000` en pruebas; en producción use HTTPS.
El modo local (llama.rn) funciona en esta versión porque el APK incluye código nativo.

## DealFinder AI
La pestaña **Ofertas** de la app busca y compara precios con la búsqueda web de Claude (`POST /deals` en el servidor).
Filtro por país y favoritos guardados en el teléfono. Requiere `ANTHROPIC_API_KEY` con la búsqueda web habilitada en su cuenta.
