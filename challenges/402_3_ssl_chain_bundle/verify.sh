#!/bin/bash
set -e
CERT_COUNT=$(grep -c "BEGIN CERTIFICATE" /etc/ssl/certs/fullchain.crt 2>/dev/null || echo "0")
if [ "$CERT_COUNT" -lt 2 ]; then
    echo "❌ 실패: /etc/ssl/certs/fullchain.crt 파일에 최소 2개 이상의 인증서(서버+중간CA)가 결합되어야 합니다."
    exit 1
fi
if ! grep -q "fullchain.crt" /etc/nginx/sites-available/default; then
    echo "❌ 실패: Nginx 설정이 fullchain.crt 를 바라보고 있지 않습니다."
    exit 1
fi
echo "✅ 성공: SSL Full Chain 인증서가 완벽하게 결합되었습니다!"
exit 0
