#!/bin/bash
set -e
if ps -eo pid,args | grep -v "$$" | grep -E "[r]ogue_api.py|[r]ogue_metric.py" >/dev/null 2>&1; then
    echo "❌ 실패: 점유 프로세스가 아직 종료되지 않았습니다."
    exit 1
fi
R1=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/ || true)
R2=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:9000/ || true)
if [ "$R1" = "200" ] && [ "$R2" = "200" ]; then
    echo "✅ 성공: 8080 및 9000번 포트 서비스가 모두 정상 복구되었습니다!"
    exit 0
else
    echo "❌ 실패: 포트 8080($R1) 또는 9000($R2) 서비스가 200 OK 응답을 주지 않습니다."
    exit 1
fi
