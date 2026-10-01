# Toolkit de diseño, animación y cine

Skills instaladas en `.claude/skills/` (actualizar: `npx skills update`; buscar más: skill `find-skills`).

| Necesidad | Skill / herramienta |
|---|---|
| **Película / video / animación completa (herramienta principal)** | `hyperframes` (HeyGen: HTML → MP4, determinista, GSAP/Lottie/Three.js, audio, subtítulos). Empezar SIEMPRE por la skill `hyperframes`. |
| Video con React | `remotion-*` (oficial Remotion). Portar a HyperFrames: `remotion-to-hyperframes` |
| Animación matemática/educativa | `manim-composer`, `manimce-best-practices` |
| Lottie / motion de logos y UI | `text-to-lottie` |
| Motion de UI (Emil Kowalski) | `animate`, `emil-design-eng`, `review-animations`, `improve-animations`, `animation-vocabulary` |
| Gusto/diseño visual | `impeccable`, `design-taste-frontend`, `high-end-visual-design`, `minimalist-ui`, `brandkit`, `apple-design` |
| Metodología de trabajo | Superpowers: `brainstorming`, `writing-plans`, `test-driven-development`, `systematic-debugging` |
| Mejora continua de skills | `task-observer` (invocar al inicio de cada sesión) |
| Todo-en-uno (agentes, hooks, 290+ skills) | plugin Everything Claude Code: `/plugin marketplace add https://github.com/affaan-m/ECC` y `/plugin install ecc@ecc` |

Requisitos de render: Node 22+, FFmpeg, Chromium (`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`).
