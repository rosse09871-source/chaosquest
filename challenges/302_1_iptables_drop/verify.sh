#!/bin/bash
set -e
if iptables -L INPUT -n 2>/dev/null | grep -q "dpt:8080.*DROP"; then
    echo "❌ 실패: iptables INPUT 체인에 8080 포트 DROP 차단 룰이 여전히 활성화되어 있습니다."
    exit 1
fi
RESPONSE=$(curl -s --connect-timeout 2 -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/ || true)
if [ "$RESPONSE" = "200" ]; then
    echo "✅ 성공: 방화벽 룰이 해제되어 8080 포트 통신이 정상 복구되었습니다!"
    exit 0
else
    echo "❌ 실패: 8080 포트에서 200 OK 응답을 받지 못했습니다."
    exit 1
fi
