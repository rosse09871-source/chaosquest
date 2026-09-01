#!/bin/bash
set -e
which iproute2 >/dev/null 2>&1 || { apt-get update -qq >/dev/null 2>&1 || true ; apt-get install -y -qq iproute2 net-tools procps >/dev/null 2>&1 || true ; }

# Shrink eth0 MTU
ip link set dev eth0 mtu 576 2>/dev/null || ifconfig eth0 mtu 576 2>/dev/null || true
echo "303-1 Sabotage completed."
