#!/bin/sh
set -eu

python manage.py migrate --noinput
python manage.py collectstatic --noinput
if [ -n "${DEVHANDOVER_DEMO_PASSWORD:-}" ]; then
    python manage.py seed_demo
fi
exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-10000}" --access-logfile -
