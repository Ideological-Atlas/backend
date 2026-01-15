#!/bin/sh

set -e
set -u
set -x

# Wait for DB
dockerize -wait tcp://postgres:"${POSTGRES_INTERNAL_PORT}" -timeout 30s

# Wait for MinIO
dockerize -wait tcp://minio:9000 -timeout 30s

# Migrate models
python3 manage.py makemigrations --no-input
python3 manage.py migrate --no-input

# Load fixtures
python3 manage.py loaddata initial_ideology_data

# Populate Test Data (Only in Non-Prod)
if [ "$ENVIRONMENT" != "prod" ] && [ "$ENVIRONMENT" != "production" ]; then
    uv sync --extra dev
    python3 manage.py populate_test_data
fi

# Custom commands
python3 manage.py init_minio

# Collect static files
python3 manage.py collectstatic --no-input

# Create the superuser
python3 manage.py ensure_admin

# Start the server
exec gunicorn backend.asgi:application \
    --workers "${DJANGO_THREADS}" \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind "0.0.0.0:${BACKEND_PORT}" \
    --timeout "${CONF_GUNICORN_TIMEOUT}" \
    "${CONF_GUNICORN_EXTRA_ARGS}"
