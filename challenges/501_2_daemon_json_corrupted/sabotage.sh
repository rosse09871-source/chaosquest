#!/bin/bash
set -e
mkdir -p /etc/docker
cat << 'JSONEOF' > /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m"
  # Missing closing brace
}
JSONEOF

cat << 'SHEOF' > /usr/local/bin/check_dockerd.sh
#!/bin/bash
python3 -c "
import json, sys
try:
    with open('/etc/docker/daemon.json') as f:
        json.load(f)
    print('DOCKERD_CONFIG_VALID')
except Exception as e:
    print('DOCKERD_CONFIG_INVALID:', e)
    sys.exit(1)
"
SHEOF
chmod +x /usr/local/bin/check_dockerd.sh
echo "501-2 Sabotage completed."
