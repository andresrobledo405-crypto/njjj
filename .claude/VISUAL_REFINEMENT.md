# Visual Refinement Workflow

## Estándar de Excelencia Obligatorio

**SIEMPRE ejecutar este workflow antes de hacer push a `main` o deploy:**

```bash
# 1. Layout: Spacing system, hierarchy, rhythm
/impeccable layout frontend/

# 2. Typeset: Typography hierarchy, contrast, reading comfort  
/impeccable typeset frontend/

# 3. Animate: Purposeful micro-interactions, feedback
/impeccable animate frontend/

# 4. Polish: Final quality pass, accessibility compliance
/impeccable polish frontend/
```

## Lo que se Asegura

✅ **Spacing System**
- 4px base unit → 8-64px scale
- Rhythm coherente (tight/generous intervals)
- Grid gaps, padding, margins consistentes

✅ **Typography**
- Jerarquía clara (ratios 1.5×)
- Display 3.5rem → Body 1rem → Small 0.875rem
- Line-heights ajustadas (display 1.2, body 1.6)
- Measure max 65ch para lectura cómoda
- Contraste WCAG AA (4.5:1 body, 3:1 large)

✅ **Micro-Interactions**
- Button states: default, hover, active, disabled, loading
- Input focus: visible, colored shadow
- Transitions: 150-300ms, cubic-bezier(0.16, 1, 0.3, 1)
- Prefers-reduced-motion: motion meaningful, not decorative

✅ **Accessibility**
- WCAG AA contrast en todos los estados
- Touch targets 14px+ mínimo
- Focus visible, tab order lógico
- Disabled/loading/empty/error states completos

## Defectos Típicos Detectados

| Problema | Solución |
|----------|----------|
| Flat type hierarchy | Aplicar scale 1.5× (h1 2.25rem, body 1rem) |
| Low contrast text | Aumentar saturación: #9ca3af → #6b7280 |
| Spacing inconsistente | Usar 4px base unit system |
| Missing states | Agregar focus, disabled, active, loading |
| Animation sin propósito | Remover decoración, mantener feedback |
| Placeholder contrast bajo | Aumentar: #9ca3af → #6b7280 |

## Commits por Paso

```bash
# Paso 1
git commit -m "refactor: impeccable layout - spacing system and visual hierarchy"

# Paso 2
git commit -m "refactor: impeccable typeset - establish hierarchy and reading comfort"

# Paso 3
git commit -m "refactor: impeccable animate - add purposeful micro-interactions"

# Paso 4
git commit -m "refactor: impeccable polish - final quality pass"
```

## Validación Final

Antes de cada paso, ejecutar detector:
```bash
/home/user/njjj/.claude/skills/impeccable/scripts/impeccable detect --json frontend/
```

Todos los defectos deben estar en 0 antes de ship.

---

**Nota:** Este workflow es OBLIGATORIO en Repurpose AI SaaS.
No shipear frontend sin pasar los 4 pases de impeccable.
