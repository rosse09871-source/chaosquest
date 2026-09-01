#!/bin/bash
set -e
PERM=$(stat -c "%a" /root/.ssh/id_rsa 2>/dev/null || stat -f "%Lp" /root/.ssh/id_rsa 2>/dev/null || echo "644")
if [ "$PERM" != "400" ] && [ "$PERM" != "600" ]; then
    echo "❌ 실패: /root/.ssh/id_rsa 권한($PERM)이 안전하지 않습니다. (chmod 400 또는 600 필요)"
    exit 1
fi
echo "✅ 성공: SSH 개인키 권한이 안전하게 보호되었습니다!"
exit 0
