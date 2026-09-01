#!/bin/bash
set -e
if ! grep -Eq "proxy_read_timeout (60s|120s|300s|600s|120|300|600)" /etc/nginx/sites-available/default /etc/nginx/nginx.conf 2>/dev/null; then
    echo "❌ 실패: proxy_read_timeout 설정이 60초 이상으로 증설되지 않았습니다."
    exit 1
fi
echo "✅ 성공: Nginx 프록시 타임아웃이 정상 튜닝되었습니다!"
exit 0
