#!/bin/bash
set -e
apt-get update -qq >/dev/null 2>&1 || true
apt-get install -y -qq lsof procps python3 cron >/dev/null 2>&1 || true

cat << 'PYEOF' > /usr/local/bin/ghost_spawner.py
import os, sys, time
if os.fork() > 0: sys.exit(0)
os.setsid()
if os.fork() > 0: sys.exit(0)

filepath = "/var/log/eternal_ghost.log"
f = open(filepath, "w")
f.write("eternal trace\n")
f.flush()
if os.path.exists(filepath): os.unlink(filepath)
while True:
    f.write("tick\n")
    f.flush()
    time.sleep(1)
PYEOF
chmod +x /usr/local/bin/ghost_spawner.py

# Create a background loop script simulating aggressive cron watcher
cat << 'SHEOF' > /usr/local/bin/ghost_watcher.sh
#!/bin/bash
while [ -f /etc/cron.d/ghost_watcher ]; do
    if ! ps -ef | grep "[g]host_spawner.py" >/dev/null; then
        python3 /usr/local/bin/ghost_spawner.py
    fi
    sleep 2
done
SHEOF
chmod +x /usr/local/bin/ghost_watcher.sh

# Register in cron.d
mkdir -p /etc/cron.d
echo "* * * * * root /usr/local/bin/ghost_watcher.sh" > /etc/cron.d/ghost_watcher

# Start watcher in background
nohup /usr/local/bin/ghost_watcher.sh >/dev/null 2>&1 &

echo "101-3 Sabotage completed."
