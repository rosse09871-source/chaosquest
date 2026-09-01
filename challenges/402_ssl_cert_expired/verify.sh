#!/bin/bash
set -e

# 1. Test nginx config
if ! nginx -t >/dev/null 2>&1; then
    echo "❌ 실패: nginx -t 설정 문법 및 인증서 파일 경로 검사가 실패했습니다."
    exit 1
fi

# 2. Test HTTPS 443 response
RESPONSE_CODE=$(curl -k -s -o /dev/null -w "%{http_code}" https://127.0.0.1:443/ || true)
if [ "$RESPONSE_CODE" = "200" ]; then
    echo "✅ 성공: SSL 인증서 경로가 올바르게 복구되어 HTTPS(443) 통신이 정상 동작합니다!"
    exit 0
else
    echo "❌ 실패: HTTPS(443 포트)에서 정상 응답(200 OK)을 받지 못했습니다. (현재 응답 코드: $RESPONSE_CODE)"
    echo "👉 팁: /etc/nginx/sites-available/default 의 인증서 경로를 /etc/ssl/certs/valid_app.crt 와 /etc/ssl/private/valid_app.key 로 수정하고 service nginx restart 하세요."
    exit 1
fi
