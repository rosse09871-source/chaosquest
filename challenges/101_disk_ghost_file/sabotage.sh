#!/bin/bash
set -e

# Install needed tools if not present
apt-get update -qq >/dev/null 2>&1 || true
apt-get install -y -qq lsof procps python3 >/dev/null 2>&1 || true

# Create a rogue background process holding a deleted file
cat << 'PYEOF' > /usr/local/bin/legacy_logger.py
import time
import os

filepath = "/var/log/app_ghost.log"
with open(filepath, "w") as f:
    # Write some initial padding
    for i in range(1000):
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Critical trace dump payload chunk {i}...\n")
    f.flush()
    # Keep holding the file descriptor open forever
    while True:
        f.write(f"Heartbeat tick: {time.time()}\n")
        f.flush()
        time.sleep(2)
PYEOF

chmod +x /usr/local/bin/legacy_logger.py

# Launch the rogue process in background
nohup python3 /usr/local/bin/legacy_logger.py >/dev/null 2>&1 &
ROGUE_PID=$!

# Wait for file creation
sleep 1

# Delete the file from filesystem (creating unlinked open file descriptor)
rm -f /var/log/app_ghost.log

echo "Stage 101 Sabotage completed. Ghost process PID: $ROGUE_PID"
