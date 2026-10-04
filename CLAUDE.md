# Toolkit de diseño, animación y cine

Skills instaladas en `.claude/skills/` (actualizar: `npx skills update`; buscar más: skill `find-skills`).

| Necesidad | Skill / herramienta |
|---|---|
| **Película / video / animación completa (herramienta principal)** | `hyperframes` (HeyGen: HTML → MP4, determinista, GSAP/Lottie/Three.js, audio, subtítulos). Empezar SIEMPRE por la skill `hyperframes`. |
| Video con React | `remotion-*` (oficial Remotion). Portar a HyperFrames: `remotion-to-hyperframes` |
| Animación matemática/educativa | `manim-composer`, `manimce-best-practices` |
| Lottie / motion de logos y UI | `text-to-lottie` |
| Motion de UI (Emil Kowalski) | `animate`, `emil-design-eng`, `review-animations`, `improve-animations`, `animation-vocabulary` |
| **Refinement visual a nivel de excelencia (ESTÁNDAR)** | `impeccable` (disciplina de 4 pases: layout → typeset → animate → polish). Además: `design-taste-frontend` (anti-slop, taste engineering). SIEMPRE usar antes de shipping frontend. |
| Gusto/diseño visual | `impeccable`, `design-taste-frontend`, `high-end-visual-design`, `minimalist-ui`, `brandkit`, `apple-design` |
| Metodología de trabajo | Superpowers: `brainstorming`, `writing-plans`, `test-driven-development`, `systematic-debugging` |
| Mejora continua de skills | `task-observer` (invocar al inicio de cada sesión) |
| GSAP (animación web, timelines, ScrollTrigger) | `gsap-core`, `gsap-timeline`, `gsap-scrolltrigger`, `gsap-plugins`, `gsap-react` (oficiales de GreenSock) |
| Voz, música y efectos con IA | ElevenLabs: `text-to-speech`, `music`, `sound-effects`, `speech-to-text`, `dubbing` (requiere `ELEVENLABS_API_KEY`) |
| Video/imagen generativos por API | Runway: `rw-generate-video`, `rw-generate-image`, `use-runway-api` (requiere `RUNWAYML_API_SECRET`); fal.ai: `genmedia`, `cinematography`, `storytelling`, `character-design`, `model-routing` (requiere `FAL_KEY`) |
| Todo-en-uno (agentes, hooks, 290+ skills) | plugin Everything Claude Code: `/plugin marketplace add https://github.com/affaan-m/ECC` y `/plugin install ecc@ecc` |

Requisitos de render: Node 22+, FFmpeg, Chromium (`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`).

## Dónde se aplicaron
- `mobile/App.js`, `mobile/theme.js`: UI rediseñada (animate-expo / apple-design / impeccable): paleta cálida con modo oscuro, entrada de mensajes (220 ms ease-out), feedback de pulsación (scale 0.96), indicador "escribiendo", respeta "reducir movimiento".
- `video/`: promo de 20 s con voz en español (Kokoro local, voz `ef_dora`) y música generada con MusicGen (Meta, MIT, local en CPU, `video/gen_music.py`; requiere `pip install torch transformers scipy`; respaldo sintético en `assets/music_synth.wav`). `python3 video/build.py` genera `promo/` (vertical 1080x1920) y `promo-landscape/` (horizontal 1920x1080) desde una sola plantilla. Cada carpeta: `npx hyperframes check` y `npx hyperframes render --output ../promo-vertical.mp4`. Resultados: `video/promo-vertical.mp4` y `video/promo-horizontal.mp4`.
- GSAP va en `vendor/` (el CDN falla detrás de proxies con TLS interceptado). La voz requiere `pip install kokoro-onnx soundfile` y `HYPERFRAMES_PYTHON` apuntando a ese Python.

## Visual Refinement Workflow (ESTÁNDAR OBLIGATORIO ANTES DE SHIP)

**Antes de deployar cualquier frontend UI, ejecutar:**

```bash
/impeccable layout [target]    # Fix spacing, hierarchy, rhythm
/impeccable typeset [target]   # Fix typography roles and contrast  
/impeccable animate [target]   # Add purposeful micro-interactions
/impeccable polish [target]    # Final quality pass (WCAG AA, accessibility)
```

**O usar shortcut:**
```bash
$impeccable layout frontend/
# (Commit. Luego:)
$impeccable typeset frontend/
# (Commit. Luego:)
$impeccable animate frontend/
# (Commit. Luego:)
$impeccable polish frontend/
```

**Qué se asegura:**
- ✅ Sistema de spacing coherente (4px base unit)
- ✅ Jerarquía tipográfica clara (ratios 1.5×, line-heights ajustadas)
- ✅ Micro-interacciones propositivas (feedback visual, no decoración)
- ✅ WCAG AA contrast, touch targets 14px+, reduced-motion support

**Defectos solucionados típicamente:**
- Flat type hierarchy (h1/h2/h3 mismo tamaño)
- Low contrast text (< 4.5:1)
- Spacing inconsistente (sin sistema)
- Missing input/button states (focus, disabled, loading)
- Animation sin propósito (decoración vs feedback)

## APIs externas (opcionales, de pago)
Las skills de ElevenLabs, Runway y fal.ai llaman APIs que necesitan clave. Copie `video/.env.example` a `video/.env` y complete las que vaya a usar; `.env` está en `.gitignore`. Sin claves, todo lo demás (HyperFrames, Remotion, Manim, Lottie, GSAP, TTS local Kokoro) funciona sin conexión a esas APIs.
