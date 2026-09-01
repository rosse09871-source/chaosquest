#!/bin/bash
set -e
RES=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:80/ || true)
if [ "$RES" = "200" ]; then
    echo "✅ 성공: Unix Domain Socket 통신이 정상 복구되어 200 OK를 반환합니다!"
    exit 0
else
    echo "❌ 실패: 80번 포트에서 200 OK 응답이 오지 않습니다. (응답: $RES)"
    exit 1
fi
