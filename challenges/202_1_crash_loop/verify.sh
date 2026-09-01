#!/bin/bash
set -e
if ! ps -eo pid,args | grep -v "$$" | grep "[p]ayment_service.py" >/dev/null 2>&1; then
    echo "❌ 실패: payment_service.py 프로세스가 실행 중이지 않습니다."
    exit 1
fi
if ! grep -q "successfully started" /var/log/payment_service.log 2>/dev/null; then
    echo "❌ 실패: 서비스 정상 시작 로그가 확인되지 않았습니다."
    exit 1
fi
echo "✅ 성공: 결제 데몬 서비스가 정상 기동 중입니다!"
exit 0
