#!/bin/bash
set -e
which ip >/dev/null 2>&1 || { apt-get update -qq >/dev/null 2>&1 || true ; apt-get install -y -qq iputils-ping >/dev/null 2>&1 || true ; }
# Remove any existing entry from /etc/hosts
sed -i '/backend.internal.service/d' /etc/hosts || true
echo "503-3 Sabotage completed."
