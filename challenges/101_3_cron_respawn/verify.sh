#!/bin/bash
set -e
if [ -f /etc/cron.d/ghost_watcher ]; then
    echo "❌ 실패: /etc/cron.d/ghost_watcher 크론 설정 파일이 여전히 존재하여 프로세스가 다시 부활합니다."
    exit 1
fi
if ps -eo pid,args | grep -v "$$" | grep "[g]host_spawner.py" >/dev/null 2>&1; then
    echo "❌ 실패: ghost_spawner.py 프로세스가 여전히 실행 중입니다."
    exit 1
fi
if ps -eo pid,args | grep -v "$$" | grep "[g]host_watcher.sh" >/dev/null 2>&1; then
    echo "❌ 실패: ghost_watcher.sh 감시 스크립트가 여전히 실행 중입니다."
    exit 1
fi
echo "✅ 성공: 부활 크론잡과 유령 데몬이 완전히 제거되었습니다!"
exit 0
