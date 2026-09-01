#!/bin/bash
set -e

# Check if resolv.conf contains a known working nameserver
if ! grep -Eq "nameserver (8\.8\.8\.8|8\.8\.4\.4|1\.1\.1\.1|1\.0\.0\.1|9\.9\.9\.9|127\.0\.0\.53)" /etc/resolv.conf 2>/dev/null; then
    echo "❌ 실패: /etc/resolv.conf 에 유효한 공용 네임서버(8.8.8.8 또는 1.1.1.1 등)가 등록되어 있지 않습니다."
    exit 1
fi

echo "✅ 성공: DNS 네임서버가 올바르게 설정되었습니다!"
exit 0
