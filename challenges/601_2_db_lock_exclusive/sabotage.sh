#!/bin/bash
set -e
mkdir -p /var/lib/data
chmod 777 /var/lib/data
which sqlite3 >/dev/null 2>&1 || { apt-get update -qq >/dev/null 2>&1 || true ; apt-get install -y -qq sqlite3 python3 procps lsof psmisc >/dev/null 2>&1 || true ; }
sqlite3 /var/lib/data/app.db "CREATE TABLE IF NOT EXISTS users (id INT, name TEXT);"
chmod 666 /var/lib/data/app.db

cat << 'PYEOF' > /usr/local/bin/zombie_db_holder.py
import os, sys, time, sqlite3
if os.fork() > 0: sys.exit(0)
os.setsid()
if os.fork() > 0: sys.exit(0)
conn = sqlite3.connect("/var/lib/data/app.db")
cur = conn.cursor()
cur.execute("BEGIN EXCLUSIVE TRANSACTION;")
while True:
    time.sleep(1)
PYEOF
chmod +x /usr/local/bin/zombie_db_holder.py
python3 /usr/local/bin/zombie_db_holder.py
echo "601-2 Sabotage completed."
