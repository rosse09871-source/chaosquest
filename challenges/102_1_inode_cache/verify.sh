#!/bin/bash
set -e
COUNT=$(find /tmp/junk_cache -type f 2>/dev/null | wc -l)
if [ "$COUNT" -gt 50 ]; then
    echo "❌ 실패: /tmp/junk_cache 디렉터리에 아직 $COUNT 개의 파일이 남아있습니다."
    exit 1
fi
echo "✅ 성공: Inode가 성공적으로 확보되었습니다!"
exit 0
