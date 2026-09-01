#!/bin/bash
set -e
if ! grep -Eq "proxy_buffer_size (64k|128k|256k|512k)" /etc/nginx/sites-available/default /etc/nginx/nginx.conf 2>/dev/null; then
    echo "❌ 실패: proxy_buffer_size 설정이 64k 이상으로 증설되지 않았습니다."
    exit 1
fi
echo "✅ 성공: Nginx 프록시 버퍼 용량이 안전하게 확장되었습니다!"
exit 0
