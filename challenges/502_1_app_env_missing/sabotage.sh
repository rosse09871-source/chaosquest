#!/bin/bash
set -e
cat << 'SHEOF' > /usr/local/bin/entrypoint.sh
#!/bin/bash
if [ -f /etc/environment ]; then source /etc/environment; fi
if [ "$APP_ENV" != "production" ] && [ "$APP_ENV" != "staging" ]; then
    echo "ERROR: APP_ENV must be set to production or staging!"
    exit 1
fi
echo "Container Entrypoint OK: APP_ENV=$APP_ENV" > /var/log/entrypoint.log
exit 0
SHEOF
chmod +x /usr/local/bin/entrypoint.sh
echo "502-1 Sabotage completed."
