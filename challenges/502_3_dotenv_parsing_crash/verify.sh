#!/bin/bash
set -e
if ! /usr/local/bin/start_app_env.sh >/dev/null 2>&1; then
    echo "❌ 실패: /app/.env 파일의 따옴표 파싱 에러가 여전히 남아있습니다."
    exit 1
fi
echo "✅ 성공: .env 파일 문법이 정상 복구되었습니다!"
exit 0
