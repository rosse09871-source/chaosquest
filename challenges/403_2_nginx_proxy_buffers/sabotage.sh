#!/bin/bash
set -e
cat << 'NGINXEOF' > /etc/nginx/sites-available/default
server {
    listen 80 default_server;
    proxy_buffer_size 1k; # Intentionally tiny buffer
    location / {
        return 200 "Buffer OK\n";
    }
}
NGINXEOF
service nginx restart || true
echo "403-2 Sabotage completed."
