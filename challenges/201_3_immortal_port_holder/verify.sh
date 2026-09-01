#!/bin/bash
set -e
if ps -eo pid,args | grep -v "$$" | grep -E "[i]mmortal_master|[i]mmortal_worker" >/dev/null 2>&1; then
    echo "❌ 실패: immortal_master 또는 worker 프로세스가 여전히 실행 중입니다."
    exit 1
fi
echo "✅ 성공: 마스터와 워커 프로세스가 모두 완벽하게 종료되었습니다!"
exit 0
