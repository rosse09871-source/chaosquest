#!/bin/bash
set -e
/usr/local/bin/deploy_s3.sh || true
if ! grep -q "successfully uploaded to S3" /var/log/s3_deploy.log 2>/dev/null; then
    echo "❌ 실패: AWS 설정이 올바르지 않아 S3 배포 스크립트 실행이 실패했습니다."
    exit 1
fi
echo "✅ 성공: AWS 자격증명 및 서울 리전(ap-northeast-2) 설정이 정상 복구되었습니다!"
exit 0
