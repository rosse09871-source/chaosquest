#!/bin/bash
set -e

# 1. Check if worker script has ENABLE_LEAK = False
if grep -q "ENABLE_LEAK = True" /usr/local/bin/queue_worker.py; then
  echo "queue_worker.py 코드에 여전히 메모리 누수(ENABLE_LEAK = True)가 켜져 있습니다."
  exit 1
fi

echo "메모리 누수 워커 버그가 성공적으로 패치되었습니다."
exit 0
