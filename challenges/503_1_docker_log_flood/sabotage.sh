#!/bin/bash
set -e
which python3 >/dev/null 2>&1 || { apt-get update -qq >/dev/null 2>&1 || true ; apt-get install -y -qq python3 procps >/dev/null 2>&1 || true ; }

mkdir -p /var/lib/docker/containers/app_demo_101
LOG_FILE="/var/lib/docker/containers/app_demo_101/app-json.log"

# Fill log file with dummy logs
for i in $(seq 1 1000); do
  echo "{\"log\":\"[2026-09-01 12:00:00] DEBUG payload flood message #$i\\n\",\"stream\":\"stdout\",\"time\":\"2026-09-01T12:00:00.000000000Z\"}" >> "$LOG_FILE"
done

cat << 'PYEOF' > /usr/local/bin/flood_logger.py
import time, os
log_file = "/var/lib/docker/containers/app_demo_101/app-json.log"
while True:
    with open(log_file, "a") as f:
        f.write(f'{{"log":"[DEBUG] runtime tick {time.time()}\\n","stream":"stdout"}}\n')
    time.sleep(0.5)
PYEOF

chmod +x /usr/local/bin/flood_logger.py
nohup python3 /usr/local/bin/flood_logger.py >/dev/null 2>&1 &
echo "503-1 Sabotage completed."
