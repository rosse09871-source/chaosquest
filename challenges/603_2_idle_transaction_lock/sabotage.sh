#!/bin/bash
set -e
which python3 >/dev/null 2>&1 || { apt-get update -qq >/dev/null 2>&1 || true ; apt-get install -y -qq python3 procps >/dev/null 2>&1 || true ; }

cat << 'PYEOF' > /usr/local/bin/zombie_tx.py
import time, os
# Simulate holding exclusive row lock
while True:
    time.sleep(10)
PYEOF

chmod +x /usr/local/bin/zombie_tx.py
nohup python3 /usr/local/bin/zombie_tx.py >/dev/null 2>&1 &
echo "603-2 Sabotage completed."
