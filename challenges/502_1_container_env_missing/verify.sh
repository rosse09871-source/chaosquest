#!/bin/bash
set -e
/usr/local/bin/run_app.sh || true
if ! grep -q "successfully connected to DB" /var/log/app_status.log 2>/dev/null; then
    echo "❌ 실패: DB_HOST 환경변수가 등록되지 않아 애플리케이션 실행이 실패했습니다."
    exit 1
fi
echo "✅ 성공: 필수 환경변수가 정상 등록되어 컨테이너 앱이 성공적으로 동작합니다!"
exit 0
