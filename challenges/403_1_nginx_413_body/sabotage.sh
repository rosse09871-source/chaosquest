#!/bin/bash
set -e
which nginx >/dev/null 2>&1 || { apt-get update -qq >/dev/null 2>&1 || true ; apt-get install -y -qq nginx curl >/dev/null 2>&1 || true ; }

cat << 'NGINXEOF' > /etc/nginx/sites-available/default
server {
    listen 80 default_server;
    server_name _;
    client_max_body_size 1k; # Intentionally tiny (1KB)
    location /upload {
        return 200 "Upload Success\n";
    }
}
NGINXEOF
service nginx restart || nginx -g "daemon on;" || true
echo "403-1 Sabotage completed."
