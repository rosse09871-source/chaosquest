#!/bin/bash
set -e

apt-get update -qq >/dev/null 2>&1 || true
apt-get install -y -qq procps python3 curl >/dev/null 2>&1 || true

mkdir -p /var/www/html
cat << 'HTMLEOF' > /var/www/html/index.html
<h1>ChaosQuest Web App - Status 200 OK</h1>
HTMLEOF

# Intentionally ruin permissions: lock directory (no traverse) and file (no read for others)
chmod 700 /var/www/html
chmod 600 /var/www/html/index.html
chown -R root:root /var/www

echo "Stage 103 Sabotage completed. /var/www/html permissions corrupted."
