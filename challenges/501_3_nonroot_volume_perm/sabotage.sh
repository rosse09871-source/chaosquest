#!/bin/bash
set -e
mkdir -p /data/app_storage
chown 0:0 /data/app_storage
chmod 700 /data/app_storage
useradd -u 1000 nodeuser 2>/dev/null || true
echo "501-3 Sabotage completed."
