#!/bin/bash
set -e

# 1. Check if hidden_miner is running
if ps -eo pid,args | grep -v "$$" | grep "[h]idden_miner.py" >/dev/null 2>&1; then
    echo "❌ 실패: CPU를 갉아먹는 .hidden_miner.py 프로세스가 여전히 실행 중입니다."
    exit 1
fi

echo "✅ 성공: 악성 CPU 폭주 프로세스가 성공적으로 종료되어 시스템 자원이 안정화되었습니다!"
exit 0
