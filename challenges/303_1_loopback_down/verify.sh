#!/bin/bash
set -e
if ip link show lo 2>/dev/null | grep -q "state DOWN"; then
    echo "❌ 실패: lo(Loopback) 인터페이스가 여전히 DOWN 상태입니다. (ip link set dev lo up 필요)"
    exit 1
fi
echo "✅ 성공: Loopback 인터페이스가 정상 활성화되었습니다!"
exit 0
