#!/bin/bash
set -e

# Test if port 80 returns 200 OK and contains backend response
RESPONSE_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:80/ || true)
RESPONSE_BODY=$(curl -s http://127.0.0.1:80/ || true)

if [ "$RESPONSE_CODE" = "200" ] && echo "$RESPONSE_BODY" | grep -q "Backend API Service"; then
    echo "✅ 성공: Nginx 리버스 프록시와 백엔드 통신이 정상 복구되어 200 OK를 반환합니다!"
    exit 0
else
    echo "❌ 실패: Nginx(80 포트)에서 정상 응답(200 OK)이 오지 않습니다. (현재 응답 코드: $RESPONSE_CODE)"
    echo "👉 팁: /var/log/nginx/error.log 를 확인하고 /etc/nginx/sites-available/default 의 proxy_pass 포트를 수정한 뒤 nginx -s reload 하세요."
    exit 1
fi
