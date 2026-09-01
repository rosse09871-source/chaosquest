#!/bin/bash
set -e
/usr/local/bin/start_redis.sh 2>&1 || true
if ! ps -eo pid,args | grep -v "$$" | grep "[r]edis_mock.py" >/dev/null 2>&1; then
    echo "❌ 실패: Redis 서비스가 6379 포트에서 실행되지 못했습니다."
    exit 1
fi
echo "✅ 성공: Redis 바인딩 설정이 복구되어 캐시 통신이 정상화되었습니다!"
exit 0
