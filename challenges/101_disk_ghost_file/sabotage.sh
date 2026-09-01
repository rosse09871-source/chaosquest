#!/bin/bash
set -e

apt-get update -qq >/dev/null 2>&1 || true
apt-get install -y -qq lsof procps python3 >/dev/null 2>&1 || true

# Create a true detached background daemon using Unix double-fork
cat << 'PYEOF' > /usr/local/bin/legacy_logger.py
import os
import sys
import time

# 1. First fork (detaches from parent)
if os.fork() > 0:
    sys.exit(0)

# 2. Create new session and become session leader
os.setsid()

# 3. Second fork (prevents acquiring a controlling terminal)
if os.fork() > 0:
    sys.exit(0)

# 4. Reparented to PID 1: Open file descriptor and delete file
filepath = "/var/log/app_ghost.log"
f = open(filepath, "w")
for i in range(500):
    f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Dump payload chunk {i}...\n")
f.flush()

# Delete file name from filesystem (unlinked open FD)
if os.path.exists(filepath):
    os.unlink(filepath)

# Keep writing and holding file descriptor open forever
while True:
    f.write(f"Heartbeat tick: {time.time()}\n")
    f.flush()
    time.sleep(1)
PYEOF

chmod +x /usr/local/bin/legacy_logger.py

# Execute python daemon
python3 /usr/local/bin/legacy_logger.py

echo "Stage 101 Sabotage completed. Ghost daemon is now running in background."
