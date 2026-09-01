#!/bin/bash
set -e

if [ ! -f /etc/ld.so.conf.d/app.conf ] || ! grep -q "/opt/lib" /etc/ld.so.conf.d/app.conf; then
  echo "/etc/ld.so.conf.d/app.conf 파일에 '/opt/lib' 경로가 등록되지 않았습니다."
  exit 1
fi

echo "공유 라이브러리 링커 경로가 성공적으로 구성되었습니다."
exit 0
