# Plan de Implementación: Repurposing SaaS

**Duración:** 26 semanas (6 meses)  
**Esfuerzo:** 1 persona full-time  
**Inicio Proyectado:** Semana del 7 de octubre, 2026  
**MVP Completo:** Semana 4  
**Launch Público:** Semana 8  

---

## FASE 1: PREPARACIÓN & MVP (Semanas 1-4)

### Semana 1: Setup de Infraestructura

**Objetivo:** Tener todas las cuentas creadas y conectadas

#### Paso 1.1: Crear Cuentas Esenciales (Día 1)
- [ ] **Make.com** — Cuenta gratuita (https://make.com)
  - Crear equipo
  - Notar API keys para guardar
  
- [ ] **Supabase** — Cuenta gratuita (https://supabase.com)
  - Crear proyecto `repurpose-saas-prod`
  - Guardar URL de la BD y API key (anon + service_role)
  
- [ ] **Framer** — Cuenta gratuita (https://framer.com)
  - Crear proyecto `repurpose-ui`
  - Setup template de dashboard
  
- [ ] **Claude API** — Activar (https://console.anthropic.com)
  - Crear API key
  - Setup billing ($5 crédito inicial)
  
- [ ] **AWS S3 o Cloudinary** — Para almacenar videos
  - S3: Create bucket `repurpose-saas-videos`
  - Generar AWS credentials
  - OR Cloudinary: Crear cuenta, guardar API key
  
- [ ] **Stripe** — Cuenta de prueba (https://stripe.com)
  - Activar modo test
  - Guardar API keys (publishable + secret)

**Tiempo:** 2-3 horas  
**Checklist:**
- [ ] 6 cuentas creadas
- [ ] Todos los API keys guardados en 1Password/secure file
- [ ] Billing configurado en cada cuenta

---

#### Paso 1.2: Setup Node.js + Railway (Día 2)
- [ ] **Crear repo Git local**
  ```bash
  mkdir repurpose-saas
  cd repurpose-saas
  git init
  ```
  
- [ ] **Setup Node.js project**
  ```bash
  npm init -y
  npm install express dotenv axios multer sharp ffmpeg-static
  ```
  
- [ ] **Create .env file** (guardar en .gitignore)
  ```
  CLAUDE_API_KEY=sk-...
  SUPABASE_URL=https://...
  SUPABASE_KEY=eyJhbGc...
  STRIPE_SECRET=sk_test_...
  AWS_ACCESS_KEY_ID=...
  AWS_SECRET_ACCESS_KEY=...
  ```
  
- [ ] **Create GitHub repo** (privado)
  ```bash
  git remote add origin https://github.com/[your-repo]
  git add .
  git commit -m "Initial setup"
  git push -u origin main
  ```
  
- [ ] **Deploy a Railway** (https://railway.app)
  - Conectar GitHub repo
  - Variables de entorno desde .env
  - Deploy automático en cada push

**Tiempo:** 2-3 horas  
**Resultado:** Node.js server corriendo en Railway.app

---

#### Paso 1.3: Supabase Schema (Día 2-3)
En Supabase SQL Editor, correr:

```sql
-- 1. Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255),
  plan VARCHAR(50) DEFAULT 'free' CHECK(plan IN ('free', 'starter', 'pro', 'agency')),
  stripe_customer_id VARCHAR(255),
  stripe_subscription_id VARCHAR(255),
  videos_processed INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Videos table
CREATE TABLE videos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255),
  original_url VARCHAR(2048),
  status VARCHAR(50) DEFAULT 'uploaded' CHECK(status IN ('uploaded', 'processing', 'ready', 'error')),
  duration_sec INT,
  viral_score_tiktok DECIMAL(3,1),
  viral_score_reels DECIMAL(3,1),
  viral_score_shorts DECIMAL(3,1),
  viral_score_linkedin DECIMAL(3,1),
  best_moment_start INT,
  best_moment_end INT,
  error_message TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. Clips table
CREATE TABLE clips (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
  platform VARCHAR(50) CHECK(platform IN ('tiktok', 'reels', 'shorts', 'linkedin', 'twitter')),
  clip_url VARCHAR(2048),
  published_url VARCHAR(2048),
  duration_sec INT,
  status VARCHAR(50) DEFAULT 'draft' CHECK(status IN ('draft', 'published', 'scheduled')),
  views INT DEFAULT 0,
  likes INT DEFAULT 0,
  shares INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 4. Analytics table
CREATE TABLE analytics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clip_id UUID REFERENCES clips(id) ON DELETE CASCADE,
  metric_date DATE,
  views INT DEFAULT 0,
  likes INT DEFAULT 0,
  shares INT DEFAULT 0,
  clicks INT DEFAULT 0,
  engagement_rate DECIMAL(5,2),
  synced_at TIMESTAMP DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_videos_user_id ON videos(user_id);
CREATE INDEX idx_clips_video_id ON clips(video_id);
CREATE INDEX idx_analytics_clip_id ON analytics(clip_id);
```

**Tiempo:** 1-2 horas  
**Resultado:** BD lista para recibir datos

---

#### Paso 1.4: Framer Frontend Básico (Día 3-4)
En Framer, crear estas 4 páginas:

1. **Landing Page**
   - Hero section con CTA "Comenzar Gratis"
   - Pricing (3 planes)
   - Testimonios placeholder
   - Footer

2. **Auth Page** (Login/Signup)
   - Email + password
   - OAuth con Google (luego)
   - Redirect a dashboard si autenticado

3. **Dashboard**
   - Bienvenida usuario
   - Upload area (drag & drop)
   - Botón "Procesar Video"
   - Lista de videos procesados (vacía por ahora)

4. **Settings**
   - Conectar TikTok (OAuth)
   - Cambiar plan
   - Cancelar suscripción

**No requiere conexión a BD aún.** Solo UI mockup.

**Tiempo:** 4-6 horas  
**Nota:** Framer genera HTML/React que luego conectaremos

---

### Semana 2: Claude API + Make.com Flujo

#### Paso 2.1: Crear Prompt + Test Claude API (Día 5)

En Node.js endpoint `/api/analyze-video`:

```javascript
// /api/analyze-video
const axios = require('axios');

app.post('/api/analyze-video', async (req, res) => {
  const { videoPath, transcript } = req.body;
  
  try {
    // 1. Extraer frames (usando ffmpeg + openai vision)
    const frames = await extractKeyFrames(videoPath); // Tu función
    
    // 2. Llamar Claude con frames + transcript
    const response = await axios.post(
      'https://api.anthropic.com/v1/messages',
      {
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 1024,
        messages: [
          {
            role: 'user',
            content: [
              {
                type: 'text',
                text: `Eres un experto en contenido viral. Analiza este video educativo/marketing.
                
Transcripción: "${transcript}"

Tareas:
1. Identifica el momento más inesperado/hook (timestamp)
2. Calcula virality score 1-10 para:
   - TikTok (Gen Z, corto, viral)
   - Instagram Reels (polished, aspiracional)
   - YouTube Shorts (educativo)
   - LinkedIn (profesional)
3. Propón 5 hashtags
4. ¿Necesita captions forzados? sí/no

Responde en JSON:
{
  "viral_scores": {
    "tiktok": 8,
    "reels": 6,
    "shorts": 7,
    "linkedin": 3
  },
  "best_moment": {
    "start_sec": 45,
    "end_sec": 75,
    "reason": "El CEO dice algo inesperado"
  },
  "hashtags": ["#SaaS", "#Startup", ...],
  "needs_captions": true,
  "recommended_duration_per_platform": {
    "tiktok": 45,
    "reels": 60,
    "shorts": 50
  }
}`,
              },
              // Si tienes frames, agregarlos aquí:
              // {
              //   "type": "image",
              //   "source": {
              //     "type": "base64",
              //     "media_type": "image/jpeg",
              //     "data": "..." // base64 de frame
              //   }
              // }
            ],
          },
        ],
      },
      {
        headers: {
          'x-api-key': process.env.CLAUDE_API_KEY,
          'anthropic-version': '2023-06-01',
        },
      }
    );
    
    const analysis = JSON.parse(response.data.content[0].text);
    res.json(analysis);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: error.message });
  }
});
```

**Test:**
```bash
curl -X POST http://localhost:3000/api/analyze-video \
  -H "Content-Type: application/json" \
  -d '{
    "videoPath": "/tmp/test.mp4",
    "transcript": "Hola, hoy hablaremos de SaaS..."
  }'
```

**Tiempo:** 3-4 horas  
**Resultado:** Endpoint funcional que analiza videos

---

#### Paso 2.2: FFmpeg Endpoint (Día 6)

En `/api/process-clips`:

```javascript
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

app.post('/api/process-clips', async (req, res) => {
  const { videoPath, bestMomentStart, bestMomentEnd, platforms } = req.body;
  // platforms = ['tiktok', 'reels', 'shorts']
  
  const outputDir = '/tmp/clips';
  fs.mkdirSync(outputDir, { recursive: true });
  
  const results = {};
  
  // Definir specs por plataforma
  const specs = {
    tiktok: { width: 1080, height: 1920, duration: 45, fps: 30 },
    reels: { width: 1080, height: 1920, duration: 60, fps: 30 },
    shorts: { width: 1080, height: 1920, duration: 50, fps: 30 },
  };
  
  for (const platform of platforms) {
    const spec = specs[platform];
    const outputPath = path.join(outputDir, `${platform}_clip.mp4`);
    
    // FFmpeg command: recortar + redimensionar + optimizar
    const ffmpegCmd = `ffmpeg -i "${videoPath}" \
      -ss ${bestMomentStart} -t ${spec.duration} \
      -s ${spec.width}x${spec.height} \
      -r ${spec.fps} \
      -c:v libx264 -preset medium -crf 23 \
      -c:a aac -b:a 128k \
      "${outputPath}"`;
    
    await new Promise((resolve, reject) => {
      exec(ffmpegCmd, (error) => {
        if (error) reject(error);
        else resolve();
      });
    });
    
    // Subir a S3/Cloudinary
    const cloudinaryPath = await uploadToCloudinary(outputPath);
    results[platform] = {
      url: cloudinaryPath,
      duration: spec.duration,
    };
  }
  
  res.json(results);
});
```

**Tiempo:** 4-5 horas  
**Resultado:** Puedes generar clips en 3 formatos automáticamente

---

#### Paso 2.3: Crear Make.com Flujo (Día 7)

En Make.com:

1. **Trigger:** Webhook (escucha POST a Make.com)
   ```
   URL: https://hook.make.com/...
   ```

2. **Modulo 1:** Guardar video en Supabase Storage
   - Recibe: videoFile (base64)
   - Guarda en bucket `videos/`

3. **Modulo 2:** Llamar Node.js `/api/analyze-video`
   - Input: videoPath
   - Output: viral_scores, best_moment, hashtags

4. **Modulo 3:** Decisión condicional
   ```
   IF viral_score_tiktok > 4
   THEN continuar
   ELSE notificar usuario "contenido muy bajo"
   ```

5. **Modulo 4:** Llamar Node.js `/api/process-clips`
   - Input: videoPath, best_moment, platforms
   - Output: 3 URLs de clips

6. **Modulo 5:** Generar captions (DeepL API)
   - Para cada clip → traducir + generar subtítulos

7. **Modulo 6:** Guardar en Supabase `clips` table
   - Insertar record por cada clip generado

8. **Modulo 7:** Enviar email
   - "¡Tus 3 clips están listos!"

**Tiempo:** 6-8 horas (hay que debugging)  
**Resultado:** Flujo automático end-to-end

---

### Semana 3: Conectar APIs de Redes Sociales

#### Paso 3.1: TikTok API Setup (Día 11-12)

1. **Registrarse en TikTok Developer:**
   - https://developer.tiktok.com
   - Crear aplicación
   - Activar permisos: video.upload, video.publish
   - Guardar Client ID + Secret

2. **Implementar OAuth 2.0:**
   ```javascript
   // /auth/tiktok/callback
   app.get('/auth/tiktok/callback', async (req, res) => {
     const { code } = req.query;
     
     // Intercambiar código por access token
     const response = await axios.post(
       'https://open.tiktokapis.com/v1/oauth/token/',
       {
         client_id: process.env.TIKTOK_CLIENT_ID,
         client_secret: process.env.TIKTOK_CLIENT_SECRET,
         code,
         grant_type: 'authorization_code',
       }
     );
     
     const { access_token, user_id } = response.data;
     
     // Guardar en BD
     await db.users.update(
       { id: req.user.id },
       { tiktok_access_token: access_token, tiktok_user_id: user_id }
     );
     
     res.redirect('/dashboard?success=tiktok_connected');
   });
   ```

3. **Endpoint para publicar:**
   ```javascript
   // POST /api/publish/tiktok
   app.post('/api/publish/tiktok', async (req, res) => {
     const { clipUrl, title } = req.body;
     const user = await db.users.findById(req.user.id);
     
     // Descargar clip
     const clipBuffer = await axios.get(clipUrl, { responseType: 'arraybuffer' });
     
     // Upload a TikTok
     const uploadResponse = await axios.post(
       `https://open.tiktokapis.com/v1/video/upload/`,
       clipBuffer,
       {
         headers: {
           'Authorization': `Bearer ${user.tiktok_access_token}`,
           'Content-Type': 'application/octet-stream',
         },
       }
     );
     
     const { upload_id } = uploadResponse.data;
     
     // Crear draft post
     const publishResponse = await axios.post(
       `https://open.tiktokapis.com/v1/video/publish/`,
       {
         upload_id,
         description: title,
         disable_comment: false,
         disable_duet: false,
         disable_stitch: false,
       },
       {
         headers: {
           'Authorization': `Bearer ${user.tiktok_access_token}`,
         },
       }
     );
     
     res.json({ status: 'published', video_id: publishResponse.data.video_id });
   });
   ```

**Tiempo:** 6-8 horas  
**Resultado:** Puedes publicar en TikTok automáticamente

---

#### Paso 3.2: Instagram + YouTube + LinkedIn (Día 13)

Mismo patrón que TikTok para:
- Instagram Graph API (para Reels)
- YouTube Shorts API
- LinkedIn Share API

**Referencia:** Cada plataforma tiene docs. Implementar en paralelo.

**Tiempo:** 12-16 horas (3-4 horas por plataforma)  
**Resultado:** 4 plataformas de publicación automática

---

### Semana 4: Polish MVP + Beta Launch

#### Paso 4.1: Conectar Frontend a Backend (Día 15-16)
En Framer, crear componentes que llamen:
- POST /api/upload (sube video)
- GET /api/videos (lista videos del usuario)
- POST /api/publish (publica a todas las redes)

Usar fetch() + axios para llamadas HTTP.

**Tiempo:** 3-4 horas

---

#### Paso 4.2: Setup Autenticación (Día 17)
- [ ] Crear /auth/signup endpoint
- [ ] Crear /auth/login endpoint
- [ ] Usar JWT tokens para sesiones
- [ ] Guardar token en localStorage (frontend)

```javascript
app.post('/auth/signup', async (req, res) => {
  const { email, password } = req.body;
  
  // Validar
  if (!email || !password) return res.status(400).json({ error: 'Missing fields' });
  
  // Hash password
  const hashedPassword = await bcrypt.hash(password, 10);
  
  // Crear usuario
  const user = await db.users.create({
    email,
    password_hash: hashedPassword,
    plan: 'free',
  });
  
  // Generar JWT
  const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET);
  
  res.json({ token, user });
});
```

**Tiempo:** 2-3 horas

---

#### Paso 4.3: Stripe Integration (Día 18)
- [ ] Crear checkout page para Starter ($29)
- [ ] Crear checkout page para Pro ($79)
- [ ] Setup webhooks (payment_intent.succeeded, invoice.paid)
- [ ] Actualizar plan en BD cuando pago exitoso

```javascript
// POST /create-checkout
app.post('/create-checkout', async (req, res) => {
  const { plan } = req.body; // 'starter' o 'pro'
  const user = req.user;
  
  const prices = {
    starter: process.env.STRIPE_PRICE_STARTER,
    pro: process.env.STRIPE_PRICE_PRO,
  };
  
  const session = await stripe.checkout.sessions.create({
    customer_email: user.email,
    line_items: [
      {
        price: prices[plan],
        quantity: 1,
      },
    ],
    mode: 'subscription',
    success_url: `${process.env.APP_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.APP_URL}/pricing`,
  });
  
  res.json({ url: session.url });
});
```

**Tiempo:** 4-5 horas

---

#### Paso 4.4: Beta Invite (Día 19-20)
- [ ] Crear lista de 20-30 beta testers (amigos, colegas, comunidad)
- [ ] Enviar invites privadas
- [ ] Setup form feedback (Google Form o Typeform)
- [ ] Monitorear errores en logs (Sentry)

**Tiempo:** 2-3 horas

---

#### Paso 4.5: Documentación Mínima (Día 21)
- [ ] Crear README.md con setup instructions
- [ ] Video tutorial 3 minutos (Loom)
- [ ] Documentación API básica

**Resultado:** MVP Completo, listo para beta testers

---

## FASE 2: LAUNCH PÚBLICO (Semanas 5-8)

### Semana 5: Feedback + Iteraciones Rápidas

**Input:** Feedback de beta testers  
**Output:** Fixes de bugs críticos, mejoras UX  

**Tareas:**
- [ ] Daily standup con feedback
- [ ] Prioritizar bugs vs features
- [ ] Lanzar hotfixes en 24-48 horas
- [ ] Actualizar producto based on learnings

---

### Semana 6: Polish UI + Crear Contenido

#### Paso 6.1: Mejorar Dashboard (Día 22-24)
- [ ] Agregar status indicator (processing animation)
- [ ] Mostrar clips generados en galería
- [ ] Dark mode toggle
- [ ] Mobile responsive

**Tiempo:** 4-5 horas

#### Paso 6.2: Crear Contenido Marketing (Día 25-27)
- [ ] 3 videos tutoriales (YouTube)
- [ ] 5 case studies (blog)
- [ ] Landing page SEO-friendly
- [ ] Copywrites persuasivos en pricing

**Tiempo:** 8-10 horas

---

### Semana 7: Launch Público + Product Hunt

#### Paso 7.1: Preparar Product Hunt (Día 28-30)
- [ ] Crear página PH
- [ ] Escribir descripción convincente
- [ ] Preparar 5 screenshots
- [ ] Video demo 2-3 minutos
- [ ] Reclutar 50-100 upvoters para el día 1

**Tiempo:** 6-8 horas

#### Paso 7.2: Lanzar en Redes Sociales (Día 31)
- [ ] Tweet anuncio
- [ ] Reddit post en /r/SaaS, /r/Entrepreneurs
- [ ] LinkedIn post (si tienes network)
- [ ] Discord communities

**Resultado:** 100-300 usuarios en el primer mes

---

### Semana 8: Primeros Pagos + Onboarding

#### Paso 8.1: Email Onboarding (Día 32-35)
Secuencia de 7 emails:
1. Welcome + primeros pasos
2. "Arriba tu primer video"
3. "Mira tu clip generado"
4. "Publíca en TikTok"
5. "Aquí va a ganar dinero"
6. "Plan Starter es para ti si..."
7. "Oferta limitada: 40% descuento mes 1"

**Time to implement:** 3-4 horas (usar Mailgun API)

#### Paso 8.2: Community (Día 36)
- [ ] Crear Discord privado
- [ ] Invitar primeros 100 usuarios
- [ ] Crear canales: #general, #feature-requests, #wins
- [ ] Moderar activamente

**Resultado:** 50+ usuarios pagos, $1.5k MRR

---

## FASE 3: DIFERENCIACIÓN (Semanas 9-12)

### Semana 9: Analytics Avanzados

#### Paso 9.1: Dashboard de Virality Scores (Día 37-40)
Mostrar en dashboard:
- Virality score por plataforma
- Predicción: "Este clip funcionará 5x mejor en TikTok"
- Trending hashtags sugeridos

**Implementación:**
```javascript
// GET /api/videos/:id/insights
app.get('/api/videos/:id/insights', async (req, res) => {
  const video = await db.videos.findById(req.params.id);
  
  res.json({
    viral_scores: {
      tiktok: video.viral_score_tiktok,
      reels: video.viral_score_reels,
      shorts: video.viral_score_shorts,
      linkedin: video.viral_score_linkedin,
    },
    best_platform: 'tiktok', // El que tiene score más alto
    recommendation: 'Publica primero en TikTok a las 7pm',
    predicted_reach: 50000, // Estimación basada en audiencia histórica
  });
});
```

**Time:** 6-8 horas

---

### Semana 10: Auto-publish (Sin Revisión Manual)

#### Paso 10.1: Publicación Automática Pro+ (Día 41-44)
Para usuarios Plan Pro+, agregar toggle:
- "Publicar automáticamente sin revisión"
- Cuando activado, clips se publican 5 segundos después de generados

**Implementación:**
```javascript
// En Make.com flujo:
// IF user.plan === 'pro' AND user.auto_publish === true
// THEN publish to all platforms immediately
// ELSE publish as draft (usuario revisa)
```

**Time:** 4-5 horas

---

### Semana 11: Localización (20+ Idiomas)

#### Paso 11.1: Multi-idioma Captions (Día 45-48)
Agregar en form:
- Selector de idioma destino (Spanish, French, Portuguese, etc)
- Auto-genera captions en ese idioma
- Usar DeepL para traducción de alta calidad

```javascript
// POST /api/captions/generate
app.post('/api/captions/generate', async (req, res) => {
  const { clipUrl, transcript, targetLanguage } = req.body;
  
  // Traducir transcript
  const translatedText = await deepl.translateText(
    transcript,
    'EN', // source
    targetLanguage.toUpperCase() // target
  );
  
  // Generar audio (TTS)
  const audioUrl = await elevenlabs.textToSpeech(
    translatedText,
    { language: targetLanguage }
  );
  
  // Agregar captions al video
  // (usar ffmpeg)
  
  res.json({ captioned_clip_url });
});
```

**Time:** 8-10 horas

---

### Semana 12: Case Studies + Partnerships

#### Paso 12.1: Crear 5 Case Studies (Día 49-52)
Entrevistar 5 primeros usuarios Pro+ y escribir:
- "Cómo [Name] escaló sus redes generando 3x más content"
- ROI: "Ahorró 20 horas/mes"
- Métrica: "Genera $5k/mes desde clips"

**Publicar en blog, incluir en landing page**

#### Paso 12.2: Partnerships (Día 53-56)
- [ ] Contactar 10 agencias digitales
- [ ] Proponer: "Te doy acceso Agency plan gratis 3 meses a cambio de testimonial + referral"
- [ ] Objetivo: 3-5 agencias usando tu producto

**Resultado:** 150-200 usuarios, $4-5k MRR

---

## FASE 4: ENTERPRISE & API (Semanas 13-16)

### Semana 13: Plan Agency + Multi-seat

#### Paso 13.1: Crear Plan Agency ($199/mes) (Día 57-60)
Agregar en Stripe:
- Precio $199/mes
- Feature: unlimited users + custom workspace

En BD:
```sql
ALTER TABLE users ADD COLUMN team_id UUID;
CREATE TABLE teams (
  id UUID PRIMARY KEY,
  owner_id UUID REFERENCES users(id),
  name VARCHAR(255),
  plan VARCHAR(50) DEFAULT 'agency',
  stripe_subscription_id VARCHAR(255)
);
CREATE TABLE team_members (
  id UUID PRIMARY KEY,
  team_id UUID REFERENCES teams(id),
  user_id UUID REFERENCES users(id),
  role VARCHAR(50) DEFAULT 'member'
);
```

**Time:** 5-6 horas

---

### Semana 14: API Pública v1

#### Paso 14.1: Documentar API (Día 61-64)
Crear docs para:
- POST /api/videos/process (procesa video)
- GET /api/videos/:id (obtiene status)
- POST /api/publish (publica a plataforma)

Usar OpenAPI/Swagger:
```yaml
openapi: 3.0.0
info:
  title: Repurposing SaaS API
  version: 1.0.0
paths:
  /api/videos/process:
    post:
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                video_url:
                  type: string
                platforms:
                  type: array
                  items:
                    type: string
```

**Publicar en:** https://docs.yourapp.com

**Time:** 4-5 horas

---

### Semana 15-16: White-label + Zapier

#### Paso 15.1: White-label Option (Día 65-70)
Agregar en settings para Agency plan:
- Custom domain (tudominio.com)
- Custom logo + colors
- Custom email "from" address

#### Paso 15.2: Listado Zapier (Día 71-75)
- [ ] Crear app en Zapier
- [ ] Definir triggers: "Video procesado"
- [ ] Definir actions: "Publicar en X plataforma"
- [ ] Enviar a Zapier para aprobación

**Resultado:** 250+ usuarios, $8-10k MRR, 3-5 agencias usando API

---

## FASE 5: INTELIGENCIA DE ROI (Semanas 17-20)

### Semana 17-18: Tracking de Conversiones

#### Paso 17.1: Integración Google Analytics (Día 76-84)
Para cada clip, trackear:
- Clicks URL (si está en descripción)
- Conversiones (pixel tracking)
- Revenue atribuible al clip

```javascript
// Generar tracking URL
const trackingUrl = `https://yourapp.com/track/${clipId}?destination=https://destination.com`;
// Incluir en descripción de clip automáticamente
```

**Time:** 6-8 horas

---

### Semana 19-20: Dashboard de ROI

#### Paso 19.1: Crear Panel ROI (Día 85-100)
Mostrar por usuario:
- "Generaste $X en ingresos desde tus clips"
- "Mejor performer: Este clip en LinkedIn"
- "Próximo mes, enfócate en Shorts"

**Resultado:** 350+ usuarios, $12-15k MRR, <5% churn

---

## FASE 6: SCALE (Semanas 21-26)

### Semana 21-22: Mobile App

#### Paso 21.1: React Native Setup (Día 101-110)
```bash
npx create-expo-app repurpose-mobile
npm install @react-navigation/native @react-native-async-storage/async-storage
```

Features:
- Upload video desde galería
- Ver status en tiempo real
- Publicar desde mobile

**Time:** 16-20 horas

---

### Semana 23-24: Marketplace

#### Paso 23.1: Crear Sistema de Templates (Día 111-128)
- Creator puede subir template de edición
- Otros users compran por $5-20
- Tú tomas 30% comisión

Implementar en BD + Stripe

**Time:** 12-16 horas

---

### Semana 25-26: Hiring + Final Polish

#### Paso 25.1: Contratar (Día 129-156)
- 1x Full-stack engineer ($3,000/mes)
- 1x Customer Success ($2,000/mes)

Esto te libera para:
- Strategy
- Sales (partnerships)
- Product direction

**Resultado:** 500+ usuarios, $22-25k MRR, $3k ingresos secundarios

---

## CHECKLIST DE DEPLOYMENT

### Antes de cada lanzamiento:
- [ ] Todos los tests pasan (npm test)
- [ ] No hay console.errors
- [ ] Logs monitoreados (Sentry)
- [ ] Backup de BD realizado
- [ ] Rollback plan ready

### Por semana:
- [ ] Pushear cambios a main
- [ ] Deploy automático via GitHub Actions
- [ ] Monitorear uptime (Uptime Robot)
- [ ] Revisar analytics (Posthog o Mixpanel)

---

## STACK FINAL DE COMANDOS

```bash
# Setup inicial
git clone repo
npm install
cp .env.example .env
npm run dev

# Deploy a Railway
git push origin main # Auto-deploy

# Monitoring
npm install -g pm2
pm2 start app.js --name "repurpose-api"
pm2 logs

# Testing
npm test
npm run lint
```

---

## MÉTRICAS A TRACKEAR DIARIAMENTE

- **Usuarios nuevos:** Target 5-10/día mes 3, 15-30/día mes 6
- **Videos procesados:** Target 20-50/día mes 3, 100-300/día mes 6
- **Conversion rate:** Target 8-12% (free → pago)
- **Churn rate:** Target <8% mes 3, <6% mes 6
- **API errors:** Target <0.5% (99.5% uptime)

---

## Próximo Paso

Comenzar **Semana 1: Paso 1.1** (crear cuentas)

**Tiempo total estimado:** 160-200 horas (6-8 semanas full-time)

