# Especificación de Diseño: Repurposing SaaS Automático

**Fecha:** 2026-10-04  
**Versión:** 1.0  
**Estado:** Diseño Completo (Listo para Implementación)  
**Público:** Multi-segmento (Agencias, Creators, Negocios, Medios)

---

## 1. RESUMEN EJECUTIVO

### Visión
Crear una plataforma SaaS que transforme **1 video largo en múltiples clips optimizados** para cada red social, con **publicación automática, analytics inteligentes y ROI medible** — todo sin requerer intervención manual ni conocimientos técnicos.

### Propuesta de Valor
- **Para Creators:** Genera 3-7 clips virales de 1 video en 30 segundos (vs 2-3 horas manual)
- **Para Agencias:** Escala contenido de clientes sin duplicar equipo creativo
- **Para E-commerce:** Reutiliza 1 producto/anuncio en 15 formatos optimizados
- **Para Medios:** Monitorea, recorta y distribuye menciones automáticamente

### Diferenciadores vs Competencia
1. **IA Multimodal** — Entiende contexto (no solo "detecta cambios de escena")
2. **Publicación Automática** — Sin revisión humana (vs OpusClip/Reap que requieren aprobación)
3. **ROI Medible** — Predice qué plataforma rendirá mejor con tu audiencia
4. **Precio Accesible** — $29-79/mes vs $200-500 de competidores
5. **API-First** — Para agencias que quieren integrar en sus herramientas

---

## 2. PROBLEMA & OPORTUNIDAD

### El Problema
- **46% de orgs inefectivas** a escala en repurposing contenido
- **Herramientas existentes fragmentadas:** OpusClip (solo clips), Runway (muy caro), Synthesia (solo avatares)
- **Proceso manual tedioso:** Upload → analizar → editar → optimizar por plataforma → publicar = 2-3 horas por video
- **Sin inteligencia de plataforma:** No saben si un clip funcionará mejor en TikTok o LinkedIn
- **Costo prohibitivo:** Herramientas decentes cuestan $500+/mes

### Oportunidad de Mercado
- **TAM (Total Addressable Market):** ~500k creadores + 50k agencias en LATAM + Global
- **SAM (Serviceable Market):** ~50k agencias + 200k creators "profesionales" que pagarían
- **SOM (Serviceable Obtainable Market):** 5-10% en 18 meses = 10-20k usuarios pagos = $10-20k MRR

---

## 3. SOLUCIÓN & ARQUITECTURA

### Flujo Principal del Producto

```
USUARIO SUBE VIDEO
        ↓
    Make.com Webhook
        ↓
Claude API (Analiza contenido)
        ↓
FFmpeg (Genera 3 versiones optimizadas)
        ↓
ElevenLabs (Auto-captions + traducción)
        ↓
Publicación Automática en TikTok, Instagram, YouTube, LinkedIn
        ↓
Supabase (Registra métricas)
        ↓
Dashboard: Usuario ve analytics en tiempo real
```

### Stack Tecnológico (No-Code + Low-Code)

| Capa | Herramienta | Propósito | Costo | Notas |
|---|---|---|---|---|
| **Frontend** | Framer / Webflow | UI/UX, landing page | $0-20/mes | Drag & drop, no código |
| **Orquestación** | Make.com | Automatiza flujos | $10-99/mes | La "columna vertebral" |
| **IA Análisis** | Claude API | Entiende contexto | $0.01-0.50/video | Por tokens consumidos |
| **Video Processing** | FFmpeg + Node.js | Genera clips | $7-30/mes | Railway / Render |
| **Captions/Traducción** | DeepL API + ElevenLabs | Localización | $0.002-0.05/video | Por caracteres/minutos |
| **Publicación** | APIs nativas (TikTok, IG, YouTube, LinkedIn) | Post automático | $0 | Requiere OAuth |
| **Base de Datos** | Supabase (PostgreSQL) | Guardar datos | $0-25/mes | Escalable |
| **Hosting** | Railway / Render | Node.js server | $7-30/mes | Para FFmpeg |
| **Pagos** | Stripe | Billing | $0.29 + 2.2% | Por transacción |

**Costo Total Mes 1:** $67/mes  
**Costo Total Mes 6 (escalado):** $405/mes  
**Margen por Usuario (Plan Starter $29):** $29 - $1.35 (costo actual) = **$27.65 ganancias por usuario/mes**

---

## 4. DETALLE TÉCNICO POR COMPONENTE

### 4.1 Frontend (Interfaz de Usuario)

**Plataforma:** Framer (React visual)  
**Páginas Principales:**
1. **Landing Page** — Hero + CTA + Testimonios + Pricing
2. **Dashboard Autenticado** — Área de usuario después de login
3. **Upload Area** — Drag & drop de video
4. **Clips Preview** — Muestra 3 versiones generadas
5. **Analytics** — Views, likes, shares por clip/plataforma
6. **Settings** — Conectar redes sociales (OAuth)

**Funcionalidades Críticas:**
- Upload de video (soporta MP4, MOV, WebM hasta 2GB)
- Live preview mientras procesa (status: "Analizando..." → "Generando clips..." → "Listo!")
- Gallery de clips generados (thumbnail + metadata)
- 1-click "Publicar en todas las plataformas"
- Métricas actualizadas cada 5 minutos
- Dark mode + responsive mobile

**Tiempo de desarrollo:** 2-3 semanas  
**Mantenimiento:** Bajo (Framer maneja hosting + SSL)

---

### 4.2 Orquestación (Make.com)

**El cerebro del sistema.** Make.com conecta todos los servicios en un flujo automatizado.

**Flujo Principal:**
```
Trigger: Webhook (usuario sube video)
  ↓
Step 1: Guardar archivo en Supabase Storage
  ↓
Step 2: Extraer primeros 30 segundos de audio (ffmpeg)
  ↓
Step 3: Enviar a Claude Vision → Analizar contenido
    Input: Frames clave + transcripción
    Output: Tema, virality_score, best_moment, hashtags
  ↓
Step 4: Decisión condicional
    ¿virality_score > 5/10? 
    NO → Notificar usuario "contenido muy bajo"
    SÍ → Continuar
  ↓
Step 5: Llamar Node.js FFmpeg service
    Input: Video, best_moment, plataformas seleccionadas
    Output: 3 clips (TikTok, Reels, Shorts)
  ↓
Step 6: Generar captions con DeepL + ElevenLabs
    Para cada clip → traducir a 5 idiomas
  ↓
Step 7: Publicar en APIs nativas
    TikTok API → POST draft
    Instagram Graph API → POST a Reels
    YouTube API → Upload a Shorts
    LinkedIn API → POST
  ↓
Step 8: Actualizar Supabase con URLs publicadas
  ↓
Step 9: Enviar email al usuario "¡Tus 3 clips están live!"
  ↓
Step 10: Setup webhook para recibir métricas cada hora
```

**Configuración Make.com:**
- Paso 3 (Claude): 1 llamada = $0.01-0.05 costo
- Paso 5 (FFmpeg): 1 llamada = $0.50-2.00 costo (variable por duración)
- Paso 6 (Captions): 3 clips × 3 idiomas = 9 llamadas = $0.01-0.10 costo
- **Costo total por video:** $0.50-2.15 USD

**Tiempo de setup:** 3-4 semanas

---

### 4.3 Análisis con Claude API

**Qué hace:**
Analiza el video y entrega insights que hacen el sistema "inteligente".

**Prompt del Sistema:**
```
"Eres un experto en contenido viral. Analiza este video.

Información:
- Frames: [primeros 10 frames clave del video]
- Audio transcripción: [transcripción de audio extraída]
- Duración: [Xs]
- Tema: [detectado automáticamente]

Tareas:
1. Identifica el "momento más inesperado" (el hook)
2. Calcula virality score 1-10 para:
   - TikTok (Gen Z, viral, entretenimiento)
   - Instagram Reels (polished, aspiracional)
   - YouTube Shorts (educativo, informativo)
   - LinkedIn (profesional, B2B)
3. Propón 5 hashtags emergentes
4. Recomienda duración ideal por plataforma
5. Identifica si necesita subtítulos forzados

Responde en JSON:
{
  'viral_score': {
    'tiktok': 8,
    'reels': 6,
    'shorts': 7,
    'linkedin': 3
  },
  'best_moment': {
    'timestamp': '00:45-01:15',
    'reason': 'El CEO dice algo controversial'
  },
  'hashtags': ['#SaaS', '#Startup', ...],
  'needs_captions': true
}
"
```

**Costo:** ~$0.02-0.05 por video (depende de duración + tokens)  
**Tiempo de respuesta:** 3-5 segundos

---

### 4.4 Video Processing (FFmpeg)

**Qué hace:**
Transforma 1 video en múltiples formatos optimizados.

**Node.js Endpoint (en Railway/Render):**
```javascript
POST /api/process-video
Body: {
  video_url: "https://...",
  best_moment: "00:45-01:15",
  platforms: ["tiktok", "reels", "shorts"]
}

Response: {
  clips: [
    { platform: "tiktok", url: "s3://...", duration: 45 },
    { platform: "reels", url: "s3://...", duration: 60 },
    { platform: "shorts", url: "s3://...", duration: 50 }
  ]
}
```

**Transformaciones por Plataforma:**
- **TikTok:** 1080×1920 (9:16), 15-60s, 30fps
- **Reels:** 1080×1920 (9:16), 15-90s, 30fps
- **Shorts:** 1080×1920 (9:16), 15-60s, 30fps

**Agrega automáticamente:**
- Captions duros (hardcoded en el video)
- Watermark (opcional, configurable)
- Efectos de transición suave (1-2 seg)
- Normalización de audio (-3dB)

**Costo:** $0.50-2/video (depende de duración)  
**Tiempo:** 30-120 seg por video

---

### 4.5 Publicación Automática (APIs Nativas)

**Cada plataforma requiere autenticación OAuth 1 sola vez.**

| Plataforma | API Usado | Status Final |
|---|---|---|
| TikTok | v1/video/publish | Draft (usuario puede revisar antes de publicar) |
| Instagram | graph/v20.0/me/media | Programado para mañana 10am |
| YouTube | youtube/v3/videos | Draft en Studio |
| LinkedIn | v2/ugcPosts | Publicado inmediatamente |
| Twitter/X | v2/tweets | Publicado inmediatamente |

**Nota Importante:** Todas son publicaciones DRAFT excepto LinkedIn y X, para que el usuario revise antes de ir en vivo (completa automatización en Pro+).

**Tiempo de setup APIs:** 2-3 semanas (requiere verificación con cada plataforma)

---

### 4.6 Base de Datos (Supabase)

**Estructura de Datos:**

```sql
-- Tabla: users
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  plan VARCHAR ('free', 'starter', 'pro', 'agency'),
  stripe_customer_id VARCHAR,
  videos_processed INT DEFAULT 0,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Tabla: videos
CREATE TABLE videos (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  original_url VARCHAR,
  title VARCHAR,
  duration INT,
  status VARCHAR ('uploaded', 'processing', 'ready', 'error'),
  viral_score_tiktok DECIMAL,
  viral_score_reels DECIMAL,
  viral_score_shorts DECIMAL,
  viral_score_linkedin DECIMAL,
  best_moment_start INT,
  best_moment_end INT,
  created_at TIMESTAMP
);

-- Tabla: clips
CREATE TABLE clips (
  id UUID PRIMARY KEY,
  video_id UUID REFERENCES videos(id),
  platform VARCHAR ('tiktok', 'reels', 'shorts', 'linkedin'),
  clip_url VARCHAR (S3),
  published_url VARCHAR,
  duration INT,
  status VARCHAR ('draft', 'published', 'scheduled'),
  views INT,
  likes INT,
  shares INT,
  sync_date TIMESTAMP
);

-- Tabla: analytics
CREATE TABLE analytics (
  id UUID PRIMARY KEY,
  clip_id UUID REFERENCES clips(id),
  metric_date DATE,
  views INT,
  likes INT,
  shares INT,
  clicks INT,
  engagement_rate DECIMAL,
  updated_at TIMESTAMP
);
```

**Costo:** Supabase free tier hasta 500MB, luego $25/mes  
**Escalabilidad:** Soporta millones de registros

---

## 5. MODELO DE NEGOCIO

### 5.1 Estructura de Precios

```
FREE TIER (Siempre Gratis)
├─ 3 videos/mes
├─ 1 plataforma
├─ Sin analytics
├─ Válido 30 días
└─ Límite: 1 video/semana

STARTER ($29/mes)
├─ 30 videos/mes
├─ 3 plataformas simultáneas
├─ Analytics básicos (views, likes)
├─ Captions en 3 idiomas
├─ Publicación = draft (revisión manual)
└─ Soporte: Email

PRO ($79/mes)
├─ 100 videos/mes
├─ 5+ plataformas
├─ Analytics completos (ROI estimado)
├─ Captions en 20+ idiomas
├─ Publicación automática SIN revisión
├─ Templates inteligentes
├─ Scheduling por zona horaria
└─ Soporte: Chat 24/7

AGENCY ($199/mes)
├─ Hasta 500 videos/mes
├─ Usuarios ilimitados (multi-seat)
├─ API access (webhooks + custom)
├─ White-label (tu logo, dominio)
├─ Integración Zapier/Make.com
├─ Gestor de cuenta dedicado
└─ SLA: 99.9% uptime
```

### 5.2 Proyecciones de Ingresos

#### **Mes 3: Early Traction**
- Usuarios: 150-200
- Mix: 40% Free, 45% Starter ($29), 12% Pro ($79), 3% Agency ($199)
- **MRR Proyectado:**
  ```
  Starter: 90 × $29 = $2,610
  Pro: 24 × $79 = $1,896
  Agency: 6 × $199 = $1,194
  ──────────────────────
  TOTAL MRR: $5,700
  Churn: ~8-10% (normal SaaS early stage)
  ```
- **Ingresos Secundarios:** $500 (partnerships)
- **Total Mes 3:** ~$5,700 MRR

#### **Mes 6: Scaling**
- Usuarios: 450-500
- Mix: 35% Free, 40% Starter, 20% Pro, 5% Agency
- **MRR Proyectado:**
  ```
  Starter: 200 × $29 = $5,800
  Pro: 100 × $79 = $7,900
  Agency: 25 × $199 = $4,975
  ──────────────────────
  TOTAL MRR: $18,675
  Churn: ~5-6% (mejor retención, producto maduro)
  ```
- **Ingresos Secundarios:**
  - Marketplace de templates: $2,000
  - API usage (agencias): $1,500
  - White-label: $3,000
- **Total Mes 6:** ~$25,175 MRR

#### **Proyección Anual (Año 1)**
- **MRR End of Year:** $25-30k
- **ARR:** $300-360k
- **CAC (Customer Acquisition Cost):** $50-100
- **LTV (Lifetime Value):** $29 × 24 meses / 6% churn = $1,160
- **LTV/CAC Ratio:** 11-20x (excelente)

### 5.3 Canales de Adquisición

| Canal | Costo Mes | ROI | Escala |
|---|---|---|---|
| **Organic (SEO + Content)** | $0 | Indefinido | Lento pero predecible |
| **Product Hunt** | $0 | 100-200 usuarios día 1 | 1x anual |
| **Comunidades (Reddit, Twitter)** | $0 | 5-10% usuarios | Constante |
| **Partnerships (agencias)** | $500 | 2-3x ROI | 10-20 usuarios/mes |
| **Google Ads** | $500 | 2-3x ROI mes 3+ | 30-50 usuarios/mes |
| **YouTube Ads** | $300 | 1.5-2x ROI | 20-30 usuarios/mes |
| **Afiliados/Referrals** | $0 (20% comisión) | 3-5x ROI | 15-30 usuarios/mes |

**Presupuesto recomendado:**
- Mes 1-2: $0 (solo organic)
- Mes 3: $500 (Google Ads)
- Mes 4-6: $1,000/mes (Google + YouTube + partnerships)

---

## 6. ROADMAP: 6 MESES (26 SEMANAS)

### **FASE 1: MVP (Semanas 1-4)**
**Objetivo:** Demostrar concepto con beta testers

**Tareas:**
- [ ] Landing page (Framer)
- [ ] Setup Make.com flujo básico
- [ ] Integración Claude API
- [ ] FFmpeg endpoint (Node.js)
- [ ] TikTok API conexión
- [ ] Supabase schema
- [ ] Free tier setup (3 videos)
- [ ] Invitar 20 beta testers

**Resultado:** Producto funcional pero sin UI pulida  
**Métrica de Éxito:** 15/20 beta testers generan clip  
**Costo:** $67/mes  
**Tiempo estimado:** 4 semanas (1 persona)

---

### **FASE 2: Launch + Primeros Pagos (Semanas 5-8)**
**Objetivo:** Go-to-market y primeros 50 usuarios pagos

**Tareas:**
- [ ] Dashboard UI pulida (Framer)
- [ ] Planes Starter ($29) + Pro ($79)
- [ ] Stripe integration (pagos)
- [ ] Conectar 3 plataformas más (Instagram, YouTube, LinkedIn)
- [ ] Video tutoriales (5x 3-min)
- [ ] Product Hunt launch
- [ ] Email onboarding (secuencia 7 emails)
- [ ] Community setup (Discord)

**Resultado:** Primeros ingresos recurrentes, primeras métricas  
**Métrica de Éxito:** 50+ usuarios pagos, $1.5k MRR, <8% churn  
**Costo:** $100/mes (ads) + $67 operativo = $167/mes  
**Ingresos:** ~$1,500-2,000 MRR

---

### **FASE 3: Diferenciación (Semanas 9-12)**
**Objetivo:** Implementar el "moat" (ventaja competitiva)

**Tareas:**
- [ ] Analytics avanzados (virality score por plataforma)
- [ ] Publicación automática sin revisión (Pro+)
- [ ] Auto-captions en 5 idiomas (DeepL)
- [ ] Templates inteligentes ("detecta tema → sugiere estilo")
- [ ] Discord community moderado
- [ ] 5 case studies escritos
- [ ] Referral program (20% comisión recurrente)

**Resultado:** Diferenciador claro vs OpusClip, Runway, Reap  
**Métrica de Éxito:** 150+ usuarios, $4-5k MRR, <7% churn  
**Costo:** $200/mes (ops + ads)  
**Ingresos:** ~$4,500-5,500 MRR

---

### **FASE 4: Enterprise (Semanas 13-16)**
**Objetivo:** Lanzar plan Agency + API pública

**Tareas:**
- [ ] Plan Agency ($199/mes) con multi-usuario
- [ ] API pública (v1) + documentación
- [ ] Webhooks + integración Make.com/Zapier
- [ ] White-label option
- [ ] 10 testimonios video de usuarios
- [ ] Partnership program (agencias resellers)
- [ ] Listado en Zapier marketplace

**Resultado:** B2B + B2C revenue streams  
**Métrica de Éxito:** 250+ usuarios, $8-10k MRR, 3-5 agencias usando API  
**Costo:** $300/mes (ops + ads)  
**Ingresos:** ~$8,500-10,500 MRR

---

### **FASE 5: Intelligence (Semanas 17-20)**
**Objetivo:** Agregue IA predictiva de ROI

**Tareas:**
- [ ] Dashboard "Qué contenido funciona mejor"
- [ ] Recomendación de plataforma por tema
- [ ] Análisis de trending topics
- [ ] Scheduling inteligente (mejor hora por plataforma)
- [ ] Multi-idioma (5 lenguajes)
- [ ] Integración con Google Analytics (tracking ROI)
- [ ] 3 webinars educativos

**Resultado:** Users retienen porque ven ROI medible  
**Métrica de Éxito:** 350+ usuarios, $12-15k MRR, <5% churn  
**Costo:** $400/mes  
**Ingresos:** ~$13,500-16,000 MRR

---

### **FASE 6: Scale (Semanas 21-26)**
**Objetivo:** Mobile + Marketplace + Automatización total

**Tareas:**
- [ ] App móvil (React Native) upload on-the-go
- [ ] Marketplace de templates (30% comisión)
- [ ] Podcast workflow específico
- [ ] CRM integration (HubSpot, Pipedrive)
- [ ] Affiliate program (YouTube, Blogs)
- [ ] 2 hire (Customer Success + Engineer)

**Resultado:** Producto mature, multi-canal ingresos  
**Métrica de Éxito:** 500+ usuarios, $20-25k MRR, +$3k ingresos secundarios  
**Costo:** $600/mes + $4,000 (2 hires)  
**Ingresos:** ~$24,000 MRR (subscripciones) + $3,000 (otros)

---

## 7. MÉTRICAS DE ÉXITO

### Métricas de Producto
- **Activation Rate:** % de free users que generan primer clip = Target 60%
- **Conversion Rate:** % free → pago = Target 8-12%
- **Churn Rate:** % usuarios que cancelan = Target <7% mensual
- **NPS (Net Promoter Score):** Target >50 (excelente SaaS)

### Métricas de Negocio
- **MRR (Monthly Recurring Revenue):** $5.7k (mes 3) → $25k (mes 6)
- **CAC (Customer Acquisition Cost):** <$100 por cliente
- **LTV/CAC Ratio:** >10x
- **Payback Period:** <3 meses

### Métricas de Uso
- **Videos procesados/usuario/mes:** Target 15+ (vs 3 free tier)
- **Clips generados/video:** Target 3.5 promedio (TikTok + Reels + Shorts + LinkedIn)
- **Tasa de publicación:** % de clips publicados vs generados = Target 80%+

---

## 8. RIESGOS & MITIGACIÓN

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| **API rate limits** (Make.com/Claude) | Media | Alto | Pre-procesar, caching, escalar gradualmente |
| **Cambios en APIs** (TikTok, Instagram) | Baja | Muy Alto | Monitorear changelog, documentación, partnerships |
| **Competencia fuerte** (OpusClip escala) | Media | Alto | Diferenciador claro: IA + automatización |
| **Acquisition cost alto** | Media | Medio | Enfoque organic + partnerships agencias |
| **Churn por features incompletos** | Alta | Medio | Lanzar fast, feedback loop, actualizaciones bi-weekly |
| **Compliance/Copyright** (videos publicados) | Baja | Muy Alto | ToS claro, disclaimer, detectar contenido flagged |

---

## 9. STACK FINAL & COSTOS

### Desglose Mensual (Mes 6, Escalado)

| Herramienta | Costo | Justificación |
|---|---|---|
| Framer | $20 | Hosting + editor visual |
| Make.com | $99 | Orquestación automática |
| Claude API | $150 | 3,000 videos × $0.05 = $150 |
| FFmpeg (Railway) | $30 | Servidor Node.js |
| DeepL | $50 | Traducción de captions |
| ElevenLabs | $50 | TTS para captions |
| Supabase | $25 | Base de datos escalada |
| Stripe | $0.29 + 2.2% | Fees en pagos (no costo fijo) |
| Google Ads | $300 | Marketing (variable) |
| Misc (Slack, monitoring, etc) | $50 | Ops tools |
| **TOTAL** | **$774/mes** | Incluye marketing |

**Por Usuario Starter ($29/mes):**
- Costo: $1.35 (operativo) + $0.60 (marketing share) = $1.95
- Ganancia: $29 - $1.95 = **$27.05/usuario**

**Por Usuario Pro ($79/mes):**
- Costo: $3 (operativo) + $1.50 (marketing) = $4.50
- Ganancia: $79 - $4.50 = **$74.50/usuario**

---

## 10. PLAN DE IMPLEMENTACIÓN (Próxima Fase)

Ver documento: **"2026-10-04-repurposing-saas-implementation.md"** (creado después de esta especificación)

**Resumen:**
1. Semana 1: Setup cuentas (Make.com, Supabase, Claude, AWS S3)
2. Semana 2-3: Build Make.com flujo + FFmpeg endpoint
3. Semana 4: Frontend (Framer)
4. Semana 5-8: Launch + primeros usuarios
5. Semana 9+: Iteración rápida basada en feedback

---

## Aprobación

**Diseño Completo:** ✅  
**Listo para Implementación:** ✅  
**Próximo paso:** Plan de Implementación Detallado

