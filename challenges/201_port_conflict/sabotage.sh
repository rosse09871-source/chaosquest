#!/bin/bash
set -e

apt-get update -qq >/dev/null 2>&1 || true
apt-get install -y -qq procps net-tools python3 curl iproute2 >/dev/null 2>&1 || true

# 1. Create a rogue daemon occupying port 80 with Unix double-fork
cat << 'PYEOF' > /usr/local/bin/rogue_occupier.py
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

# Double fork
if os.fork() > 0:
    sys.exit(0)
os.setsid()
if os.fork() > 0:
    sys.exit(0)

class RogueHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(503)
        self.end_headers()
        self.wfile.write(b"ROGUE OCCUPIER ON PORT 80 - SERVICE UNAVAILABLE")

server = HTTPServer(('0.0.0.0', 80), RogueHandler)
server.serve_forever()
PYEOF

chmod +x /usr/local/bin/rogue_occupier.py
python3 /usr/local/bin/rogue_occupier.py

# 2. Create the legitimate start script that the user should run
cat << 'SHEOF' > /usr/local/bin/start_web.sh
#!/bin/bash
cat << 'PYEOF' > /usr/local/bin/production_app.py
import os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler

if os.fork() > 0:
    sys.exit(0)
os.setsid()
if os.fork() > 0:
    sys.exit(0)

class ProdHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(b"<h1>ChaosQuest Production Web Service Online (200 OK)</h1>")

server = HTTPServer(('0.0.0.0', 80), ProdHandler)
server.serve_forever()
PYEOF

python3 /usr/local/bin/production_app.py
echo "Production Web Service Started!"
SHEOF

chmod +x /usr/local/bin/start_web.sh

echo "Stage 201 Sabotage completed. Port 80 is occupied by rogue_occupier."
