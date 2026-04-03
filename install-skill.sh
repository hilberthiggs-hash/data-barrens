#!/bin/bash
# 安装 Data Barrens skill 到 Claude Code
SKILL_DIR="$HOME/.claude/skills/data-barrens"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$HOME/.claude/skills"
rm -rf "$SKILL_DIR"
ln -s "$SCRIPT_DIR/skill" "$SKILL_DIR"

echo "✅ Data Barrens skill 已安装到 $SKILL_DIR"
echo "   重启 Claude Code 后输入 /game help 即可使用"
