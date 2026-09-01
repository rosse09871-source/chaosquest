#!/bin/bash
set -e
if ! ip route show | grep -q "default via"; then
    echo "❌ 실패: 라우팅 테이블에 default gateway 경로가 여전히 없습니다."
    exit 1
fi
echo "✅ 성공: 기본 게이트웨이 라우팅 경로가 정상 복구되었습니다!"
exit 0
