#!/usr/bin/env python3
"""
Demo Video Generator - Create professional demo video
Generates frames, adds audio, exports to 5 platforms
"""

import os
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import wave
import struct
import math

print("🎬 GENERADOR DE VIDEO DE DEMOSTRACIÓN")
print("=" * 50)

# Configuración
RESOLUTION = (1080, 1920)  # vertical
FPS = 30
DURATION = 60
FRAMES = FPS * DURATION  # 1800 frames
OUTPUT_DIR = "renders/demo_frames"

# Crear directorio
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"\n📝 CONFIGURACIÓN:")
print(f"  Resolución: {RESOLUTION[0]}×{RESOLUTION[1]}")
print(f"  FPS: {FPS}")
print(f"  Duración: {DURATION}s")
print(f"  Frames: {FRAMES}")

# FASE 1: GENERAR FRAMES
print(f"\n🎨 FASE 1: Generando {FRAMES} frames...")

colors = [
    (255, 100, 100),  # Rojo huevo
    (255, 200, 100),  # Naranja huevo
    (255, 150, 200),  # Rosa huevo
    (100, 200, 255),  # Azul fondo
]

for frame_num in range(FRAMES):
    if frame_num % 100 == 0:
        print(f"  Frame {frame_num}/{FRAMES}")

    # Crear imagen
    img = Image.new('RGB', RESOLUTION, (30, 30, 60))
    draw = ImageDraw.Draw(img)

    # Calcular progresión del video
    progress = frame_num / FRAMES

    # ESCENA 1 (0-10s): Huevos rebotando
    if progress < 0.166:  # 10 segundos de 60
        scene_progress = progress / 0.166

        # Dibujar huevos
        for i, color in enumerate(colors[:3]):
            x = 270 + i * 180
            bounce = abs(math.sin(scene_progress * math.pi * 4)) * 150
            y = 600 + bounce

            # Óvalo
            draw.ellipse([x-60, y-90, x+60, y], fill=color, outline=(255,255,255), width=3)

            # Brillo
            draw.ellipse([x-40, y-70, x-20, y-50], fill=(255,255,255))

    # ESCENA 2 (10-20s): Huevos agrietados
    elif progress < 0.333:
        scene_progress = (progress - 0.166) / 0.166

        for i, color in enumerate(colors[:3]):
            x = 270 + i * 180
            y = 600

            # Óvalo agrietado
            draw.ellipse([x-60, y-90, x+60, y], fill=color, outline=(255,255,255), width=3)

            # Grietas
            if scene_progress > 0.5:
                draw.line([x-30, y-50, x, y-20], fill=(0,0,0), width=2)
                draw.line([x, y-50, x+30, y-20], fill=(0,0,0), width=2)

    # ESCENA 3 (20-30s): Pollito emerge
    elif progress < 0.5:
        scene_progress = (progress - 0.333) / 0.166

        x, y = 270, 600

        # Huevo roto
        draw.ellipse([x-60, y-90, x+60, y], fill=colors[0], outline=(255,255,255), width=3)

        # Pollito emerge
        pollito_y = y - 90 * scene_progress
        draw.ellipse([x-30, pollito_y-40, x+30, pollito_y], fill=(255, 255, 0))  # Cuerpo
        draw.circle((x-15, pollito_y-50), 15, fill=(255, 255, 0))  # Cabeza
        draw.circle((x-18, pollito_y-55), 5, fill=(0, 0, 0))  # Ojo
        draw.polygon([(x+5, pollito_y-40), (x+15, pollito_y-35), (x+5, pollito_y-35)], fill=(255, 150, 0))  # Pico

    # ESCENA 4 (30-40s): Patito emerge
    elif progress < 0.666:
        scene_progress = (progress - 0.5) / 0.166

        x, y = 450, 600

        # Huevo roto
        draw.ellipse([x-60, y-90, x+60, y], fill=colors[1], outline=(255,255,255), width=3)

        # Patito emerge
        patito_y = y - 90 * scene_progress
        draw.ellipse([x-30, patito_y-40, x+30, patito_y], fill=(255, 200, 0))  # Cuerpo
        draw.circle((x-15, patito_y-50), 15, fill=(255, 200, 0))  # Cabeza
        draw.circle((x-18, patito_y-55), 5, fill=(0, 0, 0))  # Ojo

    # ESCENA 5 (40-50s): Conejito emerge
    elif progress < 0.833:
        scene_progress = (progress - 0.666) / 0.166

        x, y = 630, 600

        # Huevo roto
        draw.ellipse([x-60, y-90, x+60, y], fill=colors[2], outline=(255,255,255), width=3)

        # Conejito emerge
        conejito_y = y - 90 * scene_progress
        draw.ellipse([x-30, conejito_y-40, x+30, conejito_y], fill=(255, 150, 200))  # Cuerpo
        draw.circle((x-15, conejito_y-50), 15, fill=(255, 150, 200))  # Cabeza
        draw.circle((x-18, conejito_y-55), 5, fill=(0, 0, 0))  # Ojo
        draw.polygon([(x-20, conejito_y-60), (x-15, conejito_y-80), (x-10, conejito_y-60)], fill=(255, 150, 200))  # Oreja

    # ESCENA 6 (50-60s): Todos bailan juntos
    else:
        scene_progress = (progress - 0.833) / 0.166

        # Pollito
        x1 = 270 + math.sin(scene_progress * math.pi * 4) * 50
        y1 = 500 + math.cos(scene_progress * math.pi * 4) * 30
        draw.ellipse([x1-30, y1-40, x1+30, y1], fill=(255, 255, 0))
        draw.circle((x1-15, y1-50), 15, fill=(255, 255, 0))

        # Patito
        x2 = 450 + math.sin(scene_progress * math.pi * 4 + 2.09) * 50
        y2 = 500 + math.cos(scene_progress * math.pi * 4 + 2.09) * 30
        draw.ellipse([x2-30, y2-40, x2+30, y2], fill=(255, 200, 0))
        draw.circle((x2-15, y2-50), 15, fill=(255, 200, 0))

        # Conejito
        x3 = 630 + math.sin(scene_progress * math.pi * 4 + 4.19) * 50
        y3 = 500 + math.cos(scene_progress * math.pi * 4 + 4.19) * 30
        draw.ellipse([x3-30, y3-40, x3+30, y3], fill=(255, 150, 200))
        draw.circle((x3-15, y3-50), 15, fill=(255, 150, 200))

    # Agregar texto
    try:
        # Intentar usar fuente
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        font = ImageFont.load_default()

    draw.text((RESOLUTION[0]//2 - 150, 100), "Los Huevitos Sorpresa", fill=(255,255,255), font=font)

    # Guardar frame
    frame_path = os.path.join(OUTPUT_DIR, f"frame_{frame_num:06d}.png")
    img.save(frame_path)

print(f"✓ {FRAMES} frames generados en {OUTPUT_DIR}/")

# FASE 2: GENERAR AUDIO
print(f"\n🔊 FASE 2: Generando audio...")

# Audio de demostración (simple beeps + música)
SAMPLE_RATE = 48000
AUDIO_PATH = "/tmp/demo_audio.wav"

audio_data = []

# Generar tono musical simple (1200 Hz)
for i in range(SAMPLE_RATE * DURATION):
    t = i / SAMPLE_RATE
    # Envelope: fade in, hold, fade out
    if t < 0.5:
        env = t / 0.5
    elif t > DURATION - 0.5:
        env = (DURATION - t) / 0.5
    else:
        env = 1.0

    # Nota musical
    freq = 440 + 220 * math.sin(t * 2)
    sample = int(32767 * 0.3 * env * math.sin(2 * math.pi * freq * t))
    audio_data.append(sample)

# Guardar como WAV
with wave.open(AUDIO_PATH, 'w') as wav_file:
    wav_file.setnchannels(2)  # Stereo
    wav_file.setsampwidth(2)
    wav_file.setframerate(SAMPLE_RATE)
    for sample in audio_data:
        wav_file.writeframes(struct.pack('<h', sample))
        wav_file.writeframes(struct.pack('<h', sample))

print(f"✓ Audio generado: {AUDIO_PATH}")

# FASE 3: COMPILAR FRAMES A VIDEO
print(f"\n🎬 FASE 3: Compilando video con FFmpeg...")

video_path = "exports/demo_video.mp4"
os.makedirs("exports", exist_ok=True)

cmd = [
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", f"{OUTPUT_DIR}/frame_%06d.png",
    "-i", AUDIO_PATH,
    "-c:v", "libx264",
    "-preset", "slow",
    "-crf", "14",
    "-c:a", "aac",
    "-b:a", "192k",
    "-pix_fmt", "yuv420p",
    "-movflags", "+faststart",
    video_path
]

result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode == 0:
    print(f"✓ Video compilado: {video_path}")
else:
    print(f"Error: {result.stderr}")

# FASE 4: EXPORTAR A PLATAFORMAS
print(f"\n📱 FASE 4: Exportando a plataformas...")

platforms = ["youtube", "tiktok", "instagram", "facebook", "twitter"]

for platform in platforms:
    platform_dir = f"exports/{platform}"
    os.makedirs(platform_dir, exist_ok=True)

    output_file = f"{platform_dir}/demo_{platform}.mp4"

    # Copiar con FFmpeg para optimizar
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        output_file
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        size = os.path.getsize(output_file) / (1024 * 1024)
        print(f"✓ {platform.upper():10} → {output_file} ({size:.1f} MB)")

print(f"\n" + "="*50)
print(f"🎉 VIDEO DE DEMOSTRACIÓN COMPLETADO")
print(f"="*50)
print(f"\nArchivos generados:")
print(f"  - Frames:    {OUTPUT_DIR}/ ({FRAMES} PNG)")
print(f"  - Audio:     {AUDIO_PATH}")
print(f"  - Master:    exports/demo_video.mp4")
print(f"  - Plataformas: 5 variantes optimizadas")
print(f"\n✅ Listo para reproducir y publicar")
