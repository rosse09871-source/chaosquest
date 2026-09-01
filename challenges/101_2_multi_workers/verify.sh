#!/bin/bash
set -e
if ps -eo pid,args | grep -v "$$" | grep "[d]ump_worker.py" >/dev/null 2>&1; then
    echo "❌ 실패: /tmp/.shared_dump.dat 파일을 물고 있는 dump_worker 프로세스가 여전히 실행 중입니다."
    exit 1
fi
if lsof +L1 2>/dev/null | grep "[s]hared_dump.dat" >/dev/null 2>&1; then
    echo "❌ 실패: /tmp/.shared_dump.dat 파일 디스크립터가 여전히 열려 있습니다."
    exit 1
fi
echo "✅ 성공: 모든 멀티 워커 프로세스가 완전히 종료되어 디스크가 정상 반환되었습니다!"
exit 0
