#!/bin/bash
set -e
P_DIR=$(stat -c "%a" /root/.ssh 2>/dev/null || stat -f "%Lp" /root/.ssh 2>/dev/null || echo "777")
P_FILE=$(stat -c "%a" /root/.ssh/authorized_keys 2>/dev/null || stat -f "%Lp" /root/.ssh/authorized_keys 2>/dev/null || echo "666")

if [ "$P_DIR" != "700" ] && [ "$P_DIR" != "0700" ]; then
    echo "❌ 실패: /root/.ssh 디렉터리 권한($P_DIR)이 안전하지 않습니다. (chmod 700 필요)"
    exit 1
fi
if [ "$P_FILE" != "600" ] && [ "$P_FILE" != "0600" ] && [ "$P_FILE" != "400" ]; then
    echo "❌ 실패: /root/.ssh/authorized_keys 파일 권한($P_FILE)이 안전하지 않습니다. (chmod 600 필요)"
    exit 1
fi
echo "✅ 성공: SSH 공개키 저장소 권한이 안전하게 복구되었습니다!"
exit 0
