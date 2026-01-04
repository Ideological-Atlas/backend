#! /bin/sh

set -e
set -u
set -x

# Wait for DB
dockerize -wait tcp://postgres:"${POSTGRES_INTERNAL_PORT}" -timeout 30s

exec celery -A backend.celery_backend beat \
    --loglevel="${CELERY_LOG_LEVEL}" \
    --logfile="/src/logs/${WORKER_NAME}.log"
