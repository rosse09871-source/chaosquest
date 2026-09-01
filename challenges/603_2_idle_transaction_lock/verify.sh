#!/bin/bash
set -e

if pgrep -f "zombie_tx.py" >/dev/null; then
  echo "장기 트랜잭션 락을 쥔 좀비 프로세스(zombie_tx.py)가 여전히 실행 중입니다."
  exit 1
fi

echo "좀비 트랜잭션 프로세스가 성공적으로 종료되고 락이 해제되었습니다."
exit 0
