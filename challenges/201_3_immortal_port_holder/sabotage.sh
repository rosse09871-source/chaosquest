#!/bin/bash
set -e
cat << 'PYEOF' > /usr/local/bin/immortal_master.py
import os, sys, time, subprocess
if os.fork() > 0: sys.exit(0)
os.setsid()
if os.fork() > 0: sys.exit(0)

# Master loop that respawns worker on port 8000
worker_script = """
import os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(503); self.end_headers()
HTTPServer(('0.0.0.0', 8000), H).serve_forever()
"""
with open("/tmp/immortal_worker.py", "w") as f: f.write(worker_script)

while True:
    p = subprocess.Popen(["python3", "/tmp/immortal_worker.py"])
    p.wait()
    time.sleep(0.5)
PYEOF
chmod +x /usr/local/bin/immortal_master.py
python3 /usr/local/bin/immortal_master.py
echo "201-3 Sabotage completed."
