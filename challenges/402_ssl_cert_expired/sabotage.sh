#!/bin/bash
set -e

apt-get update -qq >/dev/null 2>&1 || true
apt-get install -y -qq nginx openssl curl procps >/dev/null 2>&1 || true

# Generate valid self-signed SSL certs
mkdir -p /etc/ssl/certs /etc/ssl/private
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/valid_app.key \
  -out /etc/ssl/certs/valid_app.crt \
  -subj "/CN=chaosquest.local" >/dev/null 2>&1

mkdir -p /var/www/html
echo "<h1>ChaosQuest Secure HTTPS Service (200 OK)</h1>" > /var/www/html/index.html

# Corrupt Nginx config with non-existent cert path
cat << 'NGINXEOF' > /etc/nginx/sites-available/default
server {
    listen 443 ssl default_server;
    listen [::]:443 ssl default_server;

    ssl_certificate /etc/ssl/certs/wrong_nonexistent.crt;
    ssl_certificate_key /etc/ssl/private/wrong_nonexistent.key;

    root /var/www/html;
    index index.html;

    server_name _;

    location / {
        try_files $uri $uri/ =404;
    }
}
NGINXEOF

echo "Stage 402 Sabotage completed. Nginx SSL certificate path corrupted."
