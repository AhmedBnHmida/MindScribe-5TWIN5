#!/usr/bin/env bash
set -e

# Default environment fallbacks
: "${PORT:=8000}"
: "${WORKERS:=3}"
: "${TIMEOUT:=120}"

echo "Deleting old migrations (if any)..."
Get-ChildItem -Path . -Filter "0*.py" -Recurse | Where-Object { $_.DirectoryName -like "*migrations*" } | Remove-Item -Force

echo "Applying database migrations (if any)..."
python manage.py makemigrations
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn on port ${PORT}..."
exec gunicorn mindscribe.wsgi:application \
    --bind 0.0.0.0:"${PORT}" \
    --workers "${WORKERS}" \
    --timeout "${TIMEOUT}"


