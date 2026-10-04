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
