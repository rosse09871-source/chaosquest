#!/bin/bash
set -e
mkdir -p /root/.aws
cat << 'AWSEOF' > /root/.aws/credentials
[default]
aws_access_key_id = ASIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
aws_session_token = EXPIRED_TOKEN_DEAD_BEEF
AWSEOF

cat << 'SHEOF' > /usr/local/bin/run_terraform.sh
#!/bin/bash
TOKEN=$(grep "aws_session_token" /root/.aws/credentials | awk '{print $3}')
if [ "$TOKEN" = "VALID_STS_SESSION_TOKEN_OK" ]; then
    echo "Terraform AWS API authentication successful!" > /var/log/terraform.log
    exit 0
else
    echo "ExpiredToken: The security token is expired!"
    exit 1
fi
SHEOF
chmod +x /usr/local/bin/run_terraform.sh
echo "702-3 Sabotage completed."
