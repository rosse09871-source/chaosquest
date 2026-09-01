#!/bin/bash
set -e
apt-get update -qq >/dev/null 2>&1 || true
apt-get install -y -qq nginx openssl curl >/dev/null 2>&1 || true

mkdir -p /etc/ssl/certs /etc/ssl/private
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/app.key \
  -out /etc/ssl/certs/app.crt \
  -subj "/CN=chaos.local" >/dev/null 2>&1

cat << 'NGINXEOF' > /etc/nginx/sites-available/default
server {
    listen 8080 default_server; # Missing 443 ssl!
    ssl_certificate /etc/ssl/certs/app.crt;
    ssl_certificate_key /etc/ssl/private/app.key;
    location / { return 200 "HTTPS OK\n"; }
}
NGINXEOF
service nginx restart || true
echo "402-2 Sabotage completed."
