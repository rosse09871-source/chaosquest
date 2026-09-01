#!/bin/bash
set -e
cat << 'SHEOF' > /usr/local/bin/start_indexer.sh
#!/bin/bash
ulimit -n 64 2>/dev/null || true
cat << 'PYEOF' > /usr/local/bin/indexer.py
import os, sys, time, socket
LOG = "/var/log/indexer.log"
def log(m):
    with open(LOG, "a") as f: f.write(f"{m}\n")
log("Initializing Indexer...")
sockets = []
try:
    for i in range(120):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockets.append(s)
except Exception as e:
    log(f"CRITICAL FD ERROR: {e}")
    sys.exit(1)

if os.fork() > 0: sys.exit(0)
os.setsid()
if os.fork() > 0: sys.exit(0)
log("Indexer initialized successfully with 120 sockets OK")
while True:
    time.sleep(1)
PYEOF
python3 /usr/local/bin/indexer.py
SHEOF
chmod +x /usr/local/bin/start_indexer.sh
/usr/local/bin/start_indexer.sh || true
echo "202-3 Sabotage completed."
