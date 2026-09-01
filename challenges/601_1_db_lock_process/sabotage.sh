#!/bin/bash
set -e
mkdir -p /var/lib/data
which sqlite3 >/dev/null 2>&1 || { apt-get update -qq >/dev/null 2>&1 || true ; apt-get install -y -qq sqlite3 python3 >/dev/null 2>&1 || true ; }
sqlite3 /var/lib/data/app.db "CREATE TABLE IF NOT EXISTS users (id INT, name TEXT);"
chmod 444 /var/lib/data/app.db
chmod 555 /var/lib/data
echo "601-1 Sabotage completed."
