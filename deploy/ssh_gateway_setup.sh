#!/bin/bash
# ==========================================================
# 🚪 ChaosQuest - Public SSH Gateway & Restricted Shell Setup
# Allows anyone to run `ssh play@<server_ip>` to play directly
# ==========================================================
set -e

PROJECT_DIR="/opt/chaosquest"
APP_USER="play"

echo "👤 [1/3] Creating restricted play user..."
if ! id -u "$APP_USER" >/dev/null 2>&1; then
    sudo useradd -m -s /usr/local/bin/chaosquest-entry "$APP_USER" || true
fi

# Ensure user is in docker group to control sandboxes
sudo usermod -aG docker "$APP_USER"

echo "⚙️ [2/3] Creating launcher wrapper /usr/local/bin/chaosquest-entry..."
sudo bash -c "cat << 'LAUNCHER' > /usr/local/bin/chaosquest-entry
#!/bin/bash
export TERM=xterm-256color
cd $PROJECT_DIR
exec $PROJECT_DIR/.venv/bin/python -m app.main
LAUNCHER"

sudo chmod +x /usr/local/bin/chaosquest-entry

echo "🔑 [3/3] Allowing passwordless/keyless public guest login (Optional)..."
# In sshd_config, you can add:
# Match User play
#     PasswordAuthentication yes
#     PermitEmptyPasswords yes

echo "✅ SSH Gateway setup completed! Users can connect with: ssh play@<IP>"
