#!/bin/bash
set -e
if ! nginx -t >/dev/null 2>&1; then
    echo "❌ 실패: nginx -t 설정 문법 및 인증서 파일 경로 검사가 실패했습니다."
    exit 1
fi
RESPONSE_CODE=$(curl -k -s -o /dev/null -w "%{http_code}" https://127.0.0.1:443/ || true)
if [ "$RESPONSE_CODE" = "200" ]; then
    echo "✅ 성공: SSL 인증서 경로가 복구되어 HTTPS(443) 통신이 정상 동작합니다!"
    exit 0
else
    echo "❌ 실패: HTTPS(443 포트)에서 정상 응답(200 OK)을 받지 못했습니다."
    exit 1
fi
