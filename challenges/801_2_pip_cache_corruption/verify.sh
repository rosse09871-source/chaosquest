#!/bin/bash
set -e

if [ -f /root/.cache/pip/wheels/corrupted_lib-1.0.0-py3-none-any.whl ]; then
  echo "손상된 휠 파일(/root/.cache/pip/wheels/corrupted_lib-...)이 여전히 남아있습니다."
  exit 1
fi

echo "빌드 러너 패키지 캐시가 깨끗하게 정리되었습니다."
exit 0
