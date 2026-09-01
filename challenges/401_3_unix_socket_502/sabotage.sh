#!/bin/bash
set -e
apt-get update -qq >/dev/null 2>&1 || true
apt-get install -y -qq nginx procps curl python3 >/dev/null 2>&1 || true

cat << 'PYEOF' > /usr/local/bin/uds_app.py
import socket, os, sys
SOCK = "/tmp/app.sock"
if os.path.exists(SOCK): os.unlink(SOCK)
if os.fork() > 0: sys.exit(0)
os.setsid()
if os.fork() > 0: sys.exit(0)
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.bind(SOCK)
s.listen(5)
os.chmod(SOCK, 0o600) # Restricted to root only!
while True:
    conn, _ = s.accept()
    data = conn.recv(1024)
    conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 14\r\n\r\nUDS Backend OK")
    conn.close()
PYEOF
python3 /usr/local/bin/uds_app.py

cat << 'NGINXEOF' > /etc/nginx/sites-available/default
server {
    listen 80 default_server;
    server_name _;
    location / {
        proxy_pass http://unix:/tmp/app.sock;
    }
}
NGINXEOF
service nginx restart || nginx -g "daemon on;" || true
curl -s http://127.0.0.1:80/ >/dev/null 2>&1 || true
echo "401-3 Sabotage completed."
