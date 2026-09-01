#!/bin/bash
set -e
POLICY=$(iptables -L INPUT -n 2>/dev/null | head -n 1 | awk '{print $4}' | tr -d ')' || echo "DROP")
if [ "$POLICY" = "DROP" ]; then
    echo "❌ 실패: iptables INPUT 체인의 기본 정책이 여전히 DROP 입니다. (iptables -P INPUT ACCEPT 필요)"
    exit 1
fi
echo "✅ 성공: iptables 기본 정책이 ACCEPT로 복구되었습니다!"
exit 0
