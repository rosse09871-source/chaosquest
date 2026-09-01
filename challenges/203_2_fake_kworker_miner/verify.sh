#!/bin/bash
set -e
if ps -eo pid,args | grep -v "$$" | grep "[k]worker_fake.py" >/dev/null 2>&1; then
    echo "❌ 실패: 위장된 악성 채굴 프로세스가 여전히 실행 중입니다."
    exit 1
fi
echo "✅ 성공: 커널 스레드로 위장한 악성 프로세스가 성공적으로 사살되었습니다!"
exit 0
