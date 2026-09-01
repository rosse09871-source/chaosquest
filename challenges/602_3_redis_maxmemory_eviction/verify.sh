#!/bin/bash
set -e
if ! grep -Eq "maxmemory-policy (allkeys-lru|volatile-lru|allkeys-lfu|volatile-lfu|allkeys-random)" /etc/redis/redis.conf 2>/dev/null; then
    echo "❌ 실패: maxmemory-policy 가 allkeys-lru 등 자동 축출 정책으로 변경되지 않았습니다."
    exit 1
fi
echo "✅ 성공: Redis 메모리 Eviction 정책이 안전하게 LRU로 튜닝되었습니다!"
exit 0
