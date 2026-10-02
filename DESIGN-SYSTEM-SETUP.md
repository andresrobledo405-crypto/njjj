# 🎨 Design System Setup & Integration Guide

**Professional Video, Animation & Graphic Design Studio**  
Complete toolkit for creating viral content with integrated AI skills.

---

## 📋 Table of Contents

1. [Installation](#installation)
2. [Architecture](#architecture)
3. [Design Master Agent](#design-master-agent)
4. [Workflow Examples](#workflow-examples)
5. [Troubleshooting](#troubleshooting)
6. [Quick Reference](#quick-reference)

---

## 🚀 Installation

### Step 1: Run Setup Script

```bash
cd /home/user/njjj
bash setup-design-tools.sh
```

**What it installs:**
- ✅ Node.js 22+
- ✅ FFmpeg 7.0+ (video encoding)
- ✅ Python 3.10+ with ML libraries
- ✅ Project dependencies (Remotion, GSAP, etc.)
- ✅ Directory structure
- ✅ Environment configuration

### Step 2: Activate Python Environment

```bash
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

### Step 3: Verify Installation

```bash
npm run test:design
```

Expected output:
```
Node: v22.x.x
NPM: 10.x.x
Python: 3.10+
FFmpeg: N-7234 Copyright (c) 2000-2024 ...
✓ Design tools ready
```

---

## 🏗️ Architecture

### Three-Layer System

```
┌─────────────────────────────────────────┐
│     Design Master Agent (Orchestrator)  │
│  - Analyzes requirements                │
│  - Routes to appropriate skills         │
│  - Manages workflow                     │
└────────────┬────────────────────────────┘
             │
    ┌────────┴──────────┬──────────────┬──────────┐
    │                   │              │          │
┌───▼────┐         ┌────▼───┐   ┌─────▼──┐  ┌───▼───┐
│ Video  │         │ Motion │   │ Visual │  │ Audio │
│ Skills │         │ Skills │   │ Skills │  │ Skills│
└────────┘         └────────┘   └────────┘  └───────┘
  │                    │            │           │
  ├─ hyperframes    ├─ animate   ├─ impeccable ├─ TTS
  ├─ remotion       ├─ GSAP      ├─ design-taste├─ Music
  ├─ manim          ├─ Lottie    └─ branding   └─ SFX
  └─ ffmpeg         └─ Motion         UI
```

### Skill Categories

| Category | Skills | Use Case |
|----------|--------|----------|
| **Video** | hyperframes, remotion, manim, ffmpeg | Full video production |
| **Motion** | animate, GSAP, Lottie, emil-design-eng | UI animations, motion graphics |
| **Graphics** | impeccable, design-taste-frontend, high-end-visual-design | Visual design, branding |
| **Audio** | text-to-speech, music, sound-effects | Audio track creation |
| **Transform** | html-to-express, markdown-to-pdf | Format conversion |

---

## 🤖 Design Master Agent

### What It Does

The Design Master Agent is your **creative director** - it orchestrates all tools to create professional content seamlessly.

### Activation

```bash
# In Claude Code terminal
/design "Create a 60-second viral video with..."

# Or directly invoke skills
/hyperframes
/animate
/impeccable
```

### Agent Capabilities

✅ **Analysis** - Understands design briefs  
✅ **Planning** - Creates production roadmaps  
✅ **Execution** - Coordinates skill workflows  
✅ **QA** - Reviews output quality  
✅ **Export** - Generates platform-specific variants  

---

## 📚 Workflow Examples

### Example 1: Complete Video Production

**Goal:** 60-second viral video with 3D animation + voice + music

```
1. BRIEF
   "Create 60-second video: bouncing eggs → animals emerge → dance scene"
   
2. PLANNING (Design Master Agent)
   ✓ Format: 1080×1920 vertical, 60s, 30fps
   ✓ Video: hyperframes (best for 3D + animation)
   ✓ Audio: TTS (Spanish) + generated music
   ✓ Output: 4 platform variants
   
3. EXECUTION
   ✓ Animation frames: /hyperframes (Python PIL + FFmpeg)
   ✓ Voice: /text-to-speech (ElevenLabs or local)
   ✓ Music: /music (Suno or Meta MusicGen)
   ✓ Color grade: Skyreels API or FFmpeg filters
   
4. EXPORT
   ✓ YouTube Shorts (1080×1920)
   ✓ TikTok (1080×1920 + optimized metadata)
   ✓ Instagram Reels (1080×1920)
   ✓ Facebook (1080×1920 + mobile format)
```

### Example 2: Motion Graphics Sequence

**Goal:** Animated logo + transition effects

```
1. DESIGN
   /impeccable "Design animated logo for children's channel"
   → Creates visual direction
   
2. ANIMATION
   /text-to-lottie "Convert text 'Los Huevitos' to Lottie animation"
   → Generates .json animation
   
3. REFINEMENT
   /animate "Enhance motion with ease-out, stagger effects"
   /review-animations "QA check for smoothness"
   
4. INTEGRATION
   Embed Lottie in web player or export as video
```

### Example 3: Multi-Platform Optimization

**Goal:** Same 60s video for 5 platforms

```
1. MASTER EXPORT
   Source: huevitos_60s_final.mp4 (1.7 MB)
   
2. PLATFORM VARIANTS
   YouTube Shorts  → 1080×1920, 60s, CRF 14, title + tags
   TikTok          → 1080×1920, 60s, optimized for FYP
   Instagram       → 1080×1920, 60s, auto thumbnail
   Facebook        → 1080×1920, 60s, mobile-first
   Twitter/X       → 1080×1920, 60s, vertical
   
3. METADATA
   YouTube: "Los Huevitos Sorpresa - Canción Infantil Viral 🥚"
   TikTok:  #HuevitosVirales #CancionesInfantiles #BebesVirales
   IG:      Caption + hashtags + @mentions
   FB:      Title + description + link
```

---

## 🎯 Quick Commands

### Video Creation

```bash
# Full render with HyperFrames
npm run render:hyperframes

# Using Remotion (if React-based)
npm run render:remotion

# Export to all platforms
npm run export:all

# Export specific platform
npm run export:youtube
npm run export:tiktok
npm run export:instagram
```

### Testing & Verification

```bash
# Test all tools
npm run test:design

# Verify individual tools
npm run test:ffmpeg
npm run test:node
npm run test:python
```

### Development

```bash
# Start local server
npm run serve

# View in browser
open http://localhost:8080
```

---

## 🔧 Configuration

### Environment Variables (`video/.env`)

```bash
# Python for Kokoro TTS
HYPERFRAMES_PYTHON=python3

# Playwright (browser automation)
PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers

# Optional API Keys (for enhanced features)
RUNWAYML_API_SECRET=sk_...          # Video generation
FAL_KEY=...                         # fal.ai models
ELEVENLABS_API_KEY=...              # Premium TTS
SUNO_API_KEY=...                    # AI music generation

# Video encoding defaults
FFMPEG_CRF=14                       # Quality (14-18 = high)
FFMPEG_PRESET=slow                  # Encoding speed
VIDEO_BITRATE=8000k                 # Video bitrate
AUDIO_BITRATE=192k                  # Audio bitrate
```

### Directory Structure

```
/home/user/njjj/
├── video/                  # Video production scripts
├── assets/                 # Image, audio, data files
├── renders/                # Intermediate render outputs
├── exports/                # Final exports
├── vendor/                 # Third-party libraries (GSAP, etc)
├── scripts/                # Utility scripts
├── .claude/
│   ├── agents/
│   │   └── design-master.md   # Design orchestrator agent
│   └── skills/
└── package.json            # NPM configuration
```

---

## 📊 Performance Metrics

### Video Rendering Times

| Tool | Resolution | Duration | Time | Size |
|------|------------|----------|------|------|
| HyperFrames | 1080×1920 | 60s | 2-3 min | 1.1-2.5 MB |
| Remotion | 1080×1920 | 60s | 1-2 min | 1.2-2.0 MB |
| Manim | 1920×1080 | 10s | 30-60s | 300 KB |

### Quality Standards

- **Codec**: H.264 (MPEG-4)
- **CRF**: 14 (professional quality)
- **FPS**: 30
- **Audio**: AAC 192 kbps
- **Frame Size**: 1080×1920 (vertical)

---

## 🐛 Troubleshooting

### FFmpeg Not Found

```bash
# Linux
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Verify
ffmpeg -version
```

### Python Issues

```bash
# Ensure venv is activated
source venv/bin/activate

# Install missing packages
pip install kokoro-onnx soundfile torch transformers

# Verify Python
python3 --version
which python3
```

### Node/NPM Issues

```bash
# Check version (need 22+)
node -v
npm -v

# Update NPM
npm install -g npm@latest

# Clear cache
npm cache clean --force
npm install
```

### HyperFrames Rendering Fails

```bash
# Ensure Chromium path is correct
echo $PLAYWRIGHT_BROWSERS_PATH

# Fallback to default
export PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers

# Test render
npx hyperframes check
```

---

## 📖 Quick Reference

### Common Tasks

| Task | Command | Skill |
|------|---------|-------|
| Create video | `npm run create:video` | /hyperframes |
| Animate text | `npm run create:animation` | /text-to-lottie |
| Design graphics | `npm run create:graphics` | /impeccable |
| Add voice | TTS in pipeline | /text-to-speech |
| Generate music | `/music "children's upbeat"` | /music |
| Color grade | Skyreels API or FFmpeg | Skyreels |
| Export platform | `npm run export:tiktok` | FFmpeg |

### Skill Shortcuts

```bash
/animate              # Motion design
/impeccable           # Visual excellence
/design-taste-frontend # Style refinement
/hyperframes          # Video rendering
/text-to-lottie       # Text animations
/manim-composer       # Mathematical animations
/music                # Music generation
/text-to-speech       # Voice narration
```

---

## ✅ Setup Verification Checklist

- [ ] Setup script completed (`bash setup-design-tools.sh`)
- [ ] Node.js 22+ installed (`node -v`)
- [ ] FFmpeg installed (`ffmpeg -version`)
- [ ] Python venv activated (`source venv/bin/activate`)
- [ ] npm packages installed (`npm install`)
- [ ] .env file configured (`cat video/.env`)
- [ ] Design Master Agent active
- [ ] Test render successful (`npm run test:design`)
- [ ] Player HTML files in `/root/Desktop/`
- [ ] All skills available in `/` menu

---

## 🎬 Next Steps

1. **Activate Design Master**: Use `/design` for complex projects
2. **Try individual skills**: `/hyperframes`, `/animate`, `/impeccable`
3. **Run example pipeline**: Create a test 10-second animation
4. **Explore platform exports**: Generate variants for YouTube, TikTok
5. **Integrate APIs** (optional): Add ElevenLabs, Runway, Suno for premium features

---

**✨ Studio ready for professional creative work.**  
**All tools integrated. All skills activated. Production begins now.**

