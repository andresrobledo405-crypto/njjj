#!/bin/bash
# Impeccable Visual Refinement - Automated Setup
# Ejecutar una sola vez: bash .claude/setup-impeccable.sh

set -e

echo "🎨 Setting up Impeccable Visual Refinement..."

# 1. Create git hook for auto-detection
echo "📝 Creating git post-commit hook..."
mkdir -p .git/hooks

cat > .git/hooks/post-commit << 'EOF'
#!/bin/bash
# Auto-run impeccable detector after commits to frontend

if git diff-tree --no-commit-id --name-only -r HEAD | grep -q "frontend/"; then
  echo "🔍 Running Impeccable detector on frontend changes..."
  /home/user/njjj/.claude/skills/impeccable/scripts/impeccable detect --json frontend/ 2>/dev/null || true
fi
EOF

chmod +x .git/hooks/post-commit
echo "✅ Git hook installed"

# 2. Create shell aliases
echo "⚡ Creating shell aliases..."

cat > .claude/impeccable-aliases.sh << 'EOF'
#!/bin/bash
# Quick aliases for impeccable workflow

alias imp-layout="/home/user/njjj/.claude/skills/impeccable/scripts/impeccable layout frontend/ && git add frontend/styles.css && git commit -m 'refactor: impeccable layout'"
alias imp-typeset="/home/user/njjj/.claude/skills/impeccable/scripts/impeccable typeset frontend/ && git add frontend/styles.css && git commit -m 'refactor: impeccable typeset'"
alias imp-animate="/home/user/njjj/.claude/skills/impeccable/scripts/impeccable animate frontend/ && git add frontend/styles.css && git commit -m 'refactor: impeccable animate'"
alias imp-polish="/home/user/njjj/.claude/skills/impeccable/scripts/impeccable polish frontend/ && git add frontend/styles.css && git commit -m 'refactor: impeccable polish'"
alias imp-full="imp-layout && imp-typeset && imp-animate && imp-polish"
alias imp-detect="/home/user/njjj/.claude/skills/impeccable/scripts/impeccable detect --json frontend/"

echo "✅ Aliases ready. Load them: source .claude/impeccable-aliases.sh"
EOF

chmod +x .claude/impeccable-aliases.sh
echo "✅ Aliases created"

# 3. Create Makefile for common tasks
echo "📋 Creating Makefile..."

cat > Makefile << 'EOF'
.PHONY: impeccable impeccable-layout impeccable-typeset impeccable-animate impeccable-polish impeccable-detect frontend-check frontend-ship

# Quick visual refinement
impeccable-layout:
	@/home/user/njjj/.claude/skills/impeccable/scripts/impeccable layout frontend/
	@git add frontend/styles.css
	@git commit -m "refactor: impeccable layout - spacing system"

impeccable-typeset:
	@/home/user/njjj/.claude/skills/impeccable/scripts/impeccable typeset frontend/
	@git add frontend/styles.css
	@git commit -m "refactor: impeccable typeset - typography hierarchy"

impeccable-animate:
	@/home/user/njjj/.claude/skills/impeccable/scripts/impeccable animate frontend/
	@git add frontend/styles.css
	@git commit -m "refactor: impeccable animate - micro-interactions"

impeccable-polish:
	@/home/user/njjj/.claude/skills/impeccable/scripts/impeccable polish frontend/
	@git add frontend/styles.css
	@git commit -m "refactor: impeccable polish - final quality pass"

# Run all 4 passes in sequence
impeccable: impeccable-layout impeccable-typeset impeccable-animate impeccable-polish
	@echo "✅ Frontend refined to production excellence"

# Detect defects
impeccable-detect:
	@/home/user/njjj/.claude/skills/impeccable/scripts/impeccable detect --json frontend/

# Checks before shipping
frontend-check: impeccable-detect
	@echo "✅ Frontend quality checks complete"

# Ship frontend to production
frontend-ship: impeccable frontend-check
	@echo "🚀 Frontend ready to ship"
	@git log --oneline -4
EOF

echo "✅ Makefile created"

# 4. Create settings.json configuration
echo "🔧 Updating settings.json..."

cat > .claude/settings.json << 'EOF'
{
  "design": {
    "visual_refinement": "impeccable",
    "required_before_ship": true,
    "workflow": [
      "layout",
      "typeset",
      "animate",
      "polish"
    ],
    "acceptance_criteria": {
      "typography": "WCAG AA contrast (4.5:1 min)",
      "spacing": "4px base unit system",
      "touch_targets": "14px minimum",
      "reduced_motion": "respected",
      "states": "focus, hover, active, disabled, loading, error"
    }
  },
  "skills_enabled": {
    "impeccable": true,
    "design_taste_frontend": true,
    "emil_design_eng": true,
    "review_animations": true
  }
}
EOF

echo "✅ Settings configured"

# 5. Create CI/CD pre-commit hook
echo "🔐 Creating pre-commit validation..."

cat > .claude/pre-commit-frontend-check.sh << 'EOF'
#!/bin/bash
# Runs before committing to catch quality issues early

FRONTEND_CHANGED=$(git diff --cached --name-only | grep -c "frontend/" || true)

if [ "$FRONTEND_CHANGED" -gt 0 ]; then
  echo "🔍 Running impeccable detector on staged frontend changes..."
  /home/user/njjj/.claude/skills/impeccable/scripts/impeccable detect --json frontend/ || {
    echo "⚠️  Quality issues detected. Fix them before committing."
    exit 1
  }
fi

exit 0
EOF

chmod +x .claude/pre-commit-frontend-check.sh
echo "✅ Pre-commit validation installed"

# 6. Summary
echo ""
echo "=========================================="
echo "✨ Impeccable Setup Complete!"
echo "=========================================="
echo ""
echo "Available commands:"
echo "  make impeccable              # Run all 4 passes"
echo "  make impeccable-layout       # Layout pass only"
echo "  make impeccable-typeset      # Typeset pass only"
echo "  make impeccable-animate      # Animate pass only"
echo "  make impeccable-polish       # Polish pass only"
echo "  make impeccable-detect       # Detect issues"
echo "  make frontend-ship           # Full check + ship"
echo ""
echo "Or use aliases:"
echo "  source .claude/impeccable-aliases.sh"
echo "  imp-full    # Run all 4 passes"
echo "  imp-detect  # Check for issues"
echo ""
echo "Git hooks installed:"
echo "  • post-commit: Auto-detect frontend changes"
echo "  • pre-commit: Validate before committing"
echo ""
echo "✅ Ready to use! Start with: make impeccable"
echo ""
