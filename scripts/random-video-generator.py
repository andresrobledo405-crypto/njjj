#!/usr/bin/env python3
"""
Random Video Generator - Create unique random videos
Generates random scenes, colors, animations
"""

import os
import subprocess
import numpy as np
from PIL import Image, ImageDraw
import random
import math
import wave
import struct

print("🎬 GENERADOR DE VIDEO RANDOM")
print("=" * 60)

# Configuración
RESOLUTION = (1080, 1920)
FPS = 30
DURATION = 60
FRAMES = FPS * DURATION
OUTPUT_DIR = "renders/random_frames"

os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"\n📝 CONFIGURACIÓN:")
print(f"  Resolución: {RESOLUTION[0]}×{RESOLUTION[1]}")
print(f"  Duración: {DURATION}s")
print(f"  Frames: {FRAMES}")

# Random seeds
random.seed()
bg_colors = [(random.randint(20, 100), random.randint(20, 100), random.randint(50, 150)) for _ in range(6)]
shape_colors = [(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)) for _ in range(10)]

print(f"\n🎨 FASE 1: Generando {FRAMES} frames aleatorios...")

for frame_num in range(FRAMES):
    if frame_num % 150 == 0:
        print(f"  Frame {frame_num}/{FRAMES}")

    # Crear imagen con fondo aleatorio
    progress = frame_num / FRAMES
    bg_idx = int(progress * 5)
    bg_color = bg_colors[bg_idx % len(bg_colors)]

    img = Image.new('RGB', RESOLUTION, bg_color)
    draw = ImageDraw.Draw(img)

    # Calcular animación
    angle = progress * math.pi * 8
    scale = 1 + 0.3 * math.sin(progress * math.pi * 4)

    # Dibujar formas aleatorias
    num_shapes = 3 + int(progress * 5)
    for i in range(num_shapes):
        shape_seed = (i + int(progress * 100)) % 10
        color = shape_colors[shape_seed]

        # Posición basada en fase
        x = RESOLUTION[0] // 2 + 200 * math.cos(angle + i * 2.09) * scale
        y = RESOLUTION[1] // 2 + 300 * math.sin(angle + i * 2.09) * scale

        # Dibujar círculos o rectángulos
        if i % 2 == 0:
            r = 30 + 20 * scale
            draw.ellipse([x-r, y-r, x+r, y+r], fill=color, outline=(255,255,255), width=2)
        else:
            w = 60 * scale
            draw.rectangle([x-w, y-w/2, x+w, y+w/2], fill=color, outline=(255,255,255), width=2)

    # Efectos visuales aleatorios
    if progress < 0.25:
        # Transición entrada
        alpha = progress / 0.25
        for _ in range(int(20 * alpha)):
            rx = random.randint(0, RESOLUTION[0])
            ry = random.randint(0, RESOLUTION[1])
            draw.point((rx, ry), fill=(255, 255, 255))

    elif progress > 0.75:
        # Transición salida
        alpha = (1 - progress) / 0.25
        for _ in range(int(20 * alpha)):
            rx = random.randint(0, RESOLUTION[0])
            ry = random.randint(0, RESOLUTION[1])
            draw.point((rx, ry), fill=(255, 0, 0))

    # Texto dinámico
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
    except:
        font = ImageFont.load_default()

    text = f"RANDOM VIDEO #{random.randint(1000, 9999)}"
    draw.text((RESOLUTION[0]//2 - 200, 100), text, fill=(255, 255, 255), font=font)

    # Guardar
    frame_path = os.path.join(OUTPUT_DIR, f"frame_{frame_num:06d}.png")
    img.save(frame_path)

print(f"✓ {FRAMES} frames generados")

# AUDIO RANDOM
print(f"\n🔊 FASE 2: Generando audio random...")

SAMPLE_RATE = 48000
AUDIO_PATH = "/tmp/random_audio.wav"

audio_data = []
for i in range(SAMPLE_RATE * DURATION):
    t = i / SAMPLE_RATE

    # Envelope
    if t < 1:
        env = t
    elif t > DURATION - 1:
        env = DURATION - t
    else:
        env = 1.0

    # Notas aleatorias
    freq = random.choice([440, 494, 523, 587, 659, 740, 831])
    sample = int(32767 * 0.3 * env * math.sin(2 * math.pi * freq * t))
    audio_data.append(sample)

with wave.open(AUDIO_PATH, 'w') as wav_file:
    wav_file.setnchannels(2)
    wav_file.setsampwidth(2)
    wav_file.setframerate(SAMPLE_RATE)
    for sample in audio_data:
        wav_file.writeframes(struct.pack('<h', sample))
        wav_file.writeframes(struct.pack('<h', sample))

print(f"✓ Audio generado")

# VIDEO
print(f"\n🎬 FASE 3: Compilando video...")

video_path = "exports/random_video.mp4"
os.makedirs("exports", exist_ok=True)

cmd = [
    "ffmpeg", "-y", "-loglevel", "error",
    "-framerate", str(FPS),
    "-i", f"{OUTPUT_DIR}/frame_%06d.png",
    "-i", AUDIO_PATH,
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "18",
    "-c:a", "aac",
    "-b:a", "192k",
    "-pix_fmt", "yuv420p",
    video_path
]

subprocess.run(cmd, capture_output=True)
print(f"✓ Video compilado: {video_path}")

# EXPORTAR
print(f"\n📱 FASE 4: Exportando a plataformas...")

for platform in ["youtube", "tiktok", "instagram", "facebook", "twitter"]:
    os.makedirs(f"exports/{platform}", exist_ok=True)
    output = f"exports/{platform}/random_{platform}.mp4"

    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", video_path,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        output
    ]

    subprocess.run(cmd, capture_output=True)
    size = os.path.getsize(output) / (1024 * 1024)
    print(f"✓ {platform.upper():10} → {size:.1f} MB")

print(f"\n" + "="*60)
print(f"🎉 VIDEO RANDOM GENERADO EXITOSAMENTE")
print(f"="*60)
print(f"\n✅ Resultados:")
print(f"  Master:    exports/random_video.mp4")
print(f"  YouTube:   exports/youtube/random_youtube.mp4")
print(f"  TikTok:    exports/tiktok/random_tiktok.mp4")
print(f"  Instagram: exports/instagram/random_instagram.mp4")
print(f"  Facebook:  exports/facebook/random_facebook.mp4")
print(f"  Twitter:   exports/twitter/random_twitter.mp4")
print(f"\n🚀 Listo para reproducir y publicar")
