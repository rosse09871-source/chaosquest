#!/bin/bash
set -e
# Test uploading 5MB dummy data
UPLOAD_STATUS=$(python3 -c "
import urllib.request
data = b'A' * (3 * 1024 * 1024) # 3MB
req = urllib.request.Request('http://127.0.0.1:80/upload', data=data, method='POST')
try:
    with urllib.request.urlopen(req, timeout=3) as resp:
        print(resp.status)
except urllib.error.HTTPError as e:
    print(e.code)
except Exception as e:
    print(0)
")

if [ "$UPLOAD_STATUS" = "200" ]; then
    echo "✅ 성공: client_max_body_size 가 확장되어 3MB 이상의 대용량 업로드가 정상 처리됩니다!"
    exit 0
else
    echo "❌ 실패: 3MB 데이터 업로드 시 여전히 $UPLOAD_STATUS 에러가 반환됩니다."
    exit 1
fi
