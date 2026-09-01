#!/bin/bash
set -e
mkdir -p /root/.aws
cat << 'AWSEOF' > /root/.aws/credentials
[defualt_typo]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWSEOF

cat << 'AWSEOF' > /root/.aws/config
[profile defualt_typo]
region = us-east-1
output = json
AWSEOF

cat << 'SHEOF' > /usr/local/bin/deploy_s3.sh
#!/bin/bash
if ! grep -q "^\[default\]" /root/.aws/credentials 2>/dev/null; then
    echo "ERROR: AWS profile [default] not found in credentials!"
    exit 1
fi
if ! grep -q "region = ap-northeast-2" /root/.aws/config 2>/dev/null; then
    echo "ERROR: AWS region must be configured as ap-northeast-2 in config!"
    exit 1
fi
echo "Artifact successfully uploaded to S3 in ap-northeast-2 (Seoul)!" > /var/log/s3_deploy.log
exit 0
SHEOF
chmod +x /usr/local/bin/deploy_s3.sh
echo "702-1 Sabotage completed."
