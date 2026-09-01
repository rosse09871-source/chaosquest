#!/bin/bash
set -e
/usr/local/bin/start_redis_sec.sh || true
if ! grep -q "Redis started securely" /var/log/redis.log 2>/dev/null; then
    echo "❌ 실패: Redis protected-mode 설정이 여전히 활성화되어 있습니다."
    exit 1
fi
echo "✅ 성공: Redis 보호 모드가 올바르게 설정되었습니다!"
exit 0
