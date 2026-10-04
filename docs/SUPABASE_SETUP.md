# Supabase Setup Guide

## Prerequisites

1. Create account at https://supabase.com
2. Create a new project (note the `SUPABASE_URL` and `SUPABASE_KEY`)
3. Go to Project Settings → API to find your keys

## Database Schema

Copy the following SQL and paste it into **Supabase SQL Editor**, then click **Run**:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  plan VARCHAR(50) DEFAULT 'free' CHECK(plan IN ('free', 'starter', 'pro', 'agency')),
  stripe_customer_id VARCHAR(255),
  stripe_subscription_id VARCHAR(255),
  videos_processed INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Videos table
CREATE TABLE videos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  title VARCHAR(255),
  original_url VARCHAR(2048),
  s3_path VARCHAR(2048),
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

-- Clips table
CREATE TABLE clips (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id UUID REFERENCES videos(id) ON DELETE CASCADE NOT NULL,
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

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_videos_user_id ON videos(user_id);
CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_clips_video_id ON clips(video_id);
CREATE INDEX idx_clips_platform ON clips(platform);

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE clips ENABLE ROW LEVEL SECURITY;

-- Policies: Users can only see their own data
CREATE POLICY "Users can read own row" ON users
  FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update own row" ON users
  FOR UPDATE USING (auth.uid()::text = id::text);

CREATE POLICY "Users can read own videos" ON videos
  FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can read own clips" ON clips
  FOR SELECT USING (
    video_id IN (SELECT id FROM videos WHERE user_id::text = auth.uid()::text)
  );
```

## Verification

After running the SQL:

1. Go to **Table Editor** in Supabase
2. Verify you see: `users`, `videos`, `clips` tables
3. Check each table has the correct columns

## Environment Configuration

Update your `.env` file with:
```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

Get these values from Supabase:
- Go to **Project Settings** → **API**
- Copy "Project URL" → `SUPABASE_URL`
- Copy "anon" public key → `SUPABASE_KEY`
- Copy "service_role" secret key → `SUPABASE_SERVICE_ROLE_KEY` (keep this secret!)

Done! Database is ready for the backend to connect.
