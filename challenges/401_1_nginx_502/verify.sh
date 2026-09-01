#!/bin/bash
set -e
RESPONSE_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:80/ || true)
RESPONSE_BODY=$(curl -s http://127.0.0.1:80/ || true)
if [ "$RESPONSE_CODE" = "200" ] && echo "$RESPONSE_BODY" | grep -q "Backend API Service"; then
    echo "✅ 성공: Nginx 리버스 프록시와 백엔드 통신이 정상 복구되었습니다!"
    exit 0
else
    echo "❌ 실패: Nginx(80 포트)에서 정상 응답(200 OK)이 오지 않습니다. (응답 코드: $RESPONSE_CODE)"
    exit 1
fi
