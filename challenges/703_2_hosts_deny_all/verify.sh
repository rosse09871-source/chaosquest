#!/bin/bash
set -e
if grep -q "^ALL: ALL" /etc/hosts.deny 2>/dev/null; then
    echo "❌ 실패: /etc/hosts.deny 에 ALL: ALL 전면 차단 규칙이 여전히 남아있습니다."
    exit 1
fi
echo "✅ 성공: TCP Wrapper 차단 룰이 안전하게 해제되었습니다!"
exit 0
