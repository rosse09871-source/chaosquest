#!/bin/bash
set -e
cat << 'CONFEOF' > /etc/chaos_app.conf
APP_NAME=PaymentGateway
DB_HOST=127.0.0.1
PORT_NUMBER=NOT_A_VALID_NUMBER_PORT_ERROR
WORKERS=4
CONFEOF

cat << 'PYEOF' > /usr/local/bin/payment_service.py
import os, sys, time
LOG_FILE = "/var/log/payment_service.log"
def log(msg):
    with open(LOG_FILE, "a") as f: f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
log("Starting Payment Service...")
if not os.path.exists("/etc/chaos_app.conf"): sys.exit(1)
config = {}
with open("/etc/chaos_app.conf") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            k, v = line.split("=", 1)
            config[k.strip()] = v.strip()
try:
    port = int(config.get("PORT_NUMBER", ""))
except Exception as e:
    log(f"CRITICAL ERROR: Failed to parse PORT_NUMBER '{config.get('PORT_NUMBER')}'! Error: {e}")
    sys.exit(1)
if os.fork() > 0: sys.exit(0)
os.setsid()
if os.fork() > 0: sys.exit(0)
log(f"Payment Service successfully started and listening on port {port}!")
while True:
    log(f"Payment heartbeat tick OK. Port={port}")
    time.sleep(2)
PYEOF
chmod +x /usr/local/bin/payment_service.py

cat << 'SHEOF' > /usr/local/bin/start_payment_service.sh
#!/bin/bash
python3 /usr/local/bin/payment_service.py
SHEOF
chmod +x /usr/local/bin/start_payment_service.sh
python3 /usr/local/bin/payment_service.py || true
echo "202-1 Sabotage completed."
