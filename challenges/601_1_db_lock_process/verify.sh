#!/bin/bash
set -e
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
    print('FAIL:', e)
")

if echo "$WRITE_RES" | grep -q "SUCCESS"; then
    echo "✅ 성공: DB 파일 및 디렉터리 쓰기 권한이 정상 복구되었습니다!"
    exit 0
else
    echo "❌ 실패: $WRITE_RES"
    exit 1
fi
