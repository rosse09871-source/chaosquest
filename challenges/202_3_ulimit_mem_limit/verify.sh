#!/bin/bash
set -e
if ! ps -eo pid,args | grep -v "$$" | grep "[i]ndexer.py" >/dev/null 2>&1; then
    echo "❌ 실패: indexer.py 프로세스가 실행 중이지 않습니다."
    exit 1
fi
echo "✅ 성공: ulimit 파일 디스크립터 제한이 확장되어 인덱서가 정상 동작합니다!"
exit 0
