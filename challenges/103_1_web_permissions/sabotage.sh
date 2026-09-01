#!/bin/bash
set -e
mkdir -p /var/www/html
echo "<h1>ChaosQuest Web App 200 OK</h1>" > /var/www/html/index.html
chmod 700 /var/www/html
chmod 600 /var/www/html/index.html
chown -R root:root /var/www
echo "103-1 Sabotage completed."
