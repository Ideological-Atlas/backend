#!/bin/sh

set -e
set -u
set -x

# Wait for DB
dockerize -wait tcp://postgres:"${POSTGRES_INTERNAL_PORT}" -timeout 30s

if [ "$ENVIRONMENT" != "prod" ] && [ "$ENVIRONMENT" != "production" ]; then
    echo "Environment is $ENVIRONMENT - Waiting for MinIO..."
    dockerize -wait tcp://minio:9000 -timeout 30s
fi

# Migrate models
python3 manage.py makemigrations --no-input
python3 manage.py migrate --no-input

# Load fixtures
python3 manage.py loaddata ideologies ideology_abstraction_complexities ideology_axes ideology_conditioners ideology_axis_definitions

# Populate Test Data & Init MinIO (Only in Non-Prod)
if [ "$ENVIRONMENT" != "prod" ] && [ "$ENVIRONMENT" != "production" ]; then
    uv sync --extra dev
    python3 manage.py populate_test_data
    python3 manage.py init_minio
fi

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
