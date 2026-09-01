#!/bin/bash
set -e
if ! ps -eo pid,args | grep -v "$$" | grep "[a]uth_service.py" >/dev/null 2>&1; then
    echo "❌ 실패: auth_service.py 프로세스가 실행 중이지 않습니다."
    exit 1
fi
echo "✅ 성공: JSON 설정 파일이 복구되어 인증 서비스가 정상 기동 중입니다!"
exit 0
