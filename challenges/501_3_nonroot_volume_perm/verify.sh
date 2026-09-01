#!/bin/bash
set -e
if ! su -s /bin/sh nodeuser -c "touch /data/app_storage/test_node.tmp" >/dev/null 2>&1; then
    echo "❌ 실패: UID 1000(nodeuser) 유저가 /data/app_storage 에 파일을 쓸 수 없습니다."
    exit 1
fi
rm -f /data/app_storage/test_node.tmp
echo "✅ 성공: 비루트 컨테이너 볼륨 쓰기 권한이 정상 복구되었습니다!"
exit 0
