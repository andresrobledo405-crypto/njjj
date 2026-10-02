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
