#!/bin/bash
set -e
PERM=$(stat -c "%a" /etc/sudoers 2>/dev/null || stat -f "%Lp" /etc/sudoers 2>/dev/null || echo "777")
if [ "$PERM" != "440" ] && [ "$PERM" != "0440" ]; then
    echo "❌ 실패: /etc/sudoers 권한($PERM)이 안전하지 않습니다. (chmod 440 필요)"
    exit 1
fi
echo "✅ 성공: /etc/sudoers 권한이 표준 0440으로 안전하게 복구되었습니다!"
exit 0
