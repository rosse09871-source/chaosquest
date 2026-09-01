#!/bin/bash
set -e
if ! su -s /bin/sh www-data -c "cat /var/www/html/index.html" >/dev/null 2>&1 && \
   ! su -s /bin/sh nobody -c "cat /var/www/html/index.html" >/dev/null 2>&1; then
    echo "❌ 실패: www-data 유저가 /var/www/html/index.html 파일에 접근할 수 없습니다."
    exit 1
fi
echo "✅ 성공: 웹 파일 권한이 정상화되었습니다!"
exit 0
