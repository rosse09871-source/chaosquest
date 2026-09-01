#!/bin/bash
# ==========================================================
# 🚀 ChaosQuest - 1-Click Production Web Launch (ttyd + Nginx)
# ==========================================================
set -e

DIR="$(cd "$(dirname "$0")/.." && pwd)"
echo "📍 Current ChaosQuest root: $DIR"

echo "📦 [1/4] Installing ttyd & Nginx..."
sudo apt-get update -qq
sudo apt-get install -y -qq nginx curl >/dev/null

if ! command -v ttyd >/dev/null 2>&1; then
    echo "Downloading ttyd binary..."
    sudo curl -fsSL -o /usr/local/bin/ttyd https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.x86_64
    sudo chmod +x /usr/local/bin/ttyd
fi

echo "⚙️ [2/4] Registering launcher wrapper /usr/local/bin/chaosquest-entry..."
sudo bash -c "cat << 'LAUNCHER' > /usr/local/bin/chaosquest-entry
#!/bin/bash
export TERM=xterm-256color
cd $DIR
exec $DIR/.venv/bin/python -m app.main
LAUNCHER"
sudo chmod +x /usr/local/bin/chaosquest-entry

echo "⚙️ [3/4] Registering systemd background service..."
sudo bash -c "cat << 'SERVICE' > /etc/systemd/system/chaosquest-web.service
[Unit]
Description=ChaosQuest Web Terminal Gateway
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=$DIR
ExecStart=/usr/local/bin/ttyd -p 7681 -W -t fontSize=16 -t theme={'background':'#1e1e1e'} /usr/local/bin/chaosquest-entry
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
