#!/bin/bash
# 回档：删库重建（所有玩家数据清零）
read -p "⚠️  确认删除所有玩家数据？(y/N) " confirm
if [ "$confirm" != "y" ]; then
    echo "已取消"
    exit 0
fi
cd /home/barrens/data-barrens
systemctl stop data-barrens
rm -f arena.db
systemctl start data-barrens
echo "✅ 已回档，数据已清零，NPC 已重新初始化"
