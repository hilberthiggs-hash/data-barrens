#!/bin/bash
# 更新代码 + 重启服务（保留数据）
cd /home/barrens/data-barrens
git pull
systemctl restart data-barrens
echo "✅ 已更新并重启"
systemctl status data-barrens --no-pager | head -5
