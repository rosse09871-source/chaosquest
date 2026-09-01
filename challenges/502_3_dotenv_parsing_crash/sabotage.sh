#!/bin/bash
set -e
mkdir -p /app
cat << 'ENVEOF' > /app/.env
DB_PORT=5432
API_SECRET_KEY="secret_key_missing_closing_quote
ENABLE_METRICS=true
ENVEOF

cat << 'SHEOF' > /usr/local/bin/start_app_env.sh
#!/bin/bash
python3 -c "
import sys
with open('/app/.env') as f:
    for line in f:
        line = line.strip()
        if line and '=' in line:
            k, v = line.split('=', 1)
            if v.startswith('\"') and not v.endswith('\"'):
                print('CRITICAL DOTENV PARSE ERROR on key:', k)
                sys.exit(1)
print('DOTENV_PARSED_SUCCESS')
"
SHEOF
chmod +x /usr/local/bin/start_app_env.sh
echo "502-3 Sabotage completed."
