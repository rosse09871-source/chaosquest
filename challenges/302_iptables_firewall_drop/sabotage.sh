#!/bin/bash
set -e

apt-get update -qq >/dev/null 2>&1 || true
apt-get install -y -qq procps iptables curl python3 >/dev/null 2>&1 || true

# 1. Run web server on 8080 with double fork
cat << 'PYEOF' > /usr/local/bin/api_server.py
import os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler

if os.fork() > 0:
    sys.exit(0)
os.setsid()
if os.fork() > 0:
    sys.exit(0)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"API OK")

server = HTTPServer(('0.0.0.0', 8080), Handler)
server.serve_forever()
PYEOF

python3 /usr/local/bin/api_server.py

# 2. Add iptables drop rule if iptables is allowed, or simulate blocking with ufw/hosts.deny
iptables -A INPUT -p tcp --dport 8080 -j DROP 2>/dev/null || true

echo "Stage 302 Sabotage completed. Port 8080 is blocked by iptables."
