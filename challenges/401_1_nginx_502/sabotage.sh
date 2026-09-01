#!/bin/bash
set -e
which nginx >/dev/null 2>&1 || { apt-get update -qq >/dev/null 2>&1 || true ; apt-get install -y -qq nginx procps curl python3 net-tools >/dev/null 2>&1 || true ; }

cat << 'PYEOF' > /usr/local/bin/backend_api.py
import os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
if os.fork() > 0: sys.exit(0)
os.setsid()
if os.fork() > 0: sys.exit(0)
class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b"Hello from Backend API Service (200 OK)")
server = HTTPServer(('127.0.0.1', 8080), APIHandler)
server.serve_forever()
PYEOF
python3 /usr/local/bin/backend_api.py

cat << 'NGINXEOF' > /etc/nginx/sites-available/default
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}
NGINXEOF
service nginx restart || nginx -g "daemon on;" || true
curl -s http://127.0.0.1:80/ >/dev/null 2>&1 || true
echo "401-1 Sabotage completed."
