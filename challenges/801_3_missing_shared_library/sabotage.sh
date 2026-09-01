#!/bin/bash
set -e
mkdir -p /opt/lib /opt/bin /etc/ld.so.conf.d
touch /opt/lib/libcustom.so
rm -f /etc/ld.so.conf.d/app.conf || true
ldconfig 2>/dev/null || true
echo "801-3 Sabotage completed."
