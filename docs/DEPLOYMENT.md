# Deployment Guide - Repurpose AI SaaS

## Production Checklist

- [ ] Supabase project created and configured
- [ ] PostgreSQL schema deployed (see SUPABASE_SETUP.md)
- [ ] Stripe account in production mode
- [ ] Claude API key generated
- [ ] AWS S3 or Cloudinary account configured
- [ ] Railway account created
- [ ] GitHub Actions secrets configured

## Railway Deployment

### 1. Create Railway Project

```bash
# Login to Railway
railway login

# Create project
railway init --name repurpose-saas-prod
```

### 2. Configure Environment Variables

In Railway dashboard, add environment variables:

```
PORT=3001
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGc...
JWT_SECRET=<strong-random-32-char-secret>
CLAUDE_API_KEY=sk-ant-...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PRICE_STARTER=price_xxx
STRIPE_PRICE_PRO=price_xxx
FRONTEND_URL=https://repurpose-saas.com
```

### 3. Deploy

```bash
# Push code
git push origin main

# Railway auto-deploys on push (if connected to GitHub)
# Or manual deploy:
railway up
```

### 4. Verify Deployment

```bash
# Check logs
railway logs

# Test API
curl https://repurpose-saas-prod.up.railway.app/health
```

## GitHub Actions CI/CD

Workflows run on every push to `main` or `claude/**` branches:

1. **Test** - Run test suite
2. **Security** - Scan for secrets
3. **Deploy** - Auto-deploy to Railway on main branch
4. **Notify** - Report status

### Required Secrets in GitHub

Configure these in repository Settings → Secrets:

```
SUPABASE_URL
SUPABASE_KEY
JWT_SECRET
CLAUDE_API_KEY
STRIPE_PUBLISHABLE_KEY
STRIPE_SECRET_KEY
STRIPE_PRICE_STARTER
STRIPE_PRICE_PRO
RAILWAY_TOKEN
RAILWAY_PROJECT_ID
```

## Database Migration

### Initial Setup

```bash
# Run schema in Supabase SQL Editor
# See docs/SUPABASE_SETUP.md for full SQL

# Test connection
psql $SUPABASE_URL -U postgres -d postgres
```

### Backup

```bash
# Backup production database
pg_dump $SUPABASE_URL > backup-$(date +%Y%m%d).sql

# Restore
psql $SUPABASE_URL < backup-20261004.sql
```

## Monitoring & Logs

### Railway Logs
```bash
railway logs -f
```

### Sentry Integration (Optional)
```bash
# Add to .env
SENTRY_DSN=https://...@sentry.io/...

# Error tracking setup
# See https://sentry.io/for/node/
```

### Health Checks

- `/health` - Server status
- Monitored by: Railway, Uptime Robot (optional)

## Scaling

### Horizontal Scaling
- Railway: Add more instances (auto-scaling available)
- Load balancer: Railway handles this automatically

### Database Optimization
- Add Supabase read replicas for read-heavy queries
- Enable connection pooling in Supabase

## Security

### Production Checklist

- [ ] HTTPS enforced (automatic on Railway)
- [ ] Environment variables in Railway (not in code)
- [ ] Database backups automated
- [ ] Rate limiting configured
- [ ] CORS restricted to frontend domain
- [ ] Secrets rotated regularly
- [ ] Monitoring enabled

### HTTPS/TLS
- Railway provides automatic HTTPS via Let's Encrypt
- Configure custom domain in Railway settings

### Database Security
- Use Supabase RLS (Row-Level Security)
- Rotate JWT secret quarterly
- Enable database encryption

## Rollback

```bash
# If deployment fails
railway down

# Revert to previous commit
git revert <commit-hash>
git push origin main

# Railway auto-redeploys
```

## Cost Estimation (Monthly)

| Service | Cost | Notes |
|---------|------|-------|
| Supabase (Free tier) | $0 | 500MB DB, 2GB bandwidth |
| Railway (Hobby) | ~$5-15 | $5 credit + usage |
| Stripe | 2.9% + $0.30 | Transaction fees only |
| Claude API | $0/1M tokens | Pay as you go |
| AWS S3 | $0.023/GB | Video storage |
| **Total** | **~$10-30** | Varies by usage |

Scales to production pricing as traffic increases.

## Support

- Railway: https://railway.app/support
- Supabase: https://supabase.com/support
- Stripe: https://stripe.com/support
- Anthropic: https://support.anthropic.com

## Next Steps

1. Deploy MVP to production
2. Configure custom domain
3. Set up monitoring & alerts
4. Enable analytics
5. Plan scaling strategy
