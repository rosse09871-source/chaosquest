#!/bin/bash
set -e

apt-get update -qq >/dev/null 2>&1 || true
apt-get install -y -qq nginx procps curl python3 net-tools >/dev/null 2>&1 || true

# 1. Start Python Backend on port 8080 with double fork
cat << 'PYEOF' > /usr/local/bin/backend_api.py
import os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler

if os.fork() > 0:
    sys.exit(0)
os.setsid()
if os.fork() > 0:
    sys.exit(0)

class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b"Hello from Backend API Service (200 OK)")

server = HTTPServer(('127.0.0.1', 8080), APIHandler)
server.serve_forever()
PYEOF

chmod +x /usr/local/bin/backend_api.py
python3 /usr/local/bin/backend_api.py

# 2. Configure Nginx with wrong upstream port (8000 instead of 8080)
cat << 'NGINXEOF' > /etc/nginx/sites-available/default
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
NGINXEOF

service nginx restart || nginx -g "daemon on;" || true

# Trigger a 502 request so error log is populated
curl -s http://127.0.0.1:80/ >/dev/null 2>&1 || true

echo "Stage 401 Sabotage completed. Nginx 502 Bad Gateway created."
