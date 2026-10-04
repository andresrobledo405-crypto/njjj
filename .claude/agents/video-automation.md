---
name: Video Automation Agent
description: Autonomous agent for fully automated video generation, editing, and publishing. Integrates AI models, professional tools, and multi-platform export.
model: claude-opus-5-5
interval: "0 * * * *"  # Run hourly
requires_approval: false
capabilities:
  - Autonomous video generation
  - AI model orchestration
  - Automated editing workflows
  - Quality assessment and retry
  - Multi-platform publishing
  - Performance monitoring
---

# Video Automation Agent

**Fully autonomous agent for end-to-end video production without manual intervention.**

## Core Features

### 1. Intelligent Job Queue
- Submit video concepts → auto-generate
- Priority-based processing
- Retry logic with exponential backoff
- Performance monitoring

### 2. Multi-Model Generation
- **Runway ML** - High-quality video synthesis
- **fal.ai** - Fast image→video generation
- **LTX Studio** - AI video enhancement
- **HyperFrames** - Local deterministic rendering
- **Automatic selection** based on prompt/config

### 3. Complete Production Pipeline

```
📋 Job Submission
    ↓
🧠 Prompt Optimization (Claude)
    ↓
🤖 Model Selection (Automatic)
    ↓
🎬 Video Generation (Multi-model)
    ↓
🔊 Audio Production (TTS + Music)
    ↓
🎞️ Compositing (FFmpeg)
    ↓
🎨 Color Grading (Skyreels/FFmpeg)
    ↓
✅ Quality Assessment (Auto)
    ↓
📱 Multi-Platform Export (5 formats)
    ↓
📊 Performance Report
```

### 4. API Integrations

| API | Capability | Status |
|-----|-----------|--------|
| **Runway ML** | Video generation | ✓ Ready |
| **fal.ai** | Image→video synthesis | ✓ Ready |
| **LTX Studio** | AI enhancement | ✓ Ready |
| **ElevenLabs** | Professional TTS | ✓ Ready |
| **Suno AI** | Music generation | ✓ Ready |
| **Skyreels** | Color grading | ✓ Ready |
| **Meta MusicGen** | Local music gen | ✓ Ready |
| **Festival/eSpeak** | Local TTS | ✓ Ready |

### 5. Output Formats

**Primary Export:**
- Base MP4 (H.264, CRF 14, 1080×1920)

**Platform Variants:**
- YouTube Shorts (1080×1920, 60s)
- TikTok (1080×1920, optimized FYP)
- Instagram Reels (1080×1920, auto-thumb)
- Facebook Video (1080×1920, mobile)
- Twitter/X (1080×1920, vertical)

## Usage

### Submit Job (Manual)

```bash
node video-automation-engine.js submit '{
  "prompt": "60-second viral video of animated eggs with baby animals",
  "narration": "¿Quién está dentro de los huevitos?",
  "music": "upbeat, playful, children friendly",
  "duration": 60,
  "quality": "high",
  "platforms": ["youtube", "tiktok", "instagram"]
}'
```

### Process Queue (Automated)

```bash
node video-automation-engine.js process
```

### Check Status

```bash
node video-automation-engine.js status <job-id>
node video-automation-engine.js jobs
node video-automation-engine.js report
```

## Automation Rules

### Processing Logic

1. **On Submit**: Job enters queue with status "queued"
2. **On Process**: Agent takes first job
3. **On Optimize**: Prompt enhanced with design best practices
4. **On Model Select**: Automatic selection based on input
5. **On Generate**: Video created with selected model
6. **On Audio**: Narration + music synthesized & mixed
7. **On Composite**: Video + audio combined
8. **On Grade**: Color correction applied
9. **On Export**: 5 platform variants created
10. **On Assess**: Quality scored (80-100 scale)
11. **On Retry**: If score < 85, try different model
12. **On Complete**: Results stored, job marked "completed"

### Retry Policy

```
Attempt 1: Primary model (Runway/LTX)
  ↓ (if quality < 85)
Attempt 2: Secondary model (fal.ai)
  ↓ (if quality < 85)
Attempt 3: Tertiary model (HyperFrames)
  ↓ (if quality < 85)
→ Manual review required
```

## Scheduling

### Automatic Execution

**Hourly Processing:**
```
0 * * * *  # Check queue every hour
```

**Triggers:**
- Manual submission via `/submit-video` command
- GitHub webhook (push to video/* files)
- Scheduled batch generation (daily/weekly)
- API endpoint (external callers)

## Configuration

### Environment Variables

```bash
# AI Video Generation
RUNWAYML_API_SECRET=sk_...
FAL_KEY=...
LTX_STUDIO_KEY=...

# Audio
ELEVENLABS_API_KEY=...
SUNO_API_KEY=...

# Processing
HYPERFRAMES_PYTHON=/usr/bin/python3
FFMPEG_CRF=14
FFMPEG_PRESET=slow
MAX_CONCURRENT_JOBS=3
MAX_RETRIES=3
QUALITY_THRESHOLD=85
```

### Log Files

All logs written to `logs/video-engine-YYYY-MM-DD.log`

Example entry:
```json
{
  "timestamp": "2024-10-02T14:30:45.123Z",
  "level": "success",
  "message": "Job completed successfully",
  "data": {
    "jobId": "job_1725270000000",
    "videoPath": "/exports/youtube_1725270000000.mp4",
    "quality": 92,
    "variants": ["youtube", "tiktok", "instagram", "facebook", "twitter"]
  }
}
```

## Performance Metrics

### Job Processing Time

| Phase | Time | Notes |
|-------|------|-------|
| Prompt optimization | 2-5s | Claude processing |
| Model selection | 1s | Scoring algorithm |
| Video generation | 60-180s | Depends on API |
| Audio generation | 15-30s | TTS + music |
| Compositing | 30-60s | FFmpeg |
| Color grading | 20-40s | FFmpeg filters |
| Export (5 variants) | 60-120s | Parallel possible |
| Quality assessment | 5-10s | Analysis |
| **Total** | **3-7 min** | Single job |

### Throughput

- **Sequential**: ~1 job per 5 minutes
- **With parallel exports**: ~1 job per 4 minutes
- **Daily capacity**: 288-432 videos (24h)

## Monitoring

### Metrics Tracked

```javascript
{
  totalJobs: 1247,
  successfulJobs: 1198,
  failedJobs: 49,
  averageQuality: 88.3,
  averageProcessTime: 5.2, // minutes
  topModels: {
    runway: 542,
    fal: 389,
    ltx: 267,
    hyperframes: 0
  },
  platformDistribution: {
    youtube: 1247,
    tiktok: 1247,
    instagram: 1198,
    facebook: 1156,
    twitter: 891
  }
}
```

### Dashboard

Generate reports:
```bash
node video-automation-engine.js report
```

## Error Handling

### Common Issues & Recovery

| Error | Cause | Solution |
|-------|-------|----------|
| API rate limit | Too many requests | Queue management + backoff |
| Video quality low | Poor prompt | Re-optimize + retry |
| Audio sync issue | Timing mismatch | Recalculate + recompose |
| Export failure | FFmpeg error | Fallback codec/bitrate |
| Out of storage | Disk full | Auto-cleanup old renders |

### Automatic Cleanup

```bash
# After each job:
rm -rf renders/* (temp files)
rm -rf assets/*-cache* (old cache)
find logs -mtime +30 -delete (old logs)
```

## Examples

### Example 1: Viral TikTok Series

```bash
# Submit 5 similar videos
for i in {1..5}; do
  node video-automation-engine.js submit "{
    \"prompt\": \"Episode $i: animated egg surprise\",
    \"platform\": \"tiktok\",
    \"quality\": \"high\"
  }"
done

# Process all
node video-automation-engine.js process
```

### Example 2: YouTube Series with Scheduling

```bash
# Create weekly automation
# (Would integrate with Cron)
0 8 * * MON  node video-automation-engine.js process
0 8 * * WED  node video-automation-engine.js process
0 8 * * FRI  node video-automation-engine.js process
```

### Example 3: Production Pipeline

```bash
# 1. Submit concept
node video-automation-engine.js submit '{
  "prompt": "60-second story about...",
  "narration": "Spanish voiceover",
  "style": "vibrant, energetic, viral"
}'

# 2. Automated processing
# (agent runs hourly or on-demand)

# 3. Generate report
node video-automation-engine.js report

# 4. Publish to platforms
# (via publish-to-*.sh scripts)
```

## Integration with GitHub Actions

```yaml
name: Auto-Generate Videos

on:
  schedule:
    - cron: '0 * * * *'  # Hourly
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: node video-automation-engine.js process
      - run: node video-automation-engine.js report
      - uses: actions/upload-artifact@v3
        with:
          name: exports
          path: exports/
```

## Next Steps

1. Configure API keys in `.env`
2. Submit first job: `node video-automation-engine.js submit '...'`
3. Process queue: `node video-automation-engine.js process`
4. Monitor: `node video-automation-engine.js report`
5. Publish results to platforms

---

**Video Automation Agent active. Ready for fully autonomous production.**
