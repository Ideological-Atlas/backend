#! /bin/sh

set -e
set -u
set -x

# Wait for DB
dockerize -wait tcp://postgres:"${POSTGRES_INTERNAL_PORT}" -timeout 30s

exec celery -A backend.celery_backend flower \
    --basic_auth="${FLOWER_USER}:${FLOWER_PASSWORD}"
