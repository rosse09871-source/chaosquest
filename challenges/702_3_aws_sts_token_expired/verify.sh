#!/bin/bash
set -e
/usr/local/bin/run_terraform.sh || true
if ! grep -q "Terraform AWS API authentication successful" /var/log/terraform.log 2>/dev/null; then
    echo "❌ 실패: AWS STS 세션 토큰이 유효한 토큰(VALID_STS_SESSION_TOKEN_OK)으로 갱신되지 않았습니다."
    exit 1
fi
echo "✅ 성공: AWS STS 임시 토큰이 정상 갱신되었습니다!"
exit 0
