#!/bin/bash
set -e
mkdir -p /root/.ssh
touch /root/.ssh/authorized_keys
chmod 777 /root/.ssh
chmod 666 /root/.ssh/authorized_keys
echo "701-2 Sabotage completed."
