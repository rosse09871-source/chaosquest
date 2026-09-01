#!/bin/bash
set -e
MAX_RETRY=$(grep "^maxretry" /etc/fail2ban/jail.conf 2>/dev/null | awk '{print $3}')
if [ -z "$MAX_RETRY" ] || [ "$MAX_RETRY" -lt 5 ]; then
    echo "❌ 실패: Fail2ban maxretry($MAX_RETRY) 임계치가 너무 낮습니다. (최소 5 이상으로 증설 필요)"
    exit 1
fi
echo "✅ 성공: Fail2ban 임계치가 안전하게 완화 튜닝되었습니다!"
exit 0
