#!/bin/bash
set -e
# Intentionally delete default route if possible
ip route del default 2>/dev/null || true
echo "303-2 Sabotage completed."
