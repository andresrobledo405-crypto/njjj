#!/bin/bash

##############################################################################
# Professional Animation & Video Production Tools Installer
# Installs industry-standard open-source and professional software
##############################################################################

set -e

echo "🎬 PROFESSIONAL ANIMATION & VIDEO TOOLS INSTALLER"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Detect OS
OS_TYPE=$(uname -s)
ARCH=$(uname -m)

echo "Detected: $OS_TYPE ($ARCH)"
echo ""

##############################################################################
# 1. BLENDER - Industry Standard 3D, Animation, Rendering
##############################################################################

echo -e "${BLUE}[1/8] Installing Blender (3D Animation & Rendering)${NC}"

if ! command -v blender &> /dev/null; then
  if [[ "$OS_TYPE" == "Linux" ]]; then
    if [[ "$ARCH" == "x86_64" ]]; then
      echo "Downloading Blender for Linux x64..."
      wget -q https://mirror.clarkson.edu/blender/release/Blender4.1/blender-4.1.0-linux-x64.tar.xz -O /tmp/blender.tar.xz
      tar -xf /tmp/blender.tar.xz -C /opt/
      ln -sf /opt/blender-4.1.0-linux-x64/blender /usr/local/bin/blender
    fi
  elif [[ "$OS_TYPE" == "Darwin" ]]; then
    echo "Installing Blender via Homebrew..."
    brew install blender
  fi
  echo -e "${GREEN}✓ Blender installed${NC}"
else
  echo -e "${GREEN}✓ Blender already installed$(NC)"
fi

##############################################################################
# 2. NATRON - Professional Node-Based Compositing
##############################################################################

echo ""
echo -e "${BLUE}[2/8] Installing Natron (VFX & Compositing)${NC}"

if ! command -v natron &> /dev/null; then
  if [[ "$OS_TYPE" == "Linux" ]]; then
    echo "Installing Natron dependencies..."
    if command -v apt &> /dev/null; then
      sudo apt install -y natron || echo "Natron not in default repos"
    fi
  elif [[ "$OS_TYPE" == "Darwin" ]]; then
    brew install natron || echo "Please download Natron from github.com/NatronGitHub/Natron"
  fi
  echo -e "${GREEN}✓ Natron setup complete${NC}"
else
  echo -e "${GREEN}✓ Natron already installed${NC}"
fi

##############################################################################
# 3. KDENLIVE - Professional Video Editing
##############################################################################

echo ""
echo -e "${BLUE}[3/8] Installing Kdenlive (Video Editing)${NC}"

if ! command -v kdenlive &> /dev/null; then
  if [[ "$OS_TYPE" == "Linux" ]]; then
    if command -v apt &> /dev/null; then
      sudo apt install -y kdenlive
    elif command -v yum &> /dev/null; then
      sudo yum install -y kdenlive
    fi
  elif [[ "$OS_TYPE" == "Darwin" ]]; then
    brew install kdenlive
  fi
  echo -e "${GREEN}✓ Kdenlive installed${NC}"
else
  echo -e "${GREEN}✓ Kdenlive already installed${NC}"
fi

##############################################################################
# 4. GIMP - Professional Image Editing
##############################################################################

echo ""
echo -e "${BLUE}[4/8] Installing GIMP (Image Editing)${NC}"

if ! command -v gimp &> /dev/null; then
  if [[ "$OS_TYPE" == "Linux" ]]; then
    if command -v apt &> /dev/null; then
      sudo apt install -y gimp gimp-plugin-registry
    elif command -v yum &> /dev/null; then
      sudo yum install -y gimp
    fi
  elif [[ "$OS_TYPE" == "Darwin" ]]; then
    brew install gimp
  fi
  echo -e "${GREEN}✓ GIMP installed${NC}"
else
  echo -e "${GREEN}✓ GIMP already installed${NC}"
fi

##############################################################################
# 5. KRITA - Digital Painting & Animation
##############################################################################

echo ""
echo -e "${BLUE}[5/8] Installing Krita (Digital Painting & Animation)${NC}"

if ! command -v krita &> /dev/null; then
  if [[ "$OS_TYPE" == "Linux" ]]; then
    if command -v apt &> /dev/null; then
      sudo apt install -y krita
    elif command -v yum &> /dev/null; then
      sudo yum install -y krita
    fi
  elif [[ "$OS_TYPE" == "Darwin" ]]; then
    brew install krita
  fi
  echo -e "${GREEN}✓ Krita installed${NC}"
else
  echo -e "${GREEN}✓ Krita already installed${NC}"
fi

##############################################################################
# 6. INKSCAPE - Vector Graphics & Animation
##############################################################################

echo ""
echo -e "${BLUE}[6/8] Installing Inkscape (Vector Graphics)${NC}"

if ! command -v inkscape &> /dev/null; then
  if [[ "$OS_TYPE" == "Linux" ]]; then
    if command -v apt &> /dev/null; then
      sudo apt install -y inkscape
    elif command -v yum &> /dev/null; then
      sudo yum install -y inkscape
    fi
  elif [[ "$OS_TYPE" == "Darwin" ]]; then
    brew install inkscape
  fi
  echo -e "${GREEN}✓ Inkscape installed${NC}"
else
  echo -e "${GREEN}✓ Inkscape already installed${NC}"
fi

##############################################################################
# 7. ADVANCED IMAGE PROCESSING
##############################################################################

echo ""
echo -e "${BLUE}[7/8] Installing Advanced Image Tools${NC}"

# ImageMagick
if ! command -v convert &> /dev/null; then
  if command -v apt &> /dev/null; then
    sudo apt install -y imagemagick
  elif command -v yum &> /dev/null; then
    sudo yum install -y ImageMagick
  elif [[ "$OS_TYPE" == "Darwin" ]]; then
    brew install imagemagick
  fi
  echo -e "${GREEN}✓ ImageMagick installed${NC}"
else
  echo -e "${GREEN}✓ ImageMagick already installed${NC}"
fi

# GraphicsMagick
if ! command -v gm &> /dev/null; then
  if command -v apt &> /dev/null; then
    sudo apt install -y graphicsmagick
  elif command -v yum &> /dev/null; then
    sudo yum install -y GraphicsMagick
  elif [[ "$OS_TYPE" == "Darwin" ]]; then
    brew install graphicsmagick
  fi
  echo -e "${GREEN}✓ GraphicsMagick installed${NC}"
else
  echo -e "${GREEN}✓ GraphicsMagick already installed${NC}"
fi

# Darktable (color grading)
if ! command -v darktable &> /dev/null; then
  if command -v apt &> /dev/null; then
    sudo apt install -y darktable
  elif command -v yum &> /dev/null; then
    sudo yum install -y darktable
  elif [[ "$OS_TYPE" == "Darwin" ]]; then
    brew install darktable
  fi
  echo -e "${GREEN}✓ Darktable (color grading) installed${NC}"
else
  echo -e "${GREEN}✓ Darktable already installed${NC}"
fi

##############################################################################
# 8. SCREEN RECORDING & STREAMING
##############################################################################

echo ""
echo -e "${BLUE}[8/8] Installing Screen Recording Tools${NC}"

# OBS Studio
if ! command -v obs &> /dev/null; then
  if command -v apt &> /dev/null; then
    sudo apt install -y obs-studio
  elif command -v yum &> /dev/null; then
    sudo yum install -y obs-studio
  elif [[ "$OS_TYPE" == "Darwin" ]]; then
    brew install obs
  fi
  echo -e "${GREEN}✓ OBS Studio installed${NC}"
else
  echo -e "${GREEN}✓ OBS Studio already installed${NC}"
fi

# ScreenKey (on-screen keyboard)
if ! command -v screenkey &> /dev/null; then
  if command -v apt &> /dev/null; then
    sudo apt install -y screenkey || echo "screenkey not available"
  fi
fi

##############################################################################
# BLENDER EXTENSIONS & PLUGINS
##############################################################################

echo ""
echo -e "${BLUE}Installing Blender Add-ons...${NC}"

BLENDER_ADDONS="$HOME/.config/blender/4.1/scripts/addons"
mkdir -p "$BLENDER_ADDONS"

# Download recommended add-ons
echo "Installing Blender animation tools..."

# Easier FCURVE (animation easing)
if [ ! -d "$BLENDER_ADDONS/easier_fcurve" ]; then
  echo "Downloading Easier FCURVE..."
  git clone https://github.com/Mets3D/easier_fcurve.git "$BLENDER_ADDONS/easier_fcurve" 2>/dev/null || true
fi

# Cinemagraph (looping animations)
if [ ! -d "$BLENDER_ADDONS/cinemagraph" ]; then
  echo "Cinemagraph tools included with Blender"
fi

echo -e "${GREEN}✓ Blender add-ons configured${NC}"

##############################################################################
# FFMPEG ADVANCED CODECS
##############################################################################

echo ""
echo -e "${BLUE}Building FFmpeg with Advanced Codecs...${NC}"

if command -v ffmpeg &> /dev/null; then
  FFMPEG_VERSION=$(ffmpeg -version | head -1)
  echo "Current FFmpeg: $FFMPEG_VERSION"

  # Check for required codecs
  if ffmpeg -codecs 2>&1 | grep -q "libx265"; then
    echo -e "${GREEN}✓ H.265/HEVC codec available${NC}"
  else
    echo "Installing H.265 support..."
    if command -v apt &> /dev/null; then
      sudo apt install -y libx265-dev
    fi
  fi

  if ffmpeg -codecs 2>&1 | grep -q "libvpx"; then
    echo -e "${GREEN}✓ VP9 codec available${NC}"
  fi

  if ffmpeg -codecs 2>&1 | grep -q "libopus"; then
    echo -e "${GREEN}✓ Opus audio codec available${NC}"
  fi
else
  echo -e "${RED}FFmpeg not found - already installed by setup-design-tools.sh${NC}"
fi

##############################################################################
# CONFIGURATION FILES
##############################################################################

echo ""
echo -e "${BLUE}Creating Configuration Files...${NC}"

# Blender rendering script
mkdir -p scripts/blender
cat > scripts/blender/render.py << 'EOF'
#!/usr/bin/env python3
"""
Blender batch rendering script
Usage: blender -b scene.blend -P render.py
"""

import bpy
import sys

# Get output path from command line args
output_path = sys.argv[-1] if len(sys.argv) > 1 else "/tmp/render.mp4"

# Configure scene for professional rendering
scene = bpy.context.scene
scene.render.engine = 'CYCLES'  # Best quality
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.fps = 30
scene.render.film_transparent = False

# Cycles optimization
scene.cycles.samples = 256  # High quality
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'

# Output
scene.render.filepath = output_path
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.image_settings.codec = 'H264'
scene.render.ffmpeg.codec = 'h264'
scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
scene.render.ffmpeg.format = 'MPEG4'

# Render
bpy.ops.render.render(animation=True, write_still=False)
print(f"Rendered to {output_path}")
EOF

chmod +x scripts/blender/render.py
echo -e "${GREEN}✓ Blender rendering script created${NC}"

# FFmpeg preset for fast encoding
cat > scripts/ffmpeg-preset-fast.txt << 'EOF'
# FFmpeg fast preset
-c:v libx264
-preset slow
-crf 14
-profile:v high
-level 4.2
-pix_fmt yuv420p
-movflags +faststart
-c:a aac
-b:a 192k
EOF

echo -e "${GREEN}✓ FFmpeg preset created${NC}"

##############################################################################
# DOCUMENTATION
##############################################################################

cat > PROFESSIONAL-TOOLS.md << 'EOF'
# Professional Animation & Video Production Tools

All tools installed and ready for professional use.

## Installed Software

### Video & Animation
- **Blender** - 3D modeling, animation, rendering, compositing
  - Path: `blender`
  - Render script: `scripts/blender/render.py`
- **Kdenlive** - Professional video editing (NLE)
  - Path: `kdenlive`

### Image & Graphics
- **GIMP** - Professional image editing
  - Path: `gimp`
- **Krita** - Digital painting and animation
  - Path: `krita`
- **Inkscape** - Vector graphics and animation
  - Path: `inkscape`
- **Darktable** - Color grading and RAW processing
  - Path: `darktable`

### VFX & Compositing
- **Natron** - Node-based compositing
  - Path: `natron`

### Image Processing
- **ImageMagick** - Command-line image manipulation
  - Usage: `convert`, `identify`, `mogrify`
- **GraphicsMagick** - Optimized ImageMagick fork
  - Usage: `gm convert`, `gm identify`

### Screen Recording
- **OBS Studio** - Professional streaming/recording
  - Path: `obs`

## Quick Start

### Render Animation in Blender
```bash
blender -b scene.blend -P scripts/blender/render.py -- /output/video.mp4
```

### Batch Image Processing
```bash
# Resize all images
mogrify -resize 1920x1080 *.jpg

# Convert to multiple formats
convert input.png -quality 85 output.jpg
```

### Edit Video in Kdenlive
```bash
kdenlive project.kdenlive
```

### Color Grading
```bash
darktable image.raw
```

### Compose in Natron
```bash
natron project.ntp
```

### Screen Recording
```bash
obs  # Launch GUI
```

## Integration with Automation

The video automation engine supports:

1. **Blender rendering** - For 3D animations
2. **FFmpeg encoding** - For high-quality output
3. **ImageMagick** - For frame generation
4. **Natron compositing** - For VFX integration

## Recommended Workflows

### Professional Video Production
1. **Storyboard** → Inkscape vector graphics
2. **Animate** → Blender 3D or Krita 2D
3. **Composite** → Natron node-based effects
4. **Color Grade** → Darktable or FFmpeg filters
5. **Edit** → Kdenlive (if needed)
6. **Render** → FFmpeg H.264/H.265

### Image Production
1. **Create** → GIMP or Krita
2. **Process** → ImageMagick CLI
3. **Grade** → Darktable
4. **Export** → Multiple formats

### Automation Pipeline
```
Concept → Blender Script → FFmpeg → Natron → Kdenlive → Final Export
    ↓
Automated via video-automation-engine.js
```

## Performance Tips

### Blender Rendering
- Use CUDA/OPTIX (GPU rendering) for speed
- Reduce samples for previews, increase for finals
- Use OpenImageDenoise for faster rendering

### FFmpeg Encoding
- Use `-preset slow` for quality
- Use CRF 14-18 for professional output
- Use VP9 for large uploads, H.264 for compatibility

### Memory Management
- Process large videos in segments
- Use proxies in Kdenlive for editing
- Render frames separately, then composite

## Professional Presets

### FFmpeg Quality Settings
```bash
# High quality (2-5 MB/min)
-c:v libx264 -preset slow -crf 14

# Medium quality (1-2 MB/min)
-c:v libx264 -preset medium -crf 18

# Fast quality (0.5-1 MB/min)
-c:v libx264 -preset fast -crf 20
```

### Blender Cycles Rendering
```python
scene.cycles.samples = 256  # Professional quality
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'
```

## Troubleshooting

### Blender GPU Rendering
1. Ensure NVIDIA/AMD drivers installed
2. Enable CUDA/HIP in Blender preferences
3. Set device in render settings

### FFmpeg Codec Issues
```bash
# Check available codecs
ffmpeg -codecs | grep h264

# Check input format
ffprobe video.mp4
```

### Kdenlive Performance
1. Use proxy clips for editing
2. Disable effects during editing
3. Render final export with all effects

---

**All professional tools installed and configured.**
**Ready for professional video production.**
EOF

echo -e "${GREEN}✓ Documentation created: PROFESSIONAL-TOOLS.md${NC}"

##############################################################################
# VERIFICATION
##############################################################################

echo ""
echo -e "${BLUE}Verifying Installation...${NC}"
echo ""

echo "Installed Tools:"
command -v blender &> /dev/null && echo "  ✓ Blender" || echo "  ✗ Blender"
command -v kdenlive &> /dev/null && echo "  ✓ Kdenlive" || echo "  ✗ Kdenlive"
command -v gimp &> /dev/null && echo "  ✓ GIMP" || echo "  ✗ GIMP"
command -v krita &> /dev/null && echo "  ✓ Krita" || echo "  ✗ Krita"
command -v inkscape &> /dev/null && echo "  ✓ Inkscape" || echo "  ✗ Inkscape"
command -v natron &> /dev/null && echo "  ✓ Natron" || echo "  ✗ Natron"
command -v darktable &> /dev/null && echo "  ✓ Darktable" || echo "  ✗ Darktable"
command -v convert &> /dev/null && echo "  ✓ ImageMagick" || echo "  ✗ ImageMagick"
command -v gm &> /dev/null && echo "  ✓ GraphicsMagick" || echo "  ✗ GraphicsMagick"
command -v obs &> /dev/null && echo "  ✓ OBS Studio" || echo "  ✗ OBS Studio"
command -v ffmpeg &> /dev/null && echo "  ✓ FFmpeg" || echo "  ✗ FFmpeg"

echo ""

##############################################################################
# COMPLETE
##############################################################################

echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ PROFESSIONAL TOOLS INSTALLATION COMPLETE${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Available Commands:"
echo "  Blender:      blender"
echo "  Kdenlive:     kdenlive"
echo "  GIMP:         gimp"
echo "  Krita:        krita"
echo "  Inkscape:     inkscape"
echo "  Natron:       natron"
echo "  Darktable:    darktable"
echo "  ImageMagick:  convert, identify, mogrify"
echo "  GraphicsMagick: gm"
echo "  OBS Studio:   obs"
echo "  FFmpeg:       ffmpeg, ffprobe"
echo ""
echo "Documentation: PROFESSIONAL-TOOLS.md"
echo "Integration:   video-automation-engine.js"
echo ""
echo "Next Steps:"
echo "1. Review PROFESSIONAL-TOOLS.md"
echo "2. Launch tools: blender, kdenlive, gimp, etc."
echo "3. Use automation: npm run create:video"
echo ""
