# 🚀 Repurpose AI - Production Launch Checklist

## Status: READY FOR DEPLOYMENT

### Pre-Launch Configuration

#### 1. Supabase Setup
```bash
# Create Supabase project
# Copy SUPABASE_URL and SUPABASE_KEY

# Run SQL schema
# See: docs/SUPABASE_SETUP.md
```

#### 2. Stripe Configuration
```bash
# Create Stripe account (production mode)
# Create products: Starter ($29) and Pro ($79)
# Get: STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY
# Get: STRIPE_PRICE_STARTER, STRIPE_PRICE_PRO
```

#### 3. Claude API
```bash
# Get API key from https://console.anthropic.com
# CLAUDE_API_KEY=sk-ant-...
```

#### 4. Railway Deployment
```bash
# 1. Create Railway project at railway.app
# 2. Connect GitHub repo
# 3. Set environment variables:

PORT=3001
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGc...
JWT_SECRET=<32-char-random-string>
CLAUDE_API_KEY=sk-ant-...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PRICE_STARTER=price_xxx
STRIPE_PRICE_PRO=price_xxx
FRONTEND_URL=https://yourdomain.com

# 4. Deploy: git push origin main (auto-deploys)
```

### Deployment Command
```bash
# Option 1: Railway CLI
railway login
railway link --project <PROJECT_ID>
railway up --service backend

# Option 2: GitHub Auto-Deploy
# Railway webhook on main branch push (configured in Railway dashboard)
```

### Post-Launch

#### API Health Check
```bash
curl https://repurpose-ai.railway.app/health
# Expected: {"status":"ok","timestamp":"2026-10-04T..."}
```

#### Test Sign-Up Flow
```bash
curl -X POST https://repurpose-ai.railway.app/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234"}'
# Expected: {"token":"eyJ..."}
```

#### Frontend Deployment
```bash
# Option 1: GitHub Pages
# Push /frontend to gh-pages branch

# Option 2: Netlify
# Connect /frontend directory to Netlify

# Option 3: Same server (Railway)
# Add static file serving to Express server
```

### Video Publishing
```bash
# 1. YouTube: Upload repurpose-promo-final.mp4
# 2. Twitter/X: Tweet video link
# 3. LinkedIn: Post to company page
# 4. Landing page: Embed video
```

---

## Timeline

**Day 1-2:** Configure Supabase + Stripe + Railway  
**Day 3:** Deploy backend + frontend  
**Day 4:** Launch landing page + social media campaign  
**Day 5:** Onboard first beta users  

---

## Revenue Model (Month 1-3)

| Metric | Target |
|--------|--------|
| Signups | 50 |
| Free → Starter conversion | 20% |
| Free → Pro conversion | 5% |
| MRR (Month 1) | $290 |
| MRR (Month 3) | $5,700 |

---

## Support
- Docs: `docs/SUPABASE_SETUP.md` + `docs/DEPLOYMENT.md`
- Code: `backend/` + `frontend/`
- Video: `video/repurpose-promo-final.mp4`

**Status: PRODUCTION-READY ✅**
