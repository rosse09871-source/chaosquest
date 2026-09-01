#!/bin/bash
set -e

# 1. Check if payment_service.py is running
if ! ps -eo pid,args | grep -v "$$" | grep "[p]ayment_service.py" >/dev/null 2>&1; then
    echo "❌ 실패: payment_service.py 프로세스가 실행 중이지 않습니다."
    echo "👉 팁: /var/log/payment_service.log 를 확인하여 /etc/chaos_app.conf 를 수정한 후 /usr/local/bin/start_payment_service.sh 를 실행하세요."
    exit 1
fi

# 2. Check if the log contains success message
if ! grep -q "successfully started" /var/log/payment_service.log 2>/dev/null; then
    echo "❌ 실패: 서비스가 정상 시작 로그를 기록하지 못했습니다."
    exit 1
fi

echo "✅ 성공: 설정 파일 오타가 수정되었고 결제 데몬 서비스가 정상 기동 중입니다!"
exit 0
