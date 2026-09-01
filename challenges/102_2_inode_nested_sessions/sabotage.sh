#!/bin/bash
set -e
mkdir -p /var/cache/.session_dumps
python3 -c "
import os
for i in range(15000):
    with open(f'/var/cache/.session_dumps/sess_{i}.tmp', 'w') as f: f.write('0')
"
echo "102-2 Sabotage completed."
