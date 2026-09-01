#!/bin/bash
set -e
cat << 'SHEOF' > /usr/local/bin/run_app.sh
#!/bin/bash
if [ -f /etc/environment ]; then source /etc/environment; fi
if [ -z "$DB_HOST" ]; then
    echo "FATAL: Required environment variable DB_HOST is missing!"
    exit 1
fi
echo "Application successfully connected to DB: $DB_HOST (200 OK)" > /var/log/app_status.log
exit 0
SHEOF
chmod +x /usr/local/bin/run_app.sh
echo "502-1 Sabotage completed."
