#!/bin/bash
set -e
mkdir -p /var/lib/data
chmod 777 /var/lib/data
touch /var/lib/data/app.db-wal.corrupt_lock
echo "601-3 Sabotage completed."
