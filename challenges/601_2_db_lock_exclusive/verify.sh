#!/bin/bash
set -e
if ps -eo pid,args | grep -v "$$" | grep "[z]ombie_db_holder.py" >/dev/null 2>&1; then
    echo "❌ 실패: zombie_db_holder.py 프로세스가 여전히 실행 중입니다."
    exit 1
fi
echo "✅ 성공: 독점 락 프로세스가 종료되어 DB가 정상화되었습니다!"
exit 0
