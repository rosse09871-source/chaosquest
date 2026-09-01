#!/bin/bash
set -e
COUNT=$(find /var/cache/.session_dumps -type f 2>/dev/null | wc -l)
if [ "$COUNT" -gt 50 ]; then
    echo "❌ 실패: /var/cache/.session_dumps 에 아직 $COUNT 개의 파일이 남아있습니다."
    exit 1
fi
echo "✅ 성공: 숨겨진 Inode 고갈 파일들이 깨끗하게 정리되었습니다!"
exit 0
