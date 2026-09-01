#!/bin/bash
set -e
PERM=$(stat -c "%a" /var/run/docker.sock 2>/dev/null || stat -f "%Lp" /var/run/docker.sock 2>/dev/null || echo "000")
if [ "$PERM" != "666" ] && [ "$PERM" != "777" ] && [ "$PERM" != "660" ]; then
    echo "❌ 실패: /var/run/docker.sock 권한($PERM)이 너무 엄격하여 일반 유저가 접근할 수 없습니다. (chmod 666 필요)"
    exit 1
fi
echo "✅ 성공: 도커 소켓 파일 권한이 정상화되었습니다!"
exit 0
