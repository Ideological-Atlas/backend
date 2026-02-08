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
#python3 manage.py loaddata 01_complexities 02_sections 03_axes 04_conditioners 05_ideologies 06_axis_definitions 07_conditioner_definitions 08_geography 09_religions 10_tags 11_associations

# Populate Test Data & Init MinIO (Only in Non-Prod)
if [ "$ENVIRONMENT" != "prod" ] && [ "$ENVIRONMENT" != "production" ]; then
    uv sync --extra dev
    python3 manage.py populate_test_data
    python3 manage.py init_minio
fi

# Load flags
python3 manage.py import_flags

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
