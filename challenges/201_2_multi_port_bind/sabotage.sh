#!/bin/bash
set -e
which procps >/dev/null 2>&1 || { apt-get update -qq >/dev/null 2>&1 || true ; apt-get install -y -qq procps net-tools python3 curl >/dev/null 2>&1 || true ; }

cat << 'PYEOF' > /usr/local/bin/rogue_api.py
import os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
if os.fork() > 0: sys.exit(0)
os.setsid()
if os.fork() > 0: sys.exit(0)
class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(503); self.end_headers()
HTTPServer(('0.0.0.0', 8080), H).serve_forever()
PYEOF

cat << 'PYEOF' > /usr/local/bin/rogue_metric.py
import os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
if os.fork() > 0: sys.exit(0)
os.setsid()
if os.fork() > 0: sys.exit(0)
class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(503); self.end_headers()
HTTPServer(('0.0.0.0', 9000), H).serve_forever()
PYEOF

python3 /usr/local/bin/rogue_api.py
python3 /usr/local/bin/rogue_metric.py

cat << 'SHEOF' > /usr/local/bin/start_services.sh
#!/bin/bash
cat << 'PYEOF' > /usr/local/bin/real_api.py
import os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
if os.fork() > 0: sys.exit(0)
os.setsid()
if os.fork() > 0: sys.exit(0)
class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
HTTPServer(('0.0.0.0', 8080), H).serve_forever()
PYEOF

cat << 'PYEOF' > /usr/local/bin/real_metric.py
import os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
if os.fork() > 0: sys.exit(0)
os.setsid()
if os.fork() > 0: sys.exit(0)
class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"METRICS OK")
HTTPServer(('0.0.0.0', 9000), H).serve_forever()
PYEOF

python3 /usr/local/bin/real_api.py
python3 /usr/local/bin/real_metric.py
echo "All Services Started!"
SHEOF
chmod +x /usr/local/bin/start_services.sh
echo "201-2 Sabotage completed."
