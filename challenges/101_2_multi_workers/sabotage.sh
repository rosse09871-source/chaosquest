#!/bin/bash
set -e
which lsof >/dev/null 2>&1 || { apt-get update -qq >/dev/null 2>&1 || true ; apt-get install -y -qq lsof procps python3 >/dev/null 2>&1 || true ; }

cat << 'PYEOF' > /usr/local/bin/dump_worker.py
import os, sys, time
if os.fork() > 0: sys.exit(0)
os.setsid()
if os.fork() > 0: sys.exit(0)

filepath = "/tmp/.shared_dump.dat"
f = open(filepath, "w")
for i in range(1000): f.write(f"Chunk {i}\n")
f.flush()
if os.path.exists(filepath): os.unlink(filepath)

# Spawn 3 child workers sharing the open FD
for _ in range(3):
    if os.fork() == 0:
        while True:
            f.write("worker tick\n")
            f.flush()
            time.sleep(1)

while True:
    f.write("parent tick\n")
    f.flush()
    time.sleep(1)
PYEOF

chmod +x /usr/local/bin/dump_worker.py
python3 /usr/local/bin/dump_worker.py
echo "101-2 Sabotage completed."
