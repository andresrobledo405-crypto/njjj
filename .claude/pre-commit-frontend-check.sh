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
