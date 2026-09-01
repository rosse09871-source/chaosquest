#!/bin/bash
set -e
mkdir -p /etc/ssl/certs /etc/ssl/private
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/server.key -out /etc/ssl/certs/server.crt -subj "/CN=server" >/dev/null 2>&1
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/intermediate.key -out /etc/ssl/certs/intermediate.crt -subj "/CN=intermediate" >/dev/null 2>&1

cat << 'NGINXEOF' > /etc/nginx/sites-available/default
server {
    listen 443 ssl default_server;
    ssl_certificate /etc/ssl/certs/server.crt; # Only single cert, missing chain!
    ssl_certificate_key /etc/ssl/private/server.key;
    location / { return 200 "Full Chain OK\n"; }
}
NGINXEOF
service nginx restart || true
echo "402-3 Sabotage completed."
