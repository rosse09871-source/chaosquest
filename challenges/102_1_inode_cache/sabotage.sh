#!/bin/bash
set -e
mkdir -p /tmp/junk_cache
python3 -c "
import os
for i in range(8000):
    with open(f'/tmp/junk_cache/junk_{i}.tmp', 'w') as f: f.write('0')
"
echo "102-1 Sabotage completed."
