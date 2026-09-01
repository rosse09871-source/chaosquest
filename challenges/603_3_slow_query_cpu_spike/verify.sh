#!/bin/bash
set -e

if pgrep -f "rogue_query_runner.py" >/dev/null; then
  echo "악성 슬로우 쿼리 데몬(rogue_query_runner.py)이 여전히 CPU를 소모하며 실행 중입니다."
  exit 1
fi

echo "악성 슬로우 쿼리 프로세스가 성공적으로 진압되었습니다."
exit 0
