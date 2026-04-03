#!/bin/bash
# Data Barrens - 一键安装 skill
# 用法: curl -sL https://raw.githubusercontent.com/hilberthiggs-hash/data-barrens/main/install-remote.sh | bash

SKILL_DIR="$HOME/.claude/skills/barren"

mkdir -p "$SKILL_DIR"

curl -sL https://raw.githubusercontent.com/hilberthiggs-hash/data-barrens/main/skill/SKILL.md -o "$SKILL_DIR/SKILL.md"

if [ -f "$SKILL_DIR/SKILL.md" ] && grep -q "data-barrens" "$SKILL_DIR/SKILL.md" 2>/dev/null; then
    echo ""
    echo "⚔️  数据荒原 (Data Barrens) 安装成功！"
    echo ""
    echo "   重启 Claude Code 后输入 /barren 即可开始冒险"
    echo "   首次使用会自动注册，继承你的 Buddy 形象"
    echo ""
    echo "   常用命令："
    echo "     /barren status    查看角色"
    echo "     /barren ladder    天梯匹配"
    echo "     /barren explore   探索装备"
    echo "     /barren rank      排行榜"
    echo "     /barren help      所有命令"
    echo ""
else
    echo "❌ 安装失败，请检查网络连接"
    echo "   手动下载: https://github.com/hilberthiggs-hash/data-barrens"
    exit 1
fi
