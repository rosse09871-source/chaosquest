#!/bin/bash
set -e
if ps -eo pid,args | grep -v "$$" | grep "[m]ail_flooder.py" >/dev/null 2>&1; then
    echo "❌ 실패: 메일 스풀을 생성 중인 mail_flooder.py 프로세스가 아직 실행 중입니다."
    exit 1
fi
COUNT=$(find /var/spool/mail/dead_letters -type f 2>/dev/null | wc -l)
if [ "$COUNT" -gt 50 ]; then
    echo "❌ 실패: /var/spool/mail/dead_letters 에 아직 $COUNT 개의 파일이 남아있습니다."
    exit 1
fi
echo "✅ 성공: 메일 스풀 데몬과 대량 파일이 완전히 정리되었습니다!"
exit 0
