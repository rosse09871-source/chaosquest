#!/bin/bash
set -e
if ps -eo pid,args | grep -v "$$" | grep "[c]pu_burner_worker" >/dev/null 2>&1; then
    echo "❌ 실패: CPU 폭주 워커 프로세스가 아직 남아있습니다."
    exit 1
fi
echo "✅ 성공: 모든 CPU 폭주 프로세스가 일괄 정리되었습니다!"
exit 0
