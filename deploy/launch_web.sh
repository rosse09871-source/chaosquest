#!/bin/bash
# ==========================================================
# 🚀 ChaosQuest - 1-Click Production Web Launch (ttyd + Nginx)
# ==========================================================
set -e

DIR="$(cd "$(dirname "$0")/.." && pwd)"
echo "📍 Current ChaosQuest root: $DIR"

echo "📦 [1/3] Installing Nginx..."
sudo apt-get update -qq
sudo apt-get install -y -qq nginx curl >/dev/null

echo "⚙️ [2/3] Registering systemd background service (FastAPI Web GUI)..."
sudo bash -c "cat << 'SERVICE' > /etc/systemd/system/chaosquest-web.service
[Unit]
Description=ChaosQuest Modern Web Arena Gateway (FastAPI + Uvicorn)
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=$DIR
ExecStart=$DIR/.venv/bin/uvicorn app.web.server:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICE"

sudo systemctl daemon-reload
sudo systemctl enable --now chaosquest-web.service
sudo systemctl restart chaosquest-web.service

echo "🌐 [4/4] Configuring Nginx reverse proxy on Port 80..."
sudo cp "$DIR/deploy/nginx.conf" /etc/nginx/sites-available/default
sudo nginx -t
sudo systemctl restart nginx

PUBLIC_IP=$(curl -s --connect-timeout 2 ifconfig.me || curl -s --connect-timeout 2 icanhazip.com || echo "<Your-EC2-Public-IP>")

echo ""
echo "=========================================================="
echo "🎉 ChaosQuest is LIVE on AWS! 🚀"
echo "👉 Web Browser URL: http://$PUBLIC_IP/"
echo "=========================================================="
