#!/bin/bash
set -e
/usr/local/bin/check_aws_key.sh || true
if ! grep -q "AWS Key Format Valid" /var/log/aws_key.log 2>/dev/null; then
    echo "❌ 실패: AWS Access Key ID 형식이 올바르지 않습니다. (AKIA로 시작하는 20자리 대문자/숫자)"
    exit 1
fi
echo "✅ 성공: AWS 자격증명 키 형식이 올바르게 복구되었습니다!"
exit 0
