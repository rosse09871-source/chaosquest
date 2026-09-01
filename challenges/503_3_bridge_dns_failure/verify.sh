#!/bin/bash
set -e

if ! grep -q "backend.internal.service" /etc/hosts; then
  echo "/etc/hosts에 backend.internal.service 매핑이 여전히 누락되어 있습니다."
  exit 1
fi

if ! grep -q "172.20.0.10" /etc/hosts; then
  echo "/etc/hosts의 backend.internal.service IP 주소가 172.20.0.10으로 설정되지 않았습니다."
  exit 1
fi

echo "도커 브리지 내부 DNS 매핑이 정상 복구되었습니다."
exit 0
