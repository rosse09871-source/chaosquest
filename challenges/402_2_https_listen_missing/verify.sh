#!/bin/bash
set -e
RES=$(curl -k -s -o /dev/null -w "%{http_code}" https://127.0.0.1:443/ || true)
if [ "$RES" = "200" ]; then
    echo "✅ 성공: 443 SSL 포트가 정상 활성화되어 HTTPS 응답을 반환합니다!"
    exit 0
else
    echo "❌ 실패: HTTPS(443)에서 200 OK 응답이 오지 않습니다. (응답: $RES)"
    exit 1
fi
