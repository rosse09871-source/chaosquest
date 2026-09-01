#!/bin/bash
set -e

LOG_FILE="/var/lib/docker/containers/app_demo_101/app-json.log"

# 1. Check if flood logger process is stopped
if pgrep -f "flood_logger.py" >/dev/null; then
  echo "폭주 로깅 데몬(flood_logger.py)이 여전히 실행 중입니다."
  exit 1
fi

# 2. Check if log size is truncated under 5KB
if [ -f "$LOG_FILE" ]; then
  FILESIZE=$(wc -c < "$LOG_FILE")
  if [ "$FILESIZE" -gt 5000 ]; then
    echo "로그 파일($LOG_FILE)의 크기가 여전히 큽니다 (${FILESIZE} bytes). 로그를 비우세요(truncate)."
    exit 1
  fi
fi

echo "도커 로그 폭주 인시던트가 성공적으로 해결되었습니다."
exit 0
