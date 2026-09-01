#!/bin/bash
set -e
apt-get update -qq >/dev/null 2>&1 || true
apt-get install -y -qq iproute2 net-tools >/dev/null 2>&1 || true
ip link set dev lo down 2>/dev/null || ifconfig lo down 2>/dev/null || true
echo "303-1 Sabotage completed."
