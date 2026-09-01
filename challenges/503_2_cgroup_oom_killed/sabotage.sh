#!/bin/bash
set -e
which python3 >/dev/null 2>&1 || { apt-get update -qq >/dev/null 2>&1 || true ; apt-get install -y -qq python3 procps >/dev/null 2>&1 || true ; }

cat << 'PYEOF' > /usr/local/bin/queue_worker.py
import time, os

ENABLE_LEAK = True
data_sink = []

while True:
    if ENABLE_LEAK:
        # Simulate memory leak chunk
        data_sink.append(b"X" * (1024 * 512)) # 512KB leak per second
    time.sleep(1)
PYEOF

chmod +x /usr/local/bin/queue_worker.py
nohup python3 /usr/local/bin/queue_worker.py >/dev/null 2>&1 &
echo "503-2 Sabotage completed."
