#!/bin/bash
set -e
cat << 'NGINXEOF' > /etc/nginx/sites-available/default
server {
    listen 80 default_server;
    proxy_read_timeout 2s; # Intentionally tiny timeout
    location / {
        return 200 "Timeout OK\n";
    }
}
NGINXEOF
service nginx restart || true
echo "403-3 Sabotage completed."
