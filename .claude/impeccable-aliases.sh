#!/bin/bash
# Quick aliases for impeccable workflow

alias imp-layout="/home/user/njjj/.claude/skills/impeccable/scripts/impeccable layout frontend/ && git add frontend/styles.css && git commit -m 'refactor: impeccable layout'"
alias imp-typeset="/home/user/njjj/.claude/skills/impeccable/scripts/impeccable typeset frontend/ && git add frontend/styles.css && git commit -m 'refactor: impeccable typeset'"
alias imp-animate="/home/user/njjj/.claude/skills/impeccable/scripts/impeccable animate frontend/ && git add frontend/styles.css && git commit -m 'refactor: impeccable animate'"
alias imp-polish="/home/user/njjj/.claude/skills/impeccable/scripts/impeccable polish frontend/ && git add frontend/styles.css && git commit -m 'refactor: impeccable polish'"
alias imp-full="imp-layout && imp-typeset && imp-animate && imp-polish"
alias imp-detect="/home/user/njjj/.claude/skills/impeccable/scripts/impeccable detect --json frontend/"

echo "✅ Aliases ready. Load them: source .claude/impeccable-aliases.sh"
