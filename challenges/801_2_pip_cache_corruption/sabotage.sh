#!/bin/bash
set -e
mkdir -p /root/.cache/pip/wheels
touch /root/.cache/pip/wheels/corrupted_lib-1.0.0-py3-none-any.whl
echo "801-2 Sabotage completed."
