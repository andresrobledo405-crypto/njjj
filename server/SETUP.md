# Gemini Backend Setup Guide

Este documento explica cómo configurar el backend de Gemini AI para Artesanos Panadería.

## Descripción General

El backend Gemini integra la API de Google Generative AI para:
- **Análisis de imágenes**: Extrae información visual, colores, calidad y SEO
- **Generación de contenido**: Crea captions, hashtags y estrategias de marketing
- **Prompts para Runway ML**: Genera descripciones optimizadas para video IA
- **Predicción de engagement**: Estimaciones de rendimiento en redes sociales

**Nota importante:** El frontend funciona sin problemas sin el backend Gemini. Todos los endpoints son opcionales.

---

## Requisitos

- Node.js 18+ (con npm)
- Cuenta de Google Cloud Project
- Conexión a internet

---

## Paso 1: Obtener API Key

### 1.1 Crear Google Cloud Project

1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Hacer clic en el nombre del proyecto (arriba a la izquierda)
3. Seleccionar **NEW PROJECT**
4. Nombre: `artesanos-gemini` (o el que prefieras)
5. Hacer clic en **CREATE**

### 1.2 Habilitar Generative AI API

1. En la consola, buscar "Generative AI API"
2. Hacer clic en el resultado
3. Hacer clic en **ENABLE** (Habilitar)

### 1.3 Crear API Key

1. En la consola, ir a **Credentials** (en el menú izquierdo)
2. Hacer clic en **CREATE CREDENTIALS** → **API Key**
3. Se abrirá un diálogo con tu API Key
4. **COPIAR la key** (necesitarás esto en el siguiente paso)

> ⚠️ **Seguridad:** Nunca compartir la API Key públicamente. Mantenerla en archivo `.env` que NO se comitea a Git.

---

## Paso 2: Configurar Variables de Entorno

### 2.1 Crear archivo `.env`

En la carpeta `server/`:

```bash
cp .env.example .env
```

### 2.2 Editar `.env`

Abrir `server/.env` y completar:

```env
# Gemini AI Configuration
GEMINI_API_KEY=tu_api_key_aqui_sin_comillas

# Server Configuration (opcional)
PORT=3000
NODE_ENV=development
```

**Ejemplo completado:**
```env
GEMINI_API_KEY=AIzaSyDxW3Z9k8L2m3N4o5P6q7R8s9T0u1V2w3X
PORT=3000
NODE_ENV=development
```

### 2.3 Verificar `.env` en `.gitignore`

El archivo `.env` debe estar en `.gitignore`:

```bash
cat .gitignore | grep ".env"
# Debe mostrar: .env
```

---

## Paso 3: Instalar Dependencias

En la carpeta `server/`:

```bash
npm install
```

Si falta `@google/generative-ai`, instalar explícitamente:

```bash
npm install @google/generative-ai
```

---

## Paso 4: Iniciar el Servidor

### Opción A: Desarrollo

```bash
cd server
npm start
```

Verás en la consola:
```
✅ Gemini AI initialized successfully
Server running on port 3000
```

### Opción B: Con Nodemon (hot reload)

```bash
npm install -D nodemon
npx nodemon server/index.js
```

### Opción C: Background (con `nohup`)

```bash
nohup npm start > server.log 2>&1 &
```

---

## Paso 5: Verificar Salud del Servicio

### Health Check Endpoint

```bash
curl http://localhost:3000/api/gemini/health
```

**Respuesta exitosa:**
```json
{
  "status": "online",
  "service": "Gemini AI",
  "models": ["gemini-pro", "gemini-pro-vision"],
  "timestamp": "2026-10-05T12:34:56.789Z"
}
```

**Si API Key no está configurada:**
```json
{
  "status": "offline",
  "message": "Gemini API key not configured"
}
```

---

## API Endpoints

### 1. Analizar Imagen

**Endpoint:** `POST /api/gemini/analyze-image`

Analiza una imagen y extrae información visual, colores, calidad, mood y sugerencias SEO.

**Request:**
```bash
curl -X POST http://localhost:3000/api/gemini/analyze-image \
  -H "Content-Type: application/json" \
  -d '{
    "imageUrl": "https://example.com/bread.jpg",
    "prompt": "Analiza esta imagen de pan" // opcional
  }'
```

**Response:**
```json
{
  "success": true,
  "analysis": "Análisis detallado de la imagen...",
  "metadata": {
    "imageUrl": "https://example.com/bread.jpg",
    "timestamp": "2026-10-05T12:34:56.789Z",
    "model": "gemini-pro-vision"
  }
}
```

### 2. Generar Contenido

**Endpoint:** `POST /api/gemini/generate-content`

Genera content marketing (captions, descripciones, etc).

**Request:**
```bash
curl -X POST http://localhost:3000/api/gemini/generate-content \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Crea 5 captions atractivos para Instagram sobre pan artesanal",
    "temperature": 0.7
  }'
```

**Response:**
```json
{
  "success": true,
  "content": "Caption 1: ...\nCaption 2: ...",
  "metadata": {
    "timestamp": "2026-10-05T12:34:56.789Z",
    "model": "gemini-pro",
    "inputLength": 45,
    "outputLength": 1250
  }
}
```

### 3. Generar Prompts para Runway

**Endpoint:** `POST /api/gemini/generate-runway-prompt`

Crea prompts optimizados para generar videos con Runway ML o Pika.

**Request:**
```bash
curl -X POST http://localhost:3000/api/gemini/generate-runway-prompt \
  -H "Content-Type: application/json" \
  -d '{
    "productName": "Masa Madre Artesanal",
    "imageAnalysis": "Pan con costra dorada, fermentación 48h...",
    "style": "cinematic"
  }'
```

**Response:**
```json
{
  "success": true,
  "prompts": "**Opción 1: Cinematic Food Documentary**\n[Prompt completo]...",
  "metadata": {
    "timestamp": "2026-10-05T12:34:56.789Z",
    "model": "gemini-pro",
    "productName": "Masa Madre Artesanal",
    "style": "cinematic"
  }
}
```

### 4. Predecir Engagement

**Endpoint:** `POST /api/gemini/predict-engagement`

Predice métricas de engagement y estrategias de publicación.

**Request:**
```bash
curl -X POST http://localhost:3000/api/gemini/predict-engagement \
  -H "Content-Type: application/json" \
  -d '{
    "imageAnalysis": "Pan artesanal con granos, iluminación natural...",
    "hashtags": ["#pan", "#artesanal", "#LaSerena"]
  }'
```

**Response:**
```json
{
  "success": true,
  "prediction": "1. Tipo de Contenido: Reel corto con close-up del pan...\n2. Mejor Hora: Lunes-viernes 8-9am...",
  "metadata": {
    "timestamp": "2026-10-05T12:34:56.789Z",
    "model": "gemini-pro",
    "hashtagCount": 3
  }
}
```

### 5. Analizar Lote de Imágenes

**Endpoint:** `POST /api/gemini/analyze-batch`

Analiza múltiples imágenes en paralelo.

**Request:**
```bash
curl -X POST http://localhost:3000/api/gemini/analyze-batch \
  -H "Content-Type: application/json" \
  -d '{
    "images": [
      {
        "url": "https://example.com/bread1.jpg",
        "productName": "Baguette"
      },
      {
        "url": "https://example.com/bread2.jpg",
        "productName": "Masa Madre"
      }
    ]
  }'
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "success": true,
      "productName": "Baguette",
      "analysis": "Análisis de Baguette..."
    },
    {
      "success": true,
      "productName": "Masa Madre",
      "analysis": "Análisis de Masa Madre..."
    }
  ],
  "metadata": {
    "timestamp": "2026-10-05T12:34:56.789Z",
    "totalImages": 2,
    "successCount": 2
  }
}
```

---

## Fallback Behavior (Sin Backend)

Si el backend está **offline** o la API Key **no está configurada**:

✅ **Frontend continúa funcionando:**
- Mostrador de productos → ✓ Funciona
- Galería de videos → ✓ Funciona
- Instagram Feed → ✓ Funciona
- Navegación general → ✓ Funciona

❌ **Características que no funcionan:**
- Botón "Analizar con Gemini" en productos → Mostrará error amable
- Sugerencias automáticas en Instagram → No disponibles
- Predicción de engagement → No disponibles

**Comportamiento de error (frontend):**
```javascript
// El frontend captura errores y muestra mensajes amables:
// "Gemini no disponible. Funcionalidad analítica deshabilitada."
```

---

## Solución de Problemas

### Error: "GEMINI_API_KEY not configured"

**Causa:** Variable de entorno no está configurada.

**Solución:**
```bash
# Verificar que .env existe
ls server/.env

# Verificar que contiene GEMINI_API_KEY
cat server/.env | grep GEMINI_API_KEY

# Si no existe, crear:
echo "GEMINI_API_KEY=tu_key_aqui" > server/.env
```

### Error: "Invalid API key"

**Causa:** API Key no es válida o permisos insuficientes.

**Solución:**
1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Verificar que la API Key está habilitada
3. Crear una nueva API Key si es necesario
4. Copiar la nueva key a `server/.env`

### Error: "CORS issues" (desde frontend)

**Causa:** El frontend (puerto 5173) no puede conectar al backend (puerto 3000).

**Solución:** Verificar que el servidor está corriendo:
```bash
# En otra terminal:
lsof -i :3000  # Debe mostrar: node (o npm start)

# Si no está corriendo:
cd server && npm start
```

### Timeout o lentitud

**Causa:** API de Gemini está lenta o hay problemas de conexión.

**Solución:**
- Esperar 30 segundos e intentar nuevamente
- Verificar conexión a internet
- Revisar en [Google Cloud Console](https://console.cloud.google.com/) si hay alertas

### Status "offline" pero API Key está configurada

**Causa:** Problema temporal de conectividad.

**Solución:**
```bash
# Reiniciar servidor
npm start

# Verificar logs:
tail -f server.log  # Si usas nohup
```

---

## Testing

### Ejemplo: CURL completo

```bash
# Análisis de imagen
curl -X POST http://localhost:3000/api/gemini/analyze-image \
  -H "Content-Type: application/json" \
  -d '{
    "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Camponotus_flavomarginatus_ant.jpg/440px-Camponotus_flavomarginatus_ant.jpg"
  }' | jq .

# Generación de contenido
curl -X POST http://localhost:3000/api/gemini/generate-content \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Crea 3 hashtags para panadería artesanal"
  }' | jq .

# Health check
curl http://localhost:3000/api/gemini/health | jq .
```

### Ejemplo: JavaScript (en frontend)

```javascript
// Analizar imagen
fetch('http://localhost:3000/api/gemini/analyze-image', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    imageUrl: 'https://example.com/pan.jpg'
  })
})
  .then(res => res.json())
  .then(data => console.log(data))
  .catch(err => console.error('Error:', err));
```

---

## Modelos Disponibles

| Modelo | Caso de Uso | Tokens Max |
|--------|-----------|-----------|
| `gemini-pro` | Texto y contenido general | 2048 |
| `gemini-pro-vision` | Análisis de imágenes | 4096 |

---

## Costos

La API de Gemini tiene:
- **Tier Gratuito:** 60 requests/minuto (suficiente para desarrollo)
- **Planes pagos:** Consultar en [Google AI Studio](https://makersuite.google.com/)

---

## Resumen de Archivos

| Archivo | Propósito |
|---------|-----------|
| `server/index.js` | Servidor Express principal |
| `server/routes/gemini.js` | Rutas de Gemini API |
| `server/.env` | Variables de entorno (NO comitear) |
| `frontend-v2/js/gemini-client.js` | Cliente frontend para Gemini |

---

## Próximos Pasos

1. ✅ Obtener API Key (Google Cloud Console)
2. ✅ Configurar `.env`
3. ✅ Instalar dependencias (`npm install`)
4. ✅ Iniciar servidor (`npm start`)
5. ✅ Verificar health check
6. ✅ El frontend usa automáticamente los endpoints

---

## Contacto y Soporte

- **Documentación oficial:** [Google AI Python SDK](https://ai.google.dev/docs)
- **Troubleshooting:** Ver sección "Solución de Problemas" arriba
- **Frontend sin backend:** Totalmente funcional, Gemini es opcional

---

**Última actualización:** 2026-10-05  
**Versión:** 1.0
