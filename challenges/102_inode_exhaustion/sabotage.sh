#!/bin/bash
set -e

apt-get update -qq >/dev/null 2>&1 || true
apt-get install -y -qq procps >/dev/null 2>&1 || true

DUMP_DIR="/var/cache/.session_dumps"
mkdir -p "$DUMP_DIR"

# Generate 15,000 dummy small files
python3 -c "
import os
dump_dir = '$DUMP_DIR'
for i in range(15000):
    with open(os.path.join(dump_dir, f'sess_{i}.tmp'), 'w') as f:
        f.write('0')
"

echo "Stage 102 Sabotage completed. Created 15,000 files in $DUMP_DIR."
