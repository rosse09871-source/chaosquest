#!/bin/bash
set -e
RES=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:80/ || true)
if [ "$RES" = "200" ] || [ "$RES" = "301" ] || [ "$RES" = "302" ]; then
    echo "✅ 성공: Nginx 서비스가 정상 기동되어 웹 요청에 응답하고 있습니다!"
    exit 0
else
    echo "❌ 실패: 80번 포트에서 Nginx 응답이 오지 않습니다. (응답: $RES)"
    exit 1
fi
