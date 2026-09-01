#!/bin/bash
set -e
which python3 >/dev/null 2>&1 || { apt-get update -qq >/dev/null 2>&1 || true ; apt-get install -y -qq python3 procps >/dev/null 2>&1 || true ; }

cat << 'PYEOF' > /usr/local/bin/rogue_query_runner.py
import time, math
while True:
    for _ in range(1000000):
        math.sqrt(123456.789)
    time.sleep(0.01)
PYEOF

chmod +x /usr/local/bin/rogue_query_runner.py
nohup python3 /usr/local/bin/rogue_query_runner.py >/dev/null 2>&1 &
echo "603-3 Sabotage completed."
