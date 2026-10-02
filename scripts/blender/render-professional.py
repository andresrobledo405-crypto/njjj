#!/usr/bin/env python3
"""Professional Blender Rendering Script"""
import bpy
import sys

# Scene configuration
scene = bpy.context.scene
scene.render.engine = 'CYCLES'  # Highest quality
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.fps = 30
scene.render.fps_base = 1

# Cycles settings (professional)
scene.cycles.samples = 256
scene.cycles.min_samples = 64
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.cycles.tile_size = 256

# Output settings
output_path = sys.argv[-1] if len(sys.argv) > 1 else '/tmp/blender_render.mp4'
scene.render.filepath = output_path
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.image_settings.codec = 'H264'
scene.render.ffmpeg.codec = 'h264'
scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.audio_codec = 'AAC'
scene.render.ffmpeg.audio_channels = 2
scene.render.ffmpeg.audio_mixrate = 48000

# Color space
scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'Medium High Contrast'

# Render
bpy.ops.render.render(animation=True)
print(f"Rendered professional video to: {output_path}")
