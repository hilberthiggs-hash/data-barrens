#!/bin/bash
# Data Barrens - Debian 11 一键部署脚本
# 用法: ssh root@your-vps 'bash -s' < setup.sh

set -e

echo "=== 1. 安装依赖 ==="
apt-get update
apt-get install -y python3 python3-venv python3-pip git nginx certbot python3-certbot-nginx

echo "=== 2. 创建应用用户 ==="
id -u barrens &>/dev/null || useradd -m -s /bin/bash barrens

echo "=== 3. 拉取代码 ==="
cd /home/barrens
if [ -d data-barrens ]; then
    cd data-barrens && git pull
else
    git clone https://github.com/hilberthiggs-hash/data-barrens.git
    cd data-barrens
fi

echo "=== 4. 创建 venv 并安装依赖 ==="
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

echo "=== 5. 设置权限 ==="
chown -R barrens:barrens /home/barrens/data-barrens

echo "=== 6. 创建 systemd 服务 ==="
cat > /etc/systemd/system/data-barrens.service << 'UNIT'
[Unit]
Description=Data Barrens Game Server
After=network.target

[Service]
Type=simple
User=barrens
WorkingDirectory=/home/barrens/data-barrens
ExecStart=/home/barrens/data-barrens/venv/bin/uvicorn server.main:app --host 127.0.0.1 --port 19820
Restart=always
RestartSec=5
Environment=ARENA_DB_PATH=/home/barrens/data-barrens/arena.db

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable data-barrens
systemctl restart data-barrens

echo "=== 7. 配置 Nginx 反代 ==="
cat > /etc/nginx/sites-available/barrens << 'NGINX'
server {
    listen 80;
    server_name barrens.hilberthiggs.com;

    location / {
        proxy_pass http://127.0.0.1:19820;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/barrens /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

echo "=== 8. 申请 SSL 证书 ==="
certbot --nginx -d barrens.hilberthiggs.com --non-interactive --agree-tos --register-unsafely-without-email || echo "SSL 暂未配置，等 DNS 生效后再运行: certbot --nginx -d barrens.hilberthiggs.com"

echo ""
echo "✅ 部署完成！"
echo "   服务状态: systemctl status data-barrens"
echo "   查看日志: journalctl -u data-barrens -f"
echo "   测试: curl http://127.0.0.1:19820/api/health"
echo ""
echo "后续更新: cd /home/barrens/data-barrens && git pull && systemctl restart data-barrens"
