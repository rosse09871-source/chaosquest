#!/bin/bash
set -e
which lsof >/dev/null 2>&1 || { apt-get update -qq >/dev/null 2>&1 || true ; apt-get install -y -qq lsof procps python3 >/dev/null 2>&1 || true ; }

cat << 'PYEOF' > /usr/local/bin/legacy_logger.py
import os, sys, time
if os.fork() > 0: sys.exit(0)
os.setsid()
if os.fork() > 0: sys.exit(0)

filepath = "/var/log/app_ghost.log"
f = open(filepath, "w")
for i in range(500):
    f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Dump payload chunk {i}...\n")
f.flush()
if os.path.exists(filepath): os.unlink(filepath)
while True:
    f.write(f"tick: {time.time()}\n")
    f.flush()
    time.sleep(1)
PYEOF

chmod +x /usr/local/bin/legacy_logger.py
python3 /usr/local/bin/legacy_logger.py
echo "101-1 Sabotage completed."
