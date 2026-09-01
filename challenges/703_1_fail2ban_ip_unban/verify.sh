#!/bin/bash
set -e
if grep -q "203.0.113.50" /var/log/fail2ban.blocked 2>/dev/null; then
    echo "❌ 실패: 사내 IP(203.0.113.50)가 여전히 차단 목록에 남아있습니다."
    exit 1
fi
echo "✅ 성공: 사내 개발팀 IP 차단이 안전하게 해제되었습니다!"
exit 0
