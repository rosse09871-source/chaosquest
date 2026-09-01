#!/bin/bash
set -e
/usr/local/bin/entrypoint.sh || true
if ! grep -q "Container Entrypoint OK" /var/log/entrypoint.log 2>/dev/null; then
    echo "❌ 실패: APP_ENV 환경변수가 설정되지 않아 엔트리포인트 실행이 실패했습니다."
    exit 1
fi
echo "✅ 성공: APP_ENV 환경변수가 정상 등록되었습니다!"
exit 0
