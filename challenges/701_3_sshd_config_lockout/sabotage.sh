#!/bin/bash
set -e
mkdir -p /etc/ssh
cat << 'SSHEOF' > /etc/ssh/sshd_config
PasswordAuthentication no
PubkeyAuthentication no
PermitRootLogin prohibit-password
SSHEOF
echo "701-3 Sabotage completed."
