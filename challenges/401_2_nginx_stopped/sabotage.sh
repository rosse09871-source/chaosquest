#!/bin/bash
set -e
which nginx >/dev/null 2>&1 || { apt-get update -qq >/dev/null 2>&1 || true ; apt-get install -y -qq nginx curl >/dev/null 2>&1 || true ; }
service nginx stop 2>/dev/null || true
echo "401-2 Sabotage completed."
