#!/bin/bash
set -e
if ! /usr/local/bin/check_dockerd.sh >/dev/null 2>&1; then
    echo "❌ 실패: /etc/docker/daemon.json JSON 설정 파일이 여전히 올바르지 않습니다."
    exit 1
fi
echo "✅ 성공: 도커 데몬 설정 파일이 정상 복구되었습니다!"
exit 0
