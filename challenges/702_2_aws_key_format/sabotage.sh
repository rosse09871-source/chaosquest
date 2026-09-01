#!/bin/bash
set -e
mkdir -p /root/.aws
cat << 'AWSEOF' > /root/.aws/credentials
[default]
aws_access_key_id = AKIA_INVALID_TYPO_KEY_123
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWSEOF

cat << 'SHEOF' > /usr/local/bin/check_aws_key.sh
#!/bin/bash
KEY=$(grep "aws_access_key_id" /root/.aws/credentials | awk '{print $3}')
if [[ "$KEY" =~ ^AKIA[0-9A-Z]{16}$ ]]; then
    echo "AWS Key Format Valid: $KEY" > /var/log/aws_key.log
    exit 0
else
    echo "ERROR: Invalid AWS Access Key ID format: $KEY"
    exit 1
fi
SHEOF
chmod +x /usr/local/bin/check_aws_key.sh
echo "702-2 Sabotage completed."
