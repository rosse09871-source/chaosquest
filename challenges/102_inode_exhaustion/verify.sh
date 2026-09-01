#!/bin/bash
set -e

DUMP_DIR="/var/cache/.session_dumps"
FILE_COUNT=0

if [ -d "$DUMP_DIR" ]; then
    FILE_COUNT=$(find "$DUMP_DIR" -type f 2>/dev/null | wc -l)
fi

if [ "$FILE_COUNT" -gt 100 ]; then
    echo "❌ 실패: $DUMP_DIR 디렉터리에 아직 $FILE_COUNT 개의 쓰레기 세션 파일이 남아있어 Inode가 낭비되고 있습니다."
    exit 1
fi

# Test creating a new file in /tmp
TEST_FILE="/tmp/chaos_inode_test_$(date +%s).txt"
if ! touch "$TEST_FILE" 2>/dev/null; then
    echo "❌ 실패: 파일시스템에 여전히 새 파일을 생성할 수 없습니다."
    exit 1
fi
rm -f "$TEST_FILE"

echo "✅ 성공: 불필요한 Inode 점유 파일들이 깨끗하게 정리되었고 신규 파일 생성이 정상 동작합니다!"
exit 0
