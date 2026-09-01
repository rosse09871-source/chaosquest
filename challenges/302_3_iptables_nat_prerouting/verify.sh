#!/bin/bash
set -e
if iptables -t nat -L PREROUTING -n 2>/dev/null | grep -q "9999"; then
    echo "❌ 실패: NAT PREROUTING 체인에 9999 포트 REDIRECT 룰이 여전히 남아있습니다."
    exit 1
fi
echo "✅ 성공: NAT 테이블 포트 포워딩 룰이 정상 정리되었습니다!"
exit 0
