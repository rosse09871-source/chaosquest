#!/bin/bash
set -e
if ! grep -q "^search.*internal\.net" /etc/resolv.conf 2>/dev/null; then
    echo "❌ 실패: /etc/resolv.conf 에 'search internal.net' 설정이 등록되어 있지 않습니다."
    exit 1
fi
echo "✅ 성공: 검색 도메인이 등록되어 단축 호스트명 조회가 가능합니다!"
exit 0
