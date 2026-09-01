#!/bin/bash
set -e
cat << 'JSONEOF' > /etc/auth_config.json
{
  "service": "auth",
  "port": 9100,
  "secret_key": "chaos_secret",
}
JSONEOF

cat << 'PYEOF' > /usr/local/bin/auth_service.py
import json, os, sys, time
LOG = "/var/log/auth_service.log"
def log(m):
    with open(LOG, "a") as f: f.write(f"{m}\n")
try:
    with open("/etc/auth_config.json") as f:
        cfg = json.load(f)
except Exception as e:
    log(f"CRITICAL JSON ERROR: {e}")
    sys.exit(1)

if os.fork() > 0: sys.exit(0)
os.setsid()
if os.fork() > 0: sys.exit(0)
log(f"Auth Service started on port {cfg['port']} OK")
while True:
    time.sleep(1)
PYEOF
chmod +x /usr/local/bin/auth_service.py
python3 /usr/local/bin/auth_service.py || true
echo "202-2 Sabotage completed."
