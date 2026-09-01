#!/bin/bash
set -e
if ! grep -Eq "PubkeyAuthentication (yes|true)" /etc/ssh/sshd_config 2>/dev/null; then
    echo "❌ 실패: /etc/ssh/sshd_config 에 PubkeyAuthentication yes 설정이 활성화되지 않았습니다."
    exit 1
fi
echo "✅ 성공: SSH 공개키 인증 설정이 정상 복구되었습니다!"
exit 0
