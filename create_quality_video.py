from PIL import Image, ImageDraw, ImageFont
import subprocess
import os
import math

os.makedirs("frames_hq", exist_ok=True)

W, H = 1080, 1920
fps = 30
duration_sec = 60
total_frames = fps * duration_sec

# Scenes timing
scenes = [
    {"name": "gancho", "start": 0, "duration": 5, "draw": "eggs_bounce"},
    {"name": "pollito", "start": 5, "duration": 7, "draw": "chick_dance"},
    {"name": "patito", "start": 12, "duration": 8, "draw": "duck_dance"},
    {"name": "conejito", "start": 20, "duration": 8, "draw": "bunny_dance"},
    {"name": "todos", "start": 28, "duration": 17, "draw": "all_dance"},
    {"name": "finale", "start": 45, "duration": 15, "draw": "finale"},
]

def gradient_bg(img):
    """Create gradient background"""
    pixels = img.load()
    for y in range(H):
        # Blue to green gradient
        r = int(135 + (144-135) * (y/H))
        g = int(206 + (238-206) * (y/H))
        b = int(235 - (155) * (y/H))
        for x in range(W):
            pixels[x, y] = (r, g, b)

def draw_egg(draw, x, y, color, frame, scene_start):
    """Draw bouncing egg"""
    t = (frame - scene_start * fps) / fps
    t = t % 1
    bounce = math.sin(t * math.pi) * 30
    y_pos = y - bounce
    
    size = 90
    draw.ellipse([x-size, y_pos-size-20, x+size, y_pos+size], fill=color, outline=(0,0,0), width=2)
    draw.ellipse([x-size+10, y_pos-size-20+10, x-size+30, y_pos-size-20+30], fill=(255,255,255,100))

def draw_emoji(draw, x, y, emoji, frame, scene_start, scale=1.0):
    """Draw emoji text (approximation)"""
    draw.text((x-50*scale, y-50*scale), emoji, font=None, fill=(0,0,0))

# Render frames
print("Rendering frames...")
for frame in range(total_frames):
    img = Image.new('RGB', (W, H))
    gradient_bg(img)
    draw = ImageDraw.Draw(img)
    
    current_sec = frame / fps
    
    # Determine current scene
    for scene in scenes:
        if scene["start"] <= current_sec < scene["start"] + scene["duration"]:
            # Gancho - bouncing eggs
            if scene["draw"] == "eggs_bounce":
                draw_egg(draw, W//4, H//3, (255, 68, 68), frame, scene["start"])
                draw_egg(draw, W//2, H//3, (68, 136, 255), frame, scene["start"])
                draw_egg(draw, 3*W//4, H//3, (255, 215, 0), frame, scene["start"])
                draw.text((W//2-200, H//2+200), "¿QUIEN ESTÁ ADENTRO?", font=None, fill=(255,255,255))
            
            # Solo chick
            elif scene["draw"] == "chick_dance":
                draw.text((W//2-150, H//2-100), "🐤", font=None, fill=(0,0,0))
                draw.text((W//2-200, H//2+150), "¡Pollito!", font=None, fill=(255,255,255))
                draw.text((W//2-250, H//2+250), "¡Pía, pía, pía!", font=None, fill=(255,215,0))
            
            # Solo duck
            elif scene["draw"] == "duck_dance":
                draw.text((W//2-150, H//2-100), "🦆", font=None, fill=(0,0,0))
                draw.text((W//2-200, H//2+150), "¡Patito!", font=None, fill=(255,255,255))
                draw.text((W//2-200, H//2+250), "¡Cuá, cuá!", font=None, fill=(255,215,0))
            
            # Solo bunny
            elif scene["draw"] == "bunny_dance":
                draw.text((W//2-150, H//2-100), "🐰", font=None, fill=(0,0,0))
                draw.text((W//2-200, H//2+150), "¡Conejito!", font=None, fill=(255,255,255))
                draw.text((W//2-150, H//2+250), "¡Hop!", font=None, fill=(255,215,0))
            
            # All dancing
            elif scene["draw"] == "all_dance":
                draw.text((W//4-100, H//2-100), "🐤", font=None, fill=(0,0,0))
                draw.text((W//2-100, H//2-100), "🦆", font=None, fill=(0,0,0))
                draw.text((3*W//4-100, H//2-100), "🐰", font=None, fill=(0,0,0))
                draw.text((W//2-200, H//2+300), "¡TODOS BAILAN!", font=None, fill=(255,255,255))
            
            # Finale
            elif scene["draw"] == "finale":
                draw.text((W//4-100, H//2-100), "🐤", font=None, fill=(0,0,0))
                draw.text((W//2-100, H//2-100), "🦆", font=None, fill=(0,0,0))
                draw.text((3*W//4-100, H//2-100), "🐰", font=None, fill=(0,0,0))
                draw.text((W//2-400, H//2+300), "¡LOS HUEVITOS SORPRESA!", font=None, fill=(255,255,255))
                draw.text((W//2-200, H//2+450), "❤️ FIN ❤️", font=None, fill=(255,215,0))
            break
    
    img.save(f"frames_hq/frame_{frame:06d}.png")
    if (frame + 1) % 30 == 0:
        print(f"  {frame + 1}/{total_frames}")

print("✓ Frames rendered")

# Compile to video
print("Compiling to MP4...")
os.system(f"ffmpeg -y -framerate {fps} -i frames_hq/frame_%06d.png -c:v libx264 -pix_fmt yuv420p -preset slow -crf 18 huevitos-hd.mp4 2>&1 | grep -E 'frame=|muxing'")

print("✓ Video compilado")
