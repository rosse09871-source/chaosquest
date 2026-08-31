#!/bin/bash
# ==========================================
# ☁️ ChaosQuest - AWS EC2 Ubuntu Initial Setup
# ==========================================
set -e

echo "🚀 [1/4] Updating package index..."
sudo apt-get update -qq
sudo apt-get install -y -qq git curl ca-certificates gnupg python3 python3-pip python3-venv

echo "🐳 [2/4] Installing Docker..."
if ! command -v docker >/dev/null 2>&1; then
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update -qq
    sudo apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi

# Add current user to docker group
sudo usermod -aG docker "$USER"

echo "🐍 [3/4] Setting up Python virtual environment for ChaosQuest..."
cd "$(dirname "$0")/.."
python3 -m venv .venv
.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -r requirements.txt -q

echo "✅ [4/4] Setup complete! ChaosQuest is ready to run with: .venv/bin/python -m app.main"
