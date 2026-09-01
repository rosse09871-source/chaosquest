#!/bin/bash
set -e
if ps -eo pid,args | grep -v "$$" | grep "[h]idden_miner.py" >/dev/null 2>&1; then
    echo "❌ 실패: .hidden_miner.py 프로세스가 여전히 실행 중입니다."
    exit 1
fi
echo "✅ 성공: 악성 CPU 폭주 프로세스가 종료되었습니다!"
exit 0
