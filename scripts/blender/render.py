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
