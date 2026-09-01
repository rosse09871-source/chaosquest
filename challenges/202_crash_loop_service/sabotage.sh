#!/bin/bash
set -e

apt-get update -qq >/dev/null 2>&1 || true
apt-get install -y -qq procps python3 >/dev/null 2>&1 || true

# 1. Create broken config
cat << 'CONFEOF' > /etc/chaos_app.conf
# Chaos Payment Service Configuration
APP_NAME=PaymentGateway
DB_HOST=127.0.0.1
PORT_NUMBER=NOT_A_VALID_NUMBER_PORT_ERROR
WORKERS=4
CONFEOF

# 2. Create the service script
cat << 'PYEOF' > /usr/local/bin/payment_service.py
import os, sys, time

LOG_FILE = "/var/log/payment_service.log"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

log("Starting Payment Service...")

# Read config
if not os.path.exists("/etc/chaos_app.conf"):
    log("FATAL: /etc/chaos_app.conf not found!")
    sys.exit(1)

config = {}
with open("/etc/chaos_app.conf") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            k, v = line.split("=", 1)
            config[k.strip()] = v.strip()

# Validate port
try:
    port = int(config.get("PORT_NUMBER", ""))
except Exception as e:
    log(f"CRITICAL ERROR: Failed to parse PORT_NUMBER '{config.get('PORT_NUMBER')}' as integer! Error: {e}")
    log("Application shutting down with exit code 1.")
    sys.exit(1)

# Double-fork daemon if valid
if os.fork() > 0:
    sys.exit(0)
os.setsid()
if os.fork() > 0:
    sys.exit(0)

log(f"Payment Service successfully started and listening on port {port}!")
while True:
    log(f"Payment heartbeat tick OK. Port={port}")
    time.sleep(2)
PYEOF

chmod +x /usr/local/bin/payment_service.py

# 3. Create start script
cat << 'SHEOF' > /usr/local/bin/start_payment_service.sh
#!/bin/bash
python3 /usr/local/bin/payment_service.py
SHEOF
chmod +x /usr/local/bin/start_payment_service.sh

# Run once so it creates the crash log
python3 /usr/local/bin/payment_service.py || true

echo "Stage 202 Sabotage completed. Payment service crashed on boot."
