#!/bin/bash
set -e
if ps -eo pid,args | grep -v "$$" | grep "[z]ombie_db_holder.py" >/dev/null 2>&1; then
    echo "❌ 실패: DB 락을 쥐고 있는 zombie_db_holder.py 프로세스가 여전히 실행 중입니다."
    exit 1
fi
# Test writing to DB
WRITE_RES=$(python3 -c "
import sqlite3
try:
    conn = sqlite3.connect('/var/lib/data/app.db', timeout=1)
    cur = conn.cursor()
    cur.execute('INSERT INTO users VALUES (1, \"test\");')
    conn.commit()
    conn.close()
    print('SUCCESS')
except Exception as e:
    print('LOCKED')
")

if [ "$WRITE_RES" = "SUCCESS" ]; then
    echo "✅ 성공: DB 락이 해제되어 정상적인 트랜잭션 쓰기가 가능합니다!"
    exit 0
else
    echo "❌ 실패: 데이터베이스가 여전히 잠겨 있습니다."
    exit 1
fi
