#!/bin/bash
set -e
if grep -q "127.0.0.99.*api.payment.internal" /etc/hosts 2>/dev/null; then
    echo "❌ 실패: /etc/hosts 에 127.0.0.99 가짜 IP 매핑이 여전히 남아있습니다."
    exit 1
fi
echo "✅ 성공: /etc/hosts 오염이 제거되어 정상 DNS 라우팅이 복구되었습니다!"
exit 0
