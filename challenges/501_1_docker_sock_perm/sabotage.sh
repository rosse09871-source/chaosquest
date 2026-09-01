#!/bin/bash
set -e
mkdir -p /var/run
touch /var/run/docker.sock
chmod 600 /var/run/docker.sock
chown root:root /var/run/docker.sock
echo "501-1 Sabotage completed."
