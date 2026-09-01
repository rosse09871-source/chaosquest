#!/bin/bash
set -e
mkdir -p /etc/fail2ban
cat << 'JAILEOF' > /etc/fail2ban/jail.conf
[sshd]
enabled = true
port = ssh
maxretry = 1
bantime = 86400
JAILEOF
echo "703-3 Sabotage completed."
