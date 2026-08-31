#!/bin/bash
# ==========================================================
# 🌐 ChaosQuest - Web TTY (ttyd) Daemon Setup
# Serves pure terminal directly into browser at port 7681
# ==========================================================
set -e

echo "📦 [1/2] Installing ttyd (Web Terminal)..."
if ! command -v ttyd >/dev/null 2>&1; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq ttyd || {
        echo "Building or downloading binary directly..."
        sudo curl -fsSL -o /usr/local/bin/ttyd https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.x86_64
        sudo chmod +x /usr/local/bin/ttyd
    }
fi

echo "⚙️ [2/2] Registering ttyd systemd background service..."
sudo bash -c "cat << 'SERVICE' > /etc/systemd/system/chaosquest-web.service
[Unit]
Description=ChaosQuest Web Terminal Gateway
After=network.target

[Service]
Type=simple
User=play
WorkingDirectory=/opt/chaosquest
ExecStart=/usr/local/bin/ttyd -p 7681 -t fontSize=16 -t theme={'background':'#1e1e1e'} /usr/local/bin/chaosquest-entry
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICE"

sudo systemctl daemon-reload
sudo systemctl enable --now chaosquest-web.service

echo "✅ Web Terminal gateway started on port 7681!"
