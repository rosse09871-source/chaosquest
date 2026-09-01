#!/bin/bash
set -e
mkdir -p /etc/redis
echo "bind 192.168.254.254" > /etc/redis/redis.conf

cat << 'SHEOF' > /usr/local/bin/start_redis.sh
#!/bin/bash
BIND_ADDR=$(grep "^bind" /etc/redis/redis.conf | awk '{print $2}')
if [ "$BIND_ADDR" != "0.0.0.0" ] && [ "$BIND_ADDR" != "127.0.0.1" ]; then
    echo "FATAL: Cannot bind Redis to invalid address: $BIND_ADDR"
    exit 1
fi
cat << 'PYEOF' > /usr/local/bin/redis_mock.py
import os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
if os.fork() > 0: sys.exit(0)
os.setsid()
if os.fork() > 0: sys.exit(0)
class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"+PONG\r\n")
HTTPServer(('0.0.0.0', 6379), H).serve_forever()
PYEOF
python3 /usr/local/bin/redis_mock.py
echo "Redis started on port 6379!"
SHEOF
chmod +x /usr/local/bin/start_redis.sh
echo "602-1 Sabotage completed."
