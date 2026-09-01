#!/bin/bash
set -e
if ! su -s /bin/sh www-data -c "touch /var/www/uploads/test_upload.tmp" >/dev/null 2>&1 && \
   ! su -s /bin/sh nobody -c "touch /var/www/uploads/test_upload.tmp" >/dev/null 2>&1; then
    echo "❌ 실패: www-data 유저가 /var/www/uploads 디렉터리에 파일을 생성(쓰기)할 수 없습니다."
    exit 1
fi
rm -f /var/www/uploads/test_upload.tmp
echo "✅ 성공: 업로드 디렉터리 권한이 정상화되었습니다!"
exit 0
