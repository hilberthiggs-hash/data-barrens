#!/bin/bash
# Data Barrens — Claude Code Skill Installer
# Usage:
#   bash install.sh                          # Public server (default)
#   bash install.sh https://my-server:8000   # Self-hosted server

SKILL_DIR="$HOME/.claude/skills/barren"
REPO_URL="https://raw.githubusercontent.com/hilberthiggs-hash/data-barrens/main/skill/SKILL.md"
DEFAULT_SERVER="https://barrens.hilberthiggs.com"
CUSTOM_SERVER="${1:-}"

mkdir -p "$SKILL_DIR"
curl -sL "$REPO_URL" -o "$SKILL_DIR/SKILL.md"

if [ -n "$CUSTOM_SERVER" ]; then
    sed -i.bak "s|$DEFAULT_SERVER|$CUSTOM_SERVER|g" "$SKILL_DIR/SKILL.md"
    rm -f "$SKILL_DIR/SKILL.md.bak"
    echo "✅ Installed (server: $CUSTOM_SERVER)"
else
    echo "✅ Installed (server: $DEFAULT_SERVER)"
fi
echo "   Restart Claude Code, then type /barren"
