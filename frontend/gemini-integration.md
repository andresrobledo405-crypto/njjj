# Integración Google Gemini AI - Artesanos Panadería

## Configuración rápida

### 1. Obtener API Key de Google Gemini

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o usa uno existente
3. Activa las siguientes APIs:
   - Google Generative AI API
   - Vertex AI API
4. Ve a "Credenciales" → "Crear credenciales" → "Clave de API"
5. Copia la clave de API

### 2. Configurar variables de entorno

Crea un archivo `.env.local` en la raíz del proyecto:

```env
NEXT_PUBLIC_GEMINI_API_KEY=tu_clave_aqui
NEXT_PUBLIC_GEMINI_MODEL=gemini-pro
NEXT_PUBLIC_GEMINI_VISION_MODEL=gemini-pro-vision
```

> **Nota de seguridad**: Para producción, NO expongas la clave en el frontend. Usa un backend proxy.

## Funciones principales

### Gemini Vision API - Análisis de imágenes

```javascript
async function analyzeInstagramImage(imageUrl) {
  const response = await fetch('/api/gemini/analyze-image', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      imageUrl,
      prompt: `Analiza esta imagen de panadería artesanal para redes sociales.
      Proporciona:
      1. Composición (descripción visual)
      2. Colores dominantes (paleta)
      3. Calidad percibida (1-10)
      4. Mood/atmósfera
      5. SEO Description (100 caracteres)
      6. Hashtags recomendados (10)
      7. Mejoras sugeridas`
    })
  });
  return response.json();
}
```

### Gemini Pro - Generación de contenido

```javascript
async function generateProductDescription(productName, analysisData) {
  const response = await fetch('/api/gemini/generate-content', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      prompt: `Genera una descripción PERFECTA para este producto de panadería:
      
      Producto: ${productName}
      Análisis de imagen: ${JSON.stringify(analysisData)}
      
      Requerimientos:
      1. Descripción atractiva (150 caracteres max)
      2. CTA micro-copy
      3. Prompts para Runway/Pika IA (3 opciones)
      4. Testimonios posibles (2)
      
      Tono: Artesanal, Premium, Auténtico
      Público: Foodies, Health-conscious, Local-first`
    })
  });
  return response.json();
}
```

### Análisis de engagement

```javascript
async function predictEngagement(imageDescription, hashtags) {
  const response = await fetch('/api/gemini/predict-engagement', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      prompt: `Basado en esta imagen de panadería:
      
      Descripción: ${imageDescription}
      Hashtags: ${hashtags.join(', ')}
      
      Predice:
      1. Tipo de contenido más engagable
      2. Mejor hora de publicación
      3. Formato recomendado (feed/reel/story)
      4. CTA más efectivo
      5. Métricas esperadas`
    })
  });
  return response.json();
}
```

## Archivo backend - Backend proxy (RECOMENDADO)

Crea `server/routes/gemini.js`:

```javascript
const express = require('express');
const { GoogleGenerativeAI } = require('@google/generative-ai');
const router = express.Router();

// Inicializar Gemini (usa variable de entorno en server)
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

// Endpoint: Análisis de imagen
router.post('/analyze-image', async (req, res) => {
  try {
    const { imageUrl, prompt } = req.body;
    
    const model = genAI.getGenerativeModel({ model: 'gemini-pro-vision' });
    
    const result = await model.generateContent([
      {
        inlineData: {
          data: Buffer.from(await fetch(imageUrl).then(r => r.arrayBuffer())),
          mimeType: 'image/jpeg',
        },
      },
      prompt,
    ]);
    
    res.json({
      success: true,
      analysis: result.response.text()
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Endpoint: Generación de contenido
router.post('/generate-content', async (req, res) => {
  try {
    const { prompt } = req.body;
    
    const model = genAI.getGenerativeModel({ model: 'gemini-pro' });
    
    const result = await model.generateContent(prompt);
    
    res.json({
      success: true,
      content: result.response.text()
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
```

En `server/index.js`, agrega:

```javascript
const geminiRouter = require('./routes/gemini');
app.use('/api/gemini', geminiRouter);
```

## Instalación de dependencias

```bash
# Backend
npm install @google/generative-ai dotenv

# Frontend (si usas fetch directo)
npm install js-base64
```

## Flujo de trabajo recomendado

### 1. Análisis de imágenes Instagram
- Descarga imágenes de @artesanospanaderials
- Usa Gemini Vision para analizar
- Extrae composición, colores, mood
- Genera descripción SEO

### 2. Generación de contenido
- Basado en análisis de Gemini
- Crea descripción de producto
- Genera 3 prompts para Runway/Pika
- Crea testimonios realistas

### 3. Predición de engagement
- Analiza patrón de mejor contenido
- Recomienda hora/tipo de publicación
- Sugiere CTAs más efectivos
- Propone versiones mejoradas

### 4. Integración con Runway/Pika
- Usa prompts generados por Gemini
- Crea versiones de video mejoradas
- Integra en landing page
- Muestra antes/después

## Seguridad - Checklist

- [ ] Gemini API key en variables de entorno del SERVER (no en frontend .env)
- [ ] Usa backend proxy para llamadas a Gemini
- [ ] Rate limiting en endpoints de Gemini
- [ ] Valida todas las entradas de usuario
- [ ] Implementa CORS restrictivo
- [ ] Log de todas las llamadas a API
- [ ] Cachea resultados de análisis (no re-analizar misma imagen)

## Ejemplos de prompts pre-optimizados

### Análisis de imagen
```
Analiza esta foto de panadería artesanal de La Serena, Chile. Soy @artesanospanaderials en Instagram.

Proporciona JSON con:
{
  "composicion": "...",
  "colores": ["#hex", ...],
  "calidad": 9,
  "mood": "Artesanal, Prémium, Casero",
  "seo_description": "...",
  "hashtags": ["#panartesanal", ...],
  "mejoras_sugeridas": ["..."]
}
```

### Generación de descripción
```
Eres experto en marketing de panaderías artesanales.

Genera descripción para Instagram:
- Producto: Focaccia artesanal
- Características: Hecha con masa madre de 3 días
- Tono: Premium, Local, Auténtico

Proporciona:
1. Caption (150 car) con emojis
2. CTA para generar urgencia
3. 3 prompts para Runway/Pika
4. 2 testimonios realistas
```

### Prompt para Runway/Pika
```
Create a 15-second video for Instagram Reels:
- Scene: Artisanal bakery in La Serena, Chile
- Product: Freshly baked focaccia with rosemary
- Aesthetic: Warm, natural lighting, cinematic
- Audio: Soft Italian background music
- Text overlay: "Hecho con amor en La Serena"
- Call-to-action: "Encuéntranos en @artesanospanaderials"
- Style: Food porn, slow-motion, high-quality
```

## Flujo de integración completo

1. **Usuario sube imagen** → Gemini Vision analiza
2. **Gemini proporciona análisis** → UI muestra resultados
3. **Usuario selecciona opciones** → Gemini genera contenido
4. **Contenido generado** → Usuario copia/comparte
5. **Opcional**: Envía prompt a Runway/Pika para video

## Limites y pricing Gemini

- **Gemini Pro**: Gratis hasta 60 requests/min
- **Gemini Pro Vision**: Gratis hasta 60 requests/min
- **Pricing**: $0.000075/1K input tokens, $0.000225/1K output tokens
- **Batch processing**: Usa google.ai.generativelanguage.v1beta.BatchProcessRequest para grandes volúmenes

## Troubleshooting

| Error | Solución |
|-------|----------|
| `INVALID_ARGUMENT` | Verifica el formato de la imagen (JPEG/PNG/GIF/WEBP) |
| `PERMISSION_DENIED` | Confirma que Gemini API está activada en Google Cloud |
| `RESOURCE_EXHAUSTED` | Implementa queue/retry con backoff exponencial |
| `TIMEOUT` | Aumenta timeout en fetch (default 30s) |

## Próximos pasos

1. Configura Google Cloud Project
2. Obtén API key
3. Despliega backend con Gemini
4. Integra en landing page
5. Prueba con imágenes de Instagram
6. Conecta con Runway/Pika
7. Mide engagement en versiones optimizadas

