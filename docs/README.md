# 🍞 Artesanos Panadería v2 - Landing Page Premium

Arquitectura moderna, funciones completas, lista para producción.

---

## 📁 Estructura

```
frontend-v2/
├── index.html                    # HTML principal (Alpine.js + semantic)
├── styles/
│   └── main.css                  # CSS modular (Tailwind style + custom)
├── js/
│   ├── app.js                    # Orquestador principal
│   ├── particle-system.js        # Canvas particles (harina cayendo)
│   ├── gemini-client.js          # Cliente Gemini API
│   ├── video-manager.js          # YouTube + MP4 + Runway
│   └── instagram-loader.js       # Manual upload + Gemini analysis
├── data/
│   └── productos.json            # Datos de productos (6 panes)
├── assets/
│   ├── videos/                   # MP4 locales (heroes, demos)
│   └── placeholders/             # Imágenes productos (generar con IA)
├── AI_VISUAL_PROMPTS.md          # 🎨 3 prompts por producto (realista/minimalista/creativa)
└── README.md                      # Este archivo
```

---

## 🚀 Inicio Rápido

### 1. Generar imágenes de productos
Lee `AI_VISUAL_PROMPTS.md` y genera imágenes en:
- Nano Banana (mejor calidad)
- Midjourney
- Flux
- DALL-E 3

Descarga a `/assets/placeholders/` con nombres:
- `masa-madre.jpg`
- `focaccia.jpg`
- `baguette.jpg`
- `marraqueta.jpg`
- `ciabatta.jpg`
- `croissant.jpg`

### 2. Abrir en navegador
```bash
cd frontend-v2
python3 -m http.server 8000
# Luego abre: http://localhost:8000
```

### 3. Verificar funcionamiento
- ✅ Partículas de harina animadas (hero)
- ✅ Tarjetas de productos con Glassmorphism
- ✅ Videos cargados (YouTube embebido)
- ✅ Botones "Analizar con IA" funcionales
- ✅ Subida de imágenes Instagram

---

## ✨ Características Principales

### 1. **Animaciones Avanzadas**
- **Particle System**: Harina/pan cayendo continuamente
- **Glassmorphism**: Cards con blur y transparencia
- **Intersection Observer**: Lazy animations al scroll
- **Micro-interacciones**: Hover effects, button feedback

### 2. **Integración Gemini**
Cada tarjeta de producto tiene:
- Botón "Analizar con IA"
- Análisis automático de descripción
- Generación de captions para Instagram
- Predicción de engagement
- Prompts para video (Runway ML)

### 3. **Galería Instagram**
- Subida manual de imágenes
- Gemini genera captions automáticamente
- Almacenamiento en localStorage
- Mock engagement (likes/comments)
- Borrable/editable

### 4. **Video Integrado**
- YouTube embebido (3 ejemplos)
- Soporte MP4 local
- Runway ML demo listo
- Responsive video containers

### 5. **Diseño Mobile-First**
- Fully responsive (móvil → desktop)
- CSS Grid dinámico
- Touch-friendly buttons
- Rendimiento optimizado

---

## 🎨 Paleta de Colores

```css
--primary: #d4a574      /* Oro/pan tostado */
--secondary: #8b6f47    /* Marrón tierra */
--accent: #f5e6d3       /* Crema suave */
--dark: #2b2416         /* Chocolate oscuro */
--light: #f9f7f4        /* Blanco off */
```

---

## 🔧 Componentes

### `particle-system.js`
Renderiza partículas Canvas continuamente
- 50 partículas por defecto
- Cayendo + flotando horizontalmente
- Recicla al salir de pantalla
- Optimizado para performance

### `gemini-client.js`
Cliente HTTP para Gemini API
```javascript
// Analizar producto
await gemini.analyzeProduct(product)

// Generar caption Instagram
await gemini.generateCaption(productName, imageUrl)

// Generar 3 prompts para video
await gemini.generateVideoPrompt(productName, description)

// Predicción de engagement
await gemini.predictEngagement(productName, imageUrl)
```

### `video-manager.js`
Gestor de videos multiformat
```javascript
// Renderizar galería
videoManager.renderGallery('container-id')

// Reproducir video específico
videoManager.playVideo('video-id')
```

### `instagram-loader.js`
Carga + análisis de Instagram
```javascript
// Agregar post
await instagramLoader.addPost(imageUrl, caption)

// Renderizar feed
instagramLoader.renderFeed('feed-container-id')

// Eliminar post
instagramLoader.removePost(postId)
```

---

## 📱 Responsive Breakpoints

```css
Mobile:  < 768px   (1 columna)
Tablet:  768px     (2 columnas)
Desktop: 1024px    (3-4 columnas)
```

---

## 🤖 Gemini API Integration

El app intenta conectar con backend en `http://localhost:3000/api/gemini/*`

Si no está disponible, **fallback a análisis local** (no falla):
```javascript
// Si API falla:
return `Análisis local: ${product.nombre} es un pan artesanal premium`
```

Para producción con Gemini real:
1. Configura backend en `server/routes/gemini.js`
2. Obtén API Key en `console.cloud.google.com`
3. Configura `.env` con `GEMINI_API_KEY`
4. Inicia servidor: `node server.js`

---

## 📊 Datos

### `productos.json`
```json
{
  "productos": [
    {
      "id": "masa-madre",
      "nombre": "Masa Madre",
      "descripcion": "Pan tradicional fermentado naturalmente",
      "imagen": "/assets/placeholders/masa-madre.jpg",
      "precio": "$4.500",
      "tags": ["clásico", "artesanal", "fermentado"],
      "geminiTopic": "Pan de masa madre tradicional chileno"
    }
    // ... más productos
  ]
}
```

Editable en tiempo real sin recargar (recargar la página).

---

## 🎬 Generar Videos IA

### Prompts incluidos en `AI_VISUAL_PROMPTS.md`

Copia cada prompt y pégalo en:
- **Runway ML** (mejor para panadería)
- **Pika AI** (rápido, económico)
- **Synthesia** (personajes hablantes)

Guarda videos a `/assets/videos/` y actualiza `video-manager.js`

---

## 🧪 Testing

### Local
```bash
# Abrir en puerto 8000
python3 -m http.server 8000

# O con Node
npx http-server
```

### Funcionalidades a probar
1. Partículas ¿animan en hero?
2. Scroll ¿activa fade-in de cards?
3. Click en "Analizar" ¿abre modal? (puede fallar si no hay backend, es OK)
4. Subida Instagram ¿guarda en localStorage?
5. Videos ¿se reproducen al hacer scroll?

---

## 🚢 Deployment

### GitHub Pages
```bash
# Copiar frontend-v2 a docs/
cp -r frontend-v2/* docs/

# Commitear + push
git add docs/
git commit -m "deploy: v2 landing page"
git push
```

Luego en settings de repo: GitHub Pages → Branch: main, folder: /docs

### Netlify / Vercel
```bash
# Conectar repo
# Rama: main
# Build: (sin build, es estático)
# Publish: frontend-v2/
```

---

## 📝 Próximos Pasos

1. ✅ Generar 6 imágenes de productos con IA
2. ✅ Subir a `/assets/placeholders/`
3. ✅ Grabar/descargar 2-3 videos demostración
4. ✅ Subir a `/assets/videos/`
5. ✅ Actualizar `video-manager.js` con URLs reales
6. ✅ Configurar Gemini API backend (opcional, funciona sin él)
7. ✅ Deploy a GitHub Pages / Netlify

---

## 🐛 Troubleshooting

### Las partículas no animan
- Verifica que Canvas elemento esté visible
- Revisa console para errores de `particle-system.js`
- Prueba en navegador moderno (Chrome, Safari, Firefox)

### Videos no cargan
- Verifica URLs en `video-manager.js`
- YouTube embeds necesitan permiso CORS
- MP4 locales deben estar en `/assets/videos/`

### Gemini fallando
- ✅ Normal si no hay backend
- Fallback local sigue funcionando
- Para API real, configura `.env` con GEMINI_API_KEY

### Instagram no guarda
- Verifica localStorage habilitado
- Abre DevTools → Application → LocalStorage
- Prueba en navegador reciente

---

## 📚 Referencias

- [Alpine.js](https://alpinejs.dev) - Interactividad ligera
- [CSS Grid](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout)
- [Canvas API](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API)
- [Intersection Observer](https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API)

---

## 👨‍💻 Autor

Generado con **Claude Code** + Patrón **Desarrollador Web Senior** + **Director de Arte para IA Visual**

