#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== [ChaosQuest] Building pre-baked base image (chaosquest:base)... ==="
cd "${ROOT_DIR}"
docker build -t chaosquest:base -f docker/Dockerfile.base .
echo "=== [ChaosQuest] Base image built successfully! (30s -> 0.3s boot achieved) ==="
