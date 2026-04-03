#!/bin/bash
# 仅重启服务（不更新代码）
systemctl restart data-barrens
echo "✅ 已重启"
systemctl status data-barrens --no-pager | head -5
