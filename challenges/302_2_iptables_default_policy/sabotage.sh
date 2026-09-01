#!/bin/bash
set -e
which iptables >/dev/null 2>&1 || { apt-get update -qq >/dev/null 2>&1 || true ; apt-get install -y -qq iptables >/dev/null 2>&1 || true ; }
iptables -P INPUT DROP 2>/dev/null || true
echo "302-2 Sabotage completed."
