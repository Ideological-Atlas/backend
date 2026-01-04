import os

try:
    import django.template.backends.django  # noqa
except ImportError:
    pass

import django
from celery import Celery
from celery.signals import task_postrun
from django.conf import settings
from django.db import connections

from . import celery_config

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

django.setup()

app = Celery("backend", fixups=[])

app.config_from_object(celery_config)
CELERY_TIMEZONE = "Europe/Madrid"
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@task_postrun.connect
def close_db_connections(**kwargs):
    if app.conf.task_always_eager:
        return

    for conn in connections.all():
        conn.close_if_unusable_or_obsolete()
