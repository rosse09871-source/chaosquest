#!/bin/bash
set -e

apt-get update -qq >/dev/null 2>&1 || true
apt-get install -y -qq procps dnsutils >/dev/null 2>&1 || true

# Break /etc/resolv.conf with dummy unreachable IP
echo "nameserver 192.0.2.1" > /etc/resolv.conf

echo "Stage 301 Sabotage completed. DNS is pointing to unreachable IP."
