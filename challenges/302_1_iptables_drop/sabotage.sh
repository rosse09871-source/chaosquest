#!/bin/bash
set -e
which procps >/dev/null 2>&1 || { apt-get update -qq >/dev/null 2>&1 || true ; apt-get install -y -qq procps iptables curl python3 >/dev/null 2>&1 || true ; }

cat << 'PYEOF' > /usr/local/bin/api_server.py
import os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
if os.fork() > 0: sys.exit(0)
os.setsid()
if os.fork() > 0: sys.exit(0)
class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"API OK")
HTTPServer(('0.0.0.0', 8080), H).serve_forever()
PYEOF
python3 /usr/local/bin/api_server.py
iptables -A INPUT -p tcp --dport 8080 -j DROP 2>/dev/null || true
echo "302-1 Sabotage completed."
