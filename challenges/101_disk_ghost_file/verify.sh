#!/bin/bash
set -e

# 1. Check if the legacy_logger process is still running (excluding the verify command itself)
if ps -eo pid,args | grep -v "$$" | grep "[l]egacy_logger.py" >/dev/null 2>&1; then
    echo "❌ 실패: 삭제된 로그 파일을 물고 있는 legacy_logger 프로세스가 여전히 실행 중입니다."
    exit 1
fi

# 2. Check if any deleted files are still held open in /var/log
if lsof +L1 2>/dev/null | grep "[a]pp_ghost.log" >/dev/null 2>&1; then
    echo "❌ 실패: /var/log/app_ghost.log 파일의 파일 디스크립터가 여전히 열려 있습니다."
    exit 1
fi

echo "✅ 성공: 유령 프로세스가 성공적으로 종료되었고 파일 디스크립터가 정리되었습니다!"
exit 0
