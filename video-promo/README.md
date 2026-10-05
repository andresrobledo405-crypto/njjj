# Artesanos Panadería - Video Promo

Proyecto HyperFrames para generar video promo de 25 segundos.

## 📋 Archivos

- `BRIEF.md` - Especificación completa del video
- `index.html` - Composición HyperFrames (timeline, animaciones, layout)
- `hyperframes.json` - Configuración del proyecto
- `package.json` - Scripts npm

## 🚀 Cómo renderizar

### Opción 1: Local en tu máquina

```bash
# Instalar HyperFrames globalmente
npm install -g hyperframes

# En la carpeta del proyecto
cd video-promo

# Verificar composición
npx hyperframes check

# Previsualizar en Studio
npx hyperframes preview

# Renderizar video
npx hyperframes render --output artesanos-promo.mp4

# Renderizar versión vertical (mobile)
npx hyperframes render --output artesanos-promo-vertical.mp4 --canvas 1080x1920
```

### Opción 2: Cloud HyperFrames (si tienes cuenta)

```bash
npx hyperframes render --cloud --output artesanos-promo.mp4
```

## 🎨 Estructura del video

| Sección | Tiempo | Contenido |
|---------|--------|-----------|
| Intro | 0-2s | Título "ARTESANOS" con transición |
| Producto 1 | 2-4.5s | Masa Madre |
| Producto 2 | 4.5-7s | Focaccia |
| Producto 3 | 7-9.5s | Baguette |
| Producto 4 | 9.5-12s | Marraqueta |
| Producto 5 | 12-14.5s | Ciabatta |
| Producto 6 | 14.5-17s | Croissant |
| Overlay text | 2-17s | "Pan artesanal • Fermentado 24-48h..." |
| Outro | 17-25s | Contacto: +56 9 7204 4704, La Serena |

## 🎵 Audio (Próximo paso)

Para agregar:

1. **Voiceover español** (18-20 seg)
   - Usar ElevenLabs, Google TTS, o similar
   - Script: "En Artesanos, elaboramos pan con pasión..."
   - Guardar como `audio/voiceover.mp3`

2. **Música de fondo** (royalty-free, 25 seg)
   - Sonoridad mediterránea, soft
   - Guardar como `audio/bgm.mp3`

3. **Cargar audio en composición**
   ```html
   <audio data-start="2000" data-duration="18000" src="audio/voiceover.mp3"></audio>
   <audio data-start="0" data-duration="25000" src="audio/bgm.mp3" data-volume="0.3"></audio>
   ```

## 📱 Formatos

- **Desktop**: 1920x1080 (landscape)
- **Mobile**: 1080x1920 (vertical)

## 🔄 Editar

1. Abre `index.html` en el editor
2. Usa HyperFrames Studio (`npx hyperframes preview`) para preview en vivo
3. Haz cambios al HTML
4. El Studio se actualiza en tiempo real
5. Cuando estés satisfecho, renderiza

## 📤 Integración con sitio web

Una vez renderizado, reemplaza el YouTube en el Hero del sitio:

**Antes** (index.html del sitio):
```html
<iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ..."></iframe>
```

**Después**:
```html
<video autoplay muted loop style="width: 100%; height: 100%;">
  <source src="/videos/artesanos-promo.mp4" type="video/mp4">
</video>
```

## ✅ Checklist

- [ ] Renderizar `artesanos-promo.mp4`
- [ ] Agregar voiceover audio
- [ ] Agregar música de fondo
- [ ] Copiar video a `/docs/videos/`
- [ ] Actualizar HTML del hero
- [ ] Git commit y push
- [ ] Verificar en sitio live

¡Listo! 🎬
