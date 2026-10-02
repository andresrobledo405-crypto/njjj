#!/bin/bash

# YouTube Publication Script
# Requires: youtube-dl, ffmpeg, and YouTube API credentials

VIDEO_FILE="huevitos_60s_con_audio.mp4"
TITLE="Los Huevitos Sorpresa - Canción Infantil Viral 🥚"
DESCRIPTION="
Los Huevitos Sorpresa - Canción educativa para niños pequeños

¡Bienvenido a un mundo de sorpresas! Acompaña a los tres huevitos mientras se abren y revelan increíbles personajes:
- 🐤 Pollito amarillo
- 🦆 Patito naranja  
- 🐰 Conejito rosa

Perfecta para:
✅ Bebés y niños pequeños (1-4 años)
✅ Estimulación visual y auditiva
✅ Aprendizaje de animales
✅ Entretenimiento seguro

#HuevitosVirales #CanciónesInfantiles #CancionesParaNiños #BebesVirales #ViralTikTok #YouTubeKids
"

TAGS="huevitos,canción infantil,niños pequeños,bebes,animales,viral,youtube kids,cocomelon"
CATEGORY="22"  # Kids category

echo "🎬 YouTube Publication Script"
echo "════════════════════════════════════════"
echo "Video: $VIDEO_FILE"
echo "Title: $TITLE"
echo ""
echo "To upload:"
echo "1. Set up YouTube API credentials"
echo "2. Run: yt-dlp -o '%(title)s.%(ext)s' \"$VIDEO_FILE\""
echo "3. Or use YouTube Studio web interface"
echo ""
echo "📊 Recommended Settings:"
echo "- Thumbnail: Auto-generated"
echo "- Made for Kids: YES"
echo "- Visibility: Public"
echo "- Playlist: Kids Content"
echo "- Premiere: Yes (24 hours notice)"

