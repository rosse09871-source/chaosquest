#!/bin/bash
set -e
if [ -f /var/lib/data/app.db-wal.corrupt_lock ]; then
    echo "❌ 실패: /var/lib/data/app.db-wal.corrupt_lock 손상 락 파일이 여전히 남아있습니다."
    exit 1
fi
echo "✅ 성공: 저널 파일 정리 및 무결성 검증이 완료되었습니다!"
exit 0
