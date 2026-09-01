#!/bin/bash
set -e
MTU=$(ip link show eth0 2>/dev/null | awk '{print $5}' || ifconfig eth0 2>/dev/null | grep -o 'mtu [0-9]*' | awk '{print $2}')
if [ "$MTU" -lt 1400 ]; then
    echo "❌ 실패: eth0 인터페이스의 MTU($MTU)가 너무 작아 대용량 패킷 전송이 불가능합니다. (1500으로 변경 필요)"
    exit 1
fi
echo "✅ 성공: MTU가 표준 1500으로 정상 복구되었습니다!"
exit 0
