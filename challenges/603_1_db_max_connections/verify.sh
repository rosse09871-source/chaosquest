#!/bin/bash
set -e

if [ ! -f /etc/mysql_mock/my.cnf ]; then
  echo "/etc/mysql_mock/my.cnf 설정 파일이 누락되었습니다."
  exit 1
fi

VAL=$(grep "max_connections" /etc/mysql_mock/my.cnf | awk -F'=' '{print $2}' | tr -d ' ')
if [ -z "$VAL" ] || [ "$VAL" -lt 100 ]; then
  echo "max_connections 값이 여전히 너무 작습니다 (현재: ${VAL:-없음}). 100 이상으로 상향 조정하세요."
  exit 1
fi

echo "DB 최대 커넥션 한도 설정이 정상적으로 증설되었습니다."
exit 0
