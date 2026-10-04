# 🤖 Google Gemini AI Integration - Artesanos Panadería

Integración completa de Google Gemini AI para análisis de imágenes, generación de contenido y creación de prompts para video.

## 📋 Tabla de Contenidos

1. [Configuración rápida](#configuración-rápida)
2. [Obtener API Key](#obtener-api-key)
3. [Instalación](#instalación)
4. [Estructura del proyecto](#estructura-del-proyecto)
5. [Uso de la landing page](#uso-de-la-landing-page)
6. [Flujo de trabajo completo](#flujo-de-trabajo-completo)
7. [Prompts pre-optimizados](#prompts-pre-optimizados)
8. [Troubleshooting](#troubleshooting)

## 🚀 Configuración rápida

### 1. Obtener Google Gemini API Key

#### Paso 1: Ir a Google Cloud Console
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Si no tienes un proyecto, crea uno nuevo:
   - Click en el selector de proyecto (arriba a la izquierda)
   - Click en "NEW PROJECT"
   - Ingresa nombre: "Artesanos Panadería"
   - Click "CREATE"

#### Paso 2: Activar APIs
1. Abre el menú de hamburguesa (≡) → APIs & Services → Library
2. Busca "Google Generative AI" (o "Vertex AI")
3. Click en cada uno y presiona "ENABLE"
4. Repite para "Google Generative AI API"

#### Paso 3: Crear API Key
1. Ve a APIs & Services → Credentials
2. Click "Create Credentials" → "API Key"
3. Copia la clave (la verás en una ventana emergente)
4. Guárdala en lugar seguro (**NO la compartas**)

#### Paso 4: Configurar restricciones (Recomendado para producción)
1. Haz click en tu API Key
2. Bajo "API restrictions", selecciona "Google Generative AI API"
3. Bajo "Application restrictions", selecciona "HTTP referrers"
4. Agrega tus dominios: `localhost:3000`, `tudominio.com`

### 2. Configurar variables de entorno

1. Copia `.env.example` a `.env.local`:
```bash
cp .env.example .env.local
```

2. Edita `.env.local` e ingresa tu API Key:
```env
GEMINI_API_KEY=your_actual_api_key_here
PORT=3000
```

3. **Importante**: `.env.local` está en `.gitignore`, así que no se subirá a Git

### 3. Instalar dependencias

```bash
# Backend
cd server
npm install

# Instalar dependencia para Gemini
npm install @google/generative-ai dotenv
```

### 4. Iniciar servidor

```bash
# En /server directory
npm start

# O con nodemon para desarrollo
npm install -D nodemon
npx nodemon index.js
```

El servidor debería estar en `http://localhost:3000`

### 5. Acceder a la landing page

Abre en tu navegador:
```
http://localhost:3000/artesanos.html
```

¡Listo! Ya puedes empezar a analizar imágenes.

## 🔑 Obtener API Key - Guía completa

### Video Tutorial (Recomendado)
1. Abre https://youtu.be/jXKLjOy7Y9E
2. Sigue los pasos (3 minutos)

### Pasos textuales detallados

#### A. Crear Google Cloud Project

```
console.cloud.google.com
  → Selector de proyecto (arriba izq)
  → NEW PROJECT
  → Nombre: "Artesanos AI"
  → Location: (default)
  → CREATE
  → Espera ~2 minutos a que se cree
```

#### B. Activar Google Generative AI API

```
Dashboard
  → Menu (≡) → APIs & Services → Library
  → Busca: "Google Generative AI"
  → Click en el resultado
  → ENABLE
  → Espera confirmación
```

#### C. Crear API Key

```
APIs & Services
  → Credentials (izquierda)
  → + CREATE CREDENTIALS
  → API Key
  → Copia la clave que aparece
  → CLOSE
```

#### D. Restricciones (Producción)

```
Credentials
  → Tu API Key (click en ella)
  → API restrictions
    → Restrict key
    → Selecciona "Google Generative AI API"
  → Application restrictions
    → HTTP referrers
    → Agregar: *.yourdomain.com, localhost:3000
  → SAVE
```

## 📦 Instalación

### Requisitos previos

- Node.js 18+
- npm o yarn
- Google Cloud Project con API habilitada
- Gemini API Key

### Paso a paso

1. **Clonar repo** (si es necesario)
```bash
git clone <repo-url>
cd njjj
```

2. **Configurar variables de entorno**
```bash
# Backend
cp .env.example .env.local
# Editar y agregar GEMINI_API_KEY
```

3. **Instalar dependencias**
```bash
cd server
npm install @google/generative-ai dotenv node-fetch
cd ..
```

4. **Iniciar servidor**
```bash
cd server
npm start
```

5. **En otra terminal, servir frontend** (si es necesario)
```bash
# Opción 1: Python
cd frontend
python -m http.server 8000

# Opción 2: Node
npx http-server frontend --port 8000
```

6. **Abrir en navegador**
```
http://localhost:3000/artesanos.html
```

## 📁 Estructura del proyecto

```
njjj/
├── frontend/
│   ├── artesanos.html          ← Landing page principal
│   ├── gemini-integration.md   ← Documentación técnica
│   └── styles/
├── server/
│   ├── routes/
│   │   └── gemini.js           ← Endpoints de Gemini
│   ├── index.js                ← Servidor principal
│   └── package.json
├── .env.local                  ← Configuración (NO compartir)
├── .env.example                ← Template
└── GEMINI_INTEGRATION_README.md ← Este archivo
```

## 💻 Uso de la landing page

### Interfaz principal

1. **Hero Section**: Presentación de Artesanos Panadería
2. **Productos**: Grid con 6 productos artesanales
3. **Analizador**: Panel con funcionalidad Gemini
4. **Instagram**: Link a perfil de redes
5. **Contacto**: Datos de ubicación

### Panel Analizador Gemini

```
┌─────────────────────────────────────────┐
│  📸 Analizar Imagen de Instagram        │
├─────────────────────────────────────────┤
│                                         │
│  URL de Imagen: [________________]      │
│  Nombre del Producto: [__________]      │
│  Personalizar análisis: [____text____]  │
│                                         │
│  [🤖 Analizar] [✨ Generar] [🎬 Prompt] │
│                                         │
│  ✅ Resultados aquí abajo...            │
│                                         │
└─────────────────────────────────────────┘
```

### Pasos para usar

#### 1. Analizar Imagen

```
1. Ingresa URL de imagen (Instagram o local)
2. Ingresa nombre del producto (ej: "Focaccia con Romero")
3. (Opcional) Personaliza el análisis
4. Click "🤖 Analizar con Gemini"
5. Espera 5-15 segundos
6. Ve los resultados:
   - Composición visual
   - Paleta de colores
   - Calidad (1-10)
   - Mood/Atmósfera
   - SEO Description
   - 10 Hashtags
   - Mejoras sugeridas
```

#### 2. Generar Contenido

```
1. Después de analizar imagen
2. Click "✨ Generar Contenido"
3. Recibe:
   - Caption Instagram (150 char)
   - CTA Micro-copy
   - Testimonios (2)
   - Tags recomendados (10)
```

#### 3. Crear Prompts para Video

```
1. Después de analizar imagen
2. Click "🎬 Prompt para Runway"
3. Recibe 3 prompts optimizados para:
   - Runway ML
   - Pika AI
   - Listos para copiar-pegar directamente
```

## 🔄 Flujo de trabajo completo

### Workflow: De Instagram a Video Mejorado

```
┌─────────────────────────────────────────────────────────┐
│  FLUJO COMPLETO: Instagram → Gemini → Runway → Publish  │
└─────────────────────────────────────────────────────────┘

PASO 1: Descargar imágenes
├─ Ve a @artesanospanaderials en Instagram
├─ Descarga 5-10 fotos de productos
└─ Guarda URLs o localiza archivos

PASO 2: Analizar con Gemini Vision
├─ Abre artesanos.html
├─ Ingresa URL de imagen
├─ Ingresa nombre del producto
├─ Click "🤖 Analizar"
├─ Recibe: análisis detallado de composición, colores, mood
└─ Guardar resultados (copiar a Google Docs o Notion)

PASO 3: Generar Contenido
├─ Click "✨ Generar Contenido"
├─ Recibe: Caption Instagram + CTA + Testimonios
├─ Copia caption para Instagram
└─ Programa publicación

PASO 4: Crear Prompts para Video
├─ Click "🎬 Prompt para Runway"
├─ Recibe 3 prompts profesionales
├─ Elige tu favorito
└─ Copia el prompt

PASO 5: Generar video en Runway ML
├─ Ve a runway.com (requiere cuenta)
├─ Nuevo proyecto → Video Generation
├─ Pega prompt de Gemini
├─ Configura: 15-20 segundos, 1080p
├─ Genera video (~2-5 minutos)
└─ Descarga MP4

PASO 6: Publicar
├─ Ve a Instagram
├─ Nuevo Reel
├─ Sube video de Runway
├─ Usa caption generada por Gemini
├─ Agrega hashtags sugeridos
└─ Publica y comparte link en stories

PASO 7: Medir engagement
├─ Espera 24 horas
├─ Compara views, likes, comments
├─ Nota qué funcionó mejor
└─ Ajusta próximos prompts según resultados
```

## 📝 Prompts pre-optimizados

### Prompt 1: Análisis de Imagen

```javascript
// Pre-optimizado para panaderías artesanales
const analyzePrompt = `Analiza esta imagen de panadería artesanal de La Serena, Chile.

ANÁLISIS REQUERIDO:
1. Composición Visual: Describe disposición, ángulo, profundidad, balance
2. Paleta de Colores: Lista colores dominantes con hexadecimales
3. Calidad Fotográfica: Evaluación 1-10 (1=pobre, 10=excelente)
4. Mood/Atmósfera: Sensación que transmite (cálido, artesanal, prémium, etc)
5. Descripción SEO: 100 caracteres max, optimizada para buscadores
6. Hashtags: 10 hashtags trending y relevantes
7. Mejoras: 3 sugerencias específicas para maximizar engagement

CONTEXTO:
- Marca: Artesanos Panadería
- Instagram: @artesanospanaderials
- Público: Foodies, Health-conscious, Local-first
- Tono: Premium, Artesanal, Auténtico

FORMATO: Estructura clara, markdown, listo para copiar-pegar en notas.`;
```

### Prompt 2: Generación de Caption Instagram

```javascript
const captionPrompt = `Eres copywriter especializado en food marketing.

TAREA: Crear caption Instagram para esta panadería artesanal.

ANÁLISIS PREVIO:
${previousAnalysis}

REQUERIMIENTOS:
1. Caption principal (150 caracteres max)
   - Incluir 3-5 emojis relevantes
   - Crear urgencia o curiosidad
   - Mencionar ingredientes/proceso

2. CTA (Call-to-Action)
   - "Encuéntranos en..."
   - "Compra ahora..."
   - Link a WhatsApp o Instagram

3. Testimonios (2)
   - Realistas, específicos
   - Con "comillas"
   - Mencionar qué amaron del producto

4. Hashtags (10)
   - #panartesanal #masremadre
   - #laserena #chile
   - Trending de comida
   - Mix: popular + nicho

EJEMPLOS DE TONO:
- "Masa madre de 3 días, crujiente por fuera, tierno por dentro 🥖✨"
- "Cada bocado cuenta una historia de pasión y tradición"
- "Hecho con amor en La Serena"

RESPONDE EN FORMATO LIMPIO, LISTO PARA COPIAR.`;
```

### Prompt 3: Video para Runway ML

```javascript
const runwayPrompt = `Create a cinematic 15-second video for Instagram Reels:

SUBJECT: Artisan Bakery - [Product Name]
LOCATION: La Serena, Chile
BRAND: @artesanospanaderials

VISUAL DIRECTION:
- Shot 1 (0-5s): Close-up of fresh bread in natural light
  - Slow-motion, 60fps
  - Warm golden hour lighting
  - Steam/vapor details visible
  - Text overlay: "Hecho con amor"

- Shot 2 (5-10s): Hands preparing or cutting bread
  - Show texture, crust detail
  - Artisanal process focus
  - Dust particles, steam in air
  - Text overlay: "Masa madre de 3 días"

- Shot 3 (10-15s): Final product beauty shot
  - Product on rustic plate
  - Styled minimalist
  - Text overlay: "@artesanospanaderials"
  - Text: "Encuéntranos en La Serena"

TECHNICAL SPECS:
- Resolution: 1080x1920 (vertical Reel)
- Duration: 15 seconds
- Style: Food porn, luxury, artisanal
- Music: Soft Italian background, subtle sounds (knife, crunching)
- Color Grading: Warm tones, 55% saturation boost
- Transitions: Smooth cross-dissolves (0.5s)

MOOD: Premium, Artisanal, Authentic, Local Pride
MOOD KEYWORDS: cinematic, slow-motion, luxury, handmade, traditional

BRAND ELEMENTS:
- Logo appearance: Bottom right corner (2s duration)
- Branding: Mention "artesanospanaderials" and "La Serena"
- Contact: Include WhatsApp or Instagram handle (text overlay last 2s)

CALL-TO-ACTION: "¡Visítanos!" or "Compra ahora en [link]"

OUTPUT: High-quality, 1080x1920 vertical video, ready for Instagram Reels`;
```

## 🔧 API Endpoints

### Endpoint: Analizar Imagen

```bash
POST /api/gemini/analyze-image

Request:
{
  "imageUrl": "https://example.com/image.jpg",
  "prompt": "Analiza esta panadería..." // opcional
}

Response:
{
  "success": true,
  "analysis": "Composición: ...\nColores: ...",
  "metadata": {
    "imageUrl": "...",
    "timestamp": "2024-10-04T...",
    "model": "gemini-pro-vision"
  }
}
```

### Endpoint: Generar Contenido

```bash
POST /api/gemini/generate-content

Request:
{
  "prompt": "Genera un caption Instagram para...",
  "temperature": 0.7  // opcional (0-1)
}

Response:
{
  "success": true,
  "content": "Caption: 🥖 Cada mañana...",
  "metadata": {
    "timestamp": "2024-10-04T...",
    "model": "gemini-pro"
  }
}
```

### Endpoint: Generar Prompts Runway

```bash
POST /api/gemini/generate-runway-prompt

Request:
{
  "productName": "Focaccia",
  "imageAnalysis": "Composición: ...",
  "style": "cinematic"  // opcional
}

Response:
{
  "success": true,
  "prompts": "Opción 1: Create a cinematic...",
  "metadata": {
    "timestamp": "2024-10-04T...",
    "model": "gemini-pro"
  }
}
```

## 🔒 Seguridad - Checklist

- [ ] API Key en `.env.local` (nunca en GitHub)
- [ ] `.env.local` está en `.gitignore`
- [ ] Backend proxy configurado (no exponer API Key en frontend)
- [ ] CORS configurado correctamente
- [ ] Rate limiting implementado
- [ ] Todas las entradas validadas
- [ ] HTTPS en producción
- [ ] Logs de todas las llamadas API
- [ ] Cache implementado (no re-analizar misma imagen)

## 🚨 Troubleshooting

### Error: "INVALID_ARGUMENT"

**Causa**: Formato de imagen inválido
**Solución**:
```
- Verifica que sea JPEG, PNG, GIF o WEBP
- Tamaño máximo: 20MB
- Intenta con otra imagen
```

### Error: "PERMISSION_DENIED"

**Causa**: API Key inválida o API no activada
**Solución**:
```
1. Verifica GEMINI_API_KEY en .env.local
2. Ve a console.cloud.google.com
3. Asegúrate que "Google Generative AI API" está ENABLED
4. Recrear API Key si es necesario
```

### Error: "RESOURCE_EXHAUSTED"

**Causa**: Límite de rate alcanzado
**Solución**:
```
- Espera 1-2 minutos
- Implementa backoff exponencial
- Usa batch processing para múltiples imágenes
```

### Timeout después de 30 segundos

**Causa**: Imagen grande o conexión lenta
**Solución**:
```
- Aumenta timeout en fetch (default 30s)
- Reduce tamaño de imagen
- Optimiza conexión
```

### "Service not initialized"

**Causa**: `.env.local` no tiene GEMINI_API_KEY
**Solución**:
```
1. Copia .env.example a .env.local
2. Ingresa tu API Key real
3. Reinicia servidor: npm start
4. Verifica: GET /api/gemini/health
```

## 📊 Pricing y Limites

### Google Gemini Pricing (Oct 2024)

| Modelo | Input | Output | Límite Gratis |
|--------|-------|--------|---------------|
| Gemini Pro | $0.000075/1K tokens | $0.000225/1K tokens | 60 req/min |
| Gemini Pro Vision | $0.000375/1K tokens | $0.001125/1K tokens | 60 req/min |

### Estimación de costos

```
Caso de uso: 100 imágenes/mes analizadas

Gemini Vision (análisis):
- 100 imágenes × ~2000 tokens = 200K tokens
- Costo: 200K × $0.000375 = $0.075/mes

Gemini Pro (contenido):
- 100 prompts × ~1000 tokens = 100K tokens input
- 100 respuestas × ~500 tokens = 50K tokens output
- Costo: (100K × $0.000075) + (50K × $0.000225) = $19.50/mes

TOTAL ESTIMADO: ~$20/mes para uso moderado
```

## 🎯 Casos de uso

### 1. Análisis diario de Instagram
```
Cada mañana:
1. Descarga foto nueva de Instagram
2. Analiza con Gemini
3. Genera caption
4. Programa publicación
5. Mide engagement
```

### 2. Batch processing
```
Analizar 50 imágenes de archivo:
1. POST /api/gemini/analyze-batch
2. Recibe análisis de todas
3. Exporta CSV con resultados
4. Elige las mejores 10
5. Genera videos
```

### 3. A/B Testing
```
Crear 2 versiones de cada producto:
- Versión A: Original
- Versión B: Optimizada con Gemini
Mide qué funciona mejor
Aprende qué genera engagement
```

## 📞 Soporte

Para problemas específicos:

1. **Documentación oficial**: https://ai.google.dev/
2. **Comunidad Gemini**: https://discord.gg/ai
3. **Issues en GitHub**: Crear issue con error completo
4. **Stack Overflow**: Tag `gemini-api`

## 🎓 Recursos de aprendizaje

- [Google AI Studio](https://makersuite.google.com/app/prompts)
- [Gemini API Docs](https://ai.google.dev/docs)
- [Runway ML Docs](https://docs.runwayml.com/)
- [Social Media Marketing Best Practices](https://www.hootsuite.com/blog)

## 📈 Próximos pasos

1. ✅ Configurar Gemini API
2. ✅ Probar landing page
3. ✅ Analizar 10 imágenes de Instagram
4. ✅ Generar contenido para cada una
5. ✅ Crear videos en Runway
6. ✅ Publicar y medir engagement
7. 🔄 Iterar y optimizar basado en datos

## 📄 Licencia

Este proyecto es parte de Artesanos Panadería. Todos los derechos reservados.

---

**Última actualización**: 2024-10-04
**Versión**: 1.0
**Mantenedor**: Claude AI

