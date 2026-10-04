# 🤖 Impeccable Automation - Zero Intervention

Todo está configurado para ejecutarse automáticamente. **No necesitas hacer nada más.**

## ⚙️ Lo que se Instaló

✅ **Git Hooks** - Se ejecutan automáticamente
- `post-commit`: Detecta cambios en frontend/ después de cada commit
- Pre-commit validation: Valida calidad antes de commitear

✅ **Makefile** - Comandos listos para usar
- `make impeccable` - Ejecuta los 4 pases completos
- `make frontend-ship` - Prepara frontend para production

✅ **Shell Aliases** - Atajos rápidos
- `imp-full` - Corre todos los pases
- `imp-detect` - Checa defectos

✅ **Settings** - Configuración centralizada
- `.claude/settings.json` - Criterios de aceptación
- `.claude/impeccable-aliases.sh` - Aliases
- `.claude/VISUAL_REFINEMENT.md` - Quick reference

---

## 🚀 Workflow Recomendado

### Opción 1: Make (Más simple)
```bash
# Antes de hacer push/deploy:
cd /home/user/njjj
make impeccable
```

**Qué hace:**
1. Layout pass (spacing, hierarchy, rhythm)
2. Typeset pass (typography, contrast, measure)
3. Animate pass (micro-interactions, feedback)
4. Polish pass (WCAG AA, final quality)
5. Auto-commit cada paso

### Opción 2: Aliases (Más rápido)
```bash
# Load aliases
source /home/user/njjj/.claude/impeccable-aliases.sh

# Run full workflow
imp-full

# O por paso:
imp-layout
imp-typeset
imp-animate
imp-polish
```

### Opción 3: Manual en Claude Code
```bash
/impeccable layout frontend/
/impeccable typeset frontend/
/impeccable animate frontend/
/impeccable polish frontend/
```

---

## 🔄 Git Hooks (Automático - Sin hacer nada)

Instalados en `.git/hooks/`:

**Post-Commit Hook:**
```bash
# Se ejecuta DESPUÉS de cada commit
# Si detecta cambios en frontend/
# ➡️ Ejecuta: impeccable detect --json
# ➡️ Imprime defectos (si hay)
```

Esto significa: **Cada vez que haces commit a frontend/, automáticamente se chequea la calidad**.

---

## ✨ Aceptación Criterios

Para que un frontend esté listo para ship, debe cumplir:

| Criterio | Estándar |
|----------|----------|
| **Contrast** | WCAG AA (4.5:1 mínimo) |
| **Spacing** | 4px base unit system |
| **Typography** | 1.5× scale (display→body→small) |
| **Touch targets** | 14px mínimo |
| **States** | focus, hover, active, disabled, loading, error |
| **Motion** | Prefers-reduced-motion respected |
| **Line-height** | Ajustada por role (1.2-1.6) |
| **Measure** | Max 65ch para body |

---

## 🎯 Quick Start (Hoy)

```bash
# 1. Una sola vez:
cd /home/user/njjj
bash .claude/setup-impeccable.sh

# 2. Luego, cualquier tiempo:
make impeccable

# 3. Si todo está ✅:
git push
```

---

## 📋 Checklist antes de Ship

- [ ] Run `make impeccable` (o `imp-full`)
- [ ] Check output para defectos
- [ ] Si hay defectos → se fixean automáticamente
- [ ] Review los commits de refinement
- [ ] `git push`

---

## 🛠️ Troubleshooting

**Si el hook no se ejecuta:**
```bash
# Verificar hook:
cat .git/hooks/post-commit

# Hacer executable:
chmod +x .git/hooks/post-commit
```

**Si necesitas deshabilitar temporalmente:**
```bash
# Renombra el hook:
mv .git/hooks/post-commit .git/hooks/post-commit.disabled

# Restore:
mv .git/hooks/post-commit.disabled .git/hooks/post-commit
```

**Si quieres ver defectos sin fijar:**
```bash
make impeccable-detect
```

---

## 🚀 Próximas Sesiones

Todo está automatizado. **Simplemente:**

```bash
cd /home/user/njjj
make impeccable    # ← Haz esto antes de push
git push
```

No necesitas correr setup de nuevo. Los hooks, aliases y settings están instalados permanentemente.

---

## 📚 Referencias

- `.claude/VISUAL_REFINEMENT.md` - Quick reference
- `CLAUDE.md` - Project standards
- `.claude/settings.json` - Configuration
- `Makefile` - Available commands

✅ **Listo. Todo automatizado. Sin intervención manual necesaria.**
