# 🚀 Quick Start - Artesanos Panadería + Gemini AI

**Tiempo estimado: 5 minutos**

## Paso 1: Obtener API Key de Google (2 min)

### 1a. Crear Google Cloud Project
1. Ve a https://console.cloud.google.com/
2. Click en selector de proyecto (arriba izq) → "NEW PROJECT"
3. Nombre: `Artesanos AI`
4. Click "CREATE" y espera ~30 segundos

### 1b. Activar Generative AI API
1. Menu (≡) → "APIs & Services" → "Library"
2. Busca "Google Generative AI"
3. Click en el resultado → "ENABLE"

### 1c. Crear API Key
1. APIs & Services → "Credentials"
2. "+ CREATE CREDENTIALS" → "API Key"
3. ⭐ **COPIA LA CLAVE** (la necesitarás en seguida)

## Paso 2: Configurar proyecto local (2 min)

### 2a. Crear .env.local
```bash
# En la carpeta raíz del proyecto
cp .env.example .env.local

# Abre .env.local y reemplaza:
# GEMINI_API_KEY=YOUR_KEY_HERE
# Con tu clave real
```

### 2b. Instalar dependencias
```bash
cd server
npm install @google/generative-ai dotenv node-fetch
```

## Paso 3: Iniciar servidor (1 min)

```bash
# En la carpeta /server
npm start

# Deberías ver:
# ✅ Gemini AI initialized successfully
# Server running on port 3000
```

## Paso 4: Abrir landing page (1 min)

1. Ve a http://localhost:3000/artesanos.html
2. ¡Listo! 🎉

---

## Primer uso: Analizar imagen

1. **Copiar URL de imagen**
   - Sube a Google Images o Instagram
   - Descarga una imagen de pan

2. **Ingresa en el formulario**
   - URL de imagen: `https://...`
   - Nombre del producto: `Focaccia`
   - Click "🤖 Analizar con Gemini"

3. **Espera 5-15 segundos**
   - Verás análisis con:
     - Composición
     - Colores
     - Calidad
     - Mood
     - SEO Description
     - Hashtags

4. **Genera contenido**
   - Click "✨ Generar Contenido"
   - Recibe caption + CTA + testimonios

5. **Crea video prompts**
   - Click "🎬 Prompt para Runway"
   - Obtén 3 prompts para Runway ML / Pika AI

---

## Troubleshooting rápido

| Problema | Solución |
|----------|----------|
| ❌ "Service not initialized" | Verifica `.env.local` tiene API Key real |
| ❌ "PERMISSION_DENIED" | Ve a console.cloud.google.com, verifica que "Google Generative AI API" está ENABLED |
| ❌ "Timeout" | La API es lenta, espera 30s. Intenta con imagen más pequeña |
| ❌ No ve landing page | Verifica http://localhost:3000/artesanos.html (no :8000) |

---

## Integración con Runway ML (Bonus)

1. Ve a https://runway.ml/
2. Crea cuenta
3. Nuevo proyecto → "Generate Video"
4. Pega el prompt de Gemini
5. Espera 2-5 minutos
6. Descarga video
7. Sube a Instagram 📸

---

## Documentación completa

Para más detalles, ver `GEMINI_INTEGRATION_README.md`

---

¿Preguntas? Ver archivo de troubleshooting o abre issue en GitHub.

¡A generar contenido artesanal! 🥖✨

