#!/bin/bash
set -e

# 1. Check if rogue_occupier is terminated
if ps -eo pid,args | grep -v "$$" | grep "[r]ogue_occupier.py" >/dev/null 2>&1; then
    echo "❌ 실패: 80번 포트를 점유하던 rogue_occupier 프로세스가 여전히 실행 중입니다."
    exit 1
fi

# 2. Check if port 80 returns 200 OK from production_app
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:80/ || true)

if [ "$RESPONSE" = "200" ]; then
    echo "✅ 성공: 웹서버가 80번 포트에서 정상적으로 200 OK 응답을 반환하고 있습니다!"
    exit 0
else
    echo "❌ 실패: 80번 포트에서 정상 웹 응답(200 OK)이 오지 않습니다. (현재 응답 코드: $RESPONSE)"
    echo "👉 팁: rogue_occupier를 종료한 후 /usr/local/bin/start_web.sh 를 실행하여 정상 서비스를 올리세요."
    exit 1
fi
