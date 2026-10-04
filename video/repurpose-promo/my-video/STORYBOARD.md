---
title: Repurpose AI - Product Launch Promo
duration: 30
format: landscape
destination: web + social (1920x1080, 1080x1920)
music: upbeat-electronic
narration: true
captions: true
---

# Repurpose AI - 30 Second Promo

## Video direction

Modern, fast-paced product showcase with smooth GSAP animations. Purple-to-pink gradient throughout (#667eea → #764ba2), cyan accents (#00d4ff). Glassmorphic UI elements with subtle blur. Motion is snappy (200-400ms easing), with 10-15% overshoot on clip arrivals. Split-screen design for final platform comparison. Voiceover in English with optional Spanish overlay.

---

## Frame 1: Problem Setup (0-8s)

**Role:** Hero / Problem Hook  
**Blueprint:** title-card-fade  
**Duration:** 8s

### Scene 1: Title Appears (0-2s)
- **Visual:** Desktop mockup fade in, clean white background
- **Asset:** desktop-frame (wireframe)
- **Layout:** Center, hero size
- **Motion:** 
  - Element: desktop-frame, keyframe 0-2s, fade-in + subtle scale (0.95 → 1.0)
  - Easing: ease-out-cubic
- **Text Overlay:** "One Video." appears with typing effect (color: #667eea)

### Scene 2: Problem Context (2-5s)
- **Visual:** Video file appears on desktop, thumbnail preview
- **Asset:** video-thumbnail-large
- **Layout:** Center, 60% height
- **Motion:**
  - Element: video-thumbnail, keyframe 2-5s, slide-up + fade-in
  - Start opacity: 0, End opacity: 1
  - Start transform: translateY(20px)
  - Easing: ease-out

### Scene 3: Four Platforms Text (5-8s)
- **Visual:** "Four Platforms" text appears below video
- **Text:** Large, bold, gradient text (#667eea to #764ba2)
- **Motion:**
  - Element: platforms-text, keyframe 5-8s, scale + fade-in
  - From: scale(0.8), opacity 0
  - To: scale(1), opacity 1
  - Easing: cubic-bezier(0.34, 1.56, 0.64, 1) // Bounce

**Asset_candidates:**
- desktop-frame
- video-thumbnail-large
- gradient-text-svg

---

## Frame 2: AI Analysis Magic (8-16s)

**Role:** Product Feature / Analysis  
**Blueprint:** data-visualization-animated  
**Duration:** 8s

### Scene 1: Upload Animation (8-10s)
- **Visual:** Video uploads to Repurpose AI interface
- **Asset:** upload-interface-mockup
- **Layout:** Center, 70% width
- **Motion:**
  - Element: upload-progress-bar, keyframe 8-10s, width animation
  - From: width 0%, opacity 1
  - To: width 100%, opacity 1
  - Easing: ease-out-quad
  - Include subtle pulse on 100% complete

### Scene 2: AI Analyzer Scan (10-13s)
- **Visual:** Animated scanning lines with glow, "Analyzing..." text
- **Asset:** ai-scanner-animation
- **Layout:** Overlay on interface, full width
- **Motion:**
  - Element: scanner-lines, keyframe 10-13s, continuous scan
  - Animation: translationX sweep left-to-right, repeating
  - Opacity glow pulse: 0.6 → 1.0 → 0.6
  - SFX: subtle digital "beep" every 1s

### Scene 3: Viral Scores Appear (13-16s)
- **Visual:** Viral score badges (8/10, 7/10, 6/10, 9/10) appear with numbers counting up
- **Asset:** viral-score-badges
- **Layout:** Grid 2x2 layout, center
- **Motion:**
  - Each badge: keyframe 13-16s, staggered entry (each +0.5s delay)
  - Animation: scale(0 → 1) + fade-in + rotate(slight)
  - Number counter: 0 → final-score, duration 1s per badge
  - Easing: cubic-bezier with overshoot
  - SFX: "ding" sound on each badge completion

**Asset_candidates:**
- upload-interface-mockup
- ai-scanner-animation
- viral-score-badges
- platform-icons

---

## Frame 3: Generated Clips Result (16-25s)

**Role:** Solution Reveal / Feature Comparison  
**Blueprint:** split-screen-grid  
**Duration:** 9s

### Scene 1: Split Screen Appears (16-18s)
- **Visual:** Four clips in 2x2 grid, each labeled platform (TikTok, Reels, Shorts, LinkedIn)
- **Asset:** clip-1-tiktok (vertical, 9:16)
- **Asset:** clip-2-reels (vertical, 9:16)
- **Asset:** clip-3-shorts (vertical, 9:16)
- **Asset:** clip-4-linkedin (horizontal, 16:9)
- **Layout:** Grid, 50% width each, center
- **Motion:**
  - Transition: each clip slides in from edge (cascade pattern)
  - TikTok: slide-from-left
  - Reels: slide-from-top
  - Shorts: slide-from-bottom
  - LinkedIn: slide-from-right
  - All keyframe 16-18s, staggered +0.3s each
  - Easing: ease-out-cubic

### Scene 2: Clips Hold & Highlight (18-23s)
- **Visual:** Four clips displayed, subtle play-button overlay on each
- **Asset:** play-button-icon
- **Layout:** Center on each clip (4 instances)
- **Motion:**
  - Each play button: fade-in, pulse animation (0.8 → 1.1 scale)
  - Duration: 5s, loop-smooth
  - Color glow: cyan (#00d4ff) on hover state (static glow render)

### Scene 3: Platform Labels Appear (23-25s)
- **Visual:** Platform names fade in below each clip
- **Text:** "TikTok", "Instagram Reels", "YouTube Shorts", "LinkedIn"
- **Motion:**
  - Text: fade-in + scale-up
  - Keyframe 23-25s
  - Staggered +0.2s each
  - Color: white, slight drop shadow

**Asset_candidates:**
- clip-1-tiktok
- clip-2-reels
- clip-3-shorts
- clip-4-linkedin
- play-button-icon
- platform-label-tiktok
- platform-label-reels
- platform-label-shorts
- platform-label-linkedin

---

## Frame 4: Call-to-Action (25-30s)

**Role:** CTA / Conversion  
**Blueprint:** cta-finale  
**Duration:** 5s

### Scene 1: Logo Appears (25-27s)
- **Visual:** "Repurpose AI" logo animates in
- **Asset:** repurpose-ai-logo
- **Layout:** Center, 30% height
- **Motion:**
  - Logo: scale(0 → 1) + fade-in + rotate(slight spin)
  - Keyframe 25-27s
  - Easing: cubic-bezier(0.34, 1.56, 0.64, 1) // Bounce overshoot

### Scene 2: CTA Button Appears (27-29s)
- **Visual:** "Get Started Free" button, gradient background purple-pink
- **Asset:** cta-button-gradient
- **Layout:** Center below logo, 40% width
- **Motion:**
  - Button: scale(0.8 → 1.0) + fade-in
  - Keyframe 27-29s
  - Continuous pulse animation (shadow grow/shrink): 0.5s loop
  - Color pulse: glow intensity 0.6 → 1.0 → 0.6

### Scene 3: Supporting Text (29-30s)
- **Visual:** "No credit card required" subtitle appears
- **Text:** Small, subtle, color: #999
- **Motion:**
  - Text: fade-in
  - Keyframe 29-30s
  - Scale: 0.9 → 1.0

**Handoff_out:** 
- Element: gradient-background
- Position: x 50%, y 50%
- Scale: 1.0
- Opacity: 1.0
- Direction: static, no motion outbound

**Asset_candidates:**
- repurpose-ai-logo
- cta-button-gradient
- gradient-background-purple-pink

---

## Summary

**Total Duration:** 30 seconds  
**Scenes:** 11 micro-scenes across 4 major frames  
**Platforms:** All 4 represented (TikTok, Reels, Shorts, LinkedIn)  
**Music:** Upbeat electronic, 120-130 BPM, builds to climax at Frame 4  
**Narration:** English VO (optional Spanish)  
**Transitions:** Slide + fade, cascade stagger, bounce effects  
**Color Palette:** Purple (#667eea) → Pink (#764ba2), Cyan accents (#00d4ff)  
**Motion Style:** Snappy (200-400ms), 10-15% overshoot, GSAP-based
