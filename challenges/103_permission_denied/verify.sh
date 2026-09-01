#!/bin/bash
set -e

# Test if an unprivileged user (www-data or nobody) can read the index.html
if ! su -s /bin/sh www-data -c "cat /var/www/html/index.html" >/dev/null 2>&1 && \
   ! su -s /bin/sh nobody -c "cat /var/www/html/index.html" >/dev/null 2>&1; then
    echo "❌ 실패: www-data 유저가 /var/www/html/index.html 파일에 접근(읽기)할 수 없습니다."
    echo "👉 팁: 디렉터리에는 실행(x) 권한(755), 파일에는 읽기(r) 권한(644)이 필요합니다."
    exit 1
fi

echo "✅ 성공: 웹 파일 권한이 정상화되어 웹 서비스 데몬이 파일을 성공적으로 읽을 수 있습니다!"
exit 0
