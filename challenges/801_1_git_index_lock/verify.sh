#!/bin/bash
set -e

if [ -f /opt/deploy_repo/.git/index.lock ]; then
  echo "/opt/deploy_repo/.git/index.lock 파일이 여전히 존재합니다."
  exit 1
fi

echo "Git 배포 락 파일이 성공적으로 정리되었습니다."
exit 0
