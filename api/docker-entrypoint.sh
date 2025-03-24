#!/bin/sh

set -e

while ! alembic upgrade heads;
do
    echo "Retrying in 5 seconds..."
    sleep 5
done

exec uvicorn app.main:app --host 0.0.0.0 --port 80 --forwarded-allow-ips '*'